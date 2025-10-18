import os
import re
import chromadb
from agents import (
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
    Runner,
    trace
)
from openai.types.responses import ResponseTextDeltaEvent
from openai import AsyncAzureOpenAI, AsyncOpenAI, OpenAIError
from typing import Any, AsyncGenerator
import pandas as pd

# Import base utilities (avoid circular imports by importing agents only in initialize_system)
from utils.csv_loader import CSVloader
from utils.prepare_customer_data import PrepareCustomerData
from db.vectorstore_chroma import ChromaVectorStore
from test.test_questions import TestQuestions
from utils.synthetic_data_generator import AdvancedSyntheticFeedbackGenerator
from datetime import datetime


def is_azure_openai() -> bool:
    """
    Checks if Azure OpenAI is configured based on environment variables.

    Returns:
        bool: True if all required Azure OpenAI environment variables are set:
             - AZURE_OPENAI_API_KEY
             - AZURE_OPENAI_ENDPOINT  
             - AZURE_OPENAI_API_VERSION
             
    Notes:
        - Used to determine which OpenAI client to instantiate
        - Falls back to standard OpenAI if any variable is missing
    """
    return bool(
        os.environ.get("AZURE_OPENAI_API_KEY") and 
        os.environ.get("AZURE_OPENAI_ENDPOINT") and 
        os.environ.get("AZURE_OPENAI_API_VERSION")
    )


def check_vectorstore_exists(
    vectorstore_path: str = "./chroma",
    collection_name: str = "feedback_data"
) -> tuple[bool, int]:
    """
    Checks if VectorStore exists and returns document count.
    
    Args:
        vectorstore_path (str): Path to VectorStore directory. Defaults to "./chroma"
        collection_name (str): Name of the ChromaDB collection. Defaults to "feedback_data"
    
    Returns:
        tuple[bool, int]: (exists, document_count) where:
            - exists (bool): True if VectorStore exists, False otherwise
            - document_count (int): Number of documents in VectorStore (0 if doesn't exist)
            
    Notes:
        - ChromaDB client must point to feedback_vectorstore subdirectory
        - Collections are located in ./chroma/feedback_vectorstore, not ./chroma
        - Returns (False, 0) on any errors during checking
    """
    try:
        # Check if directory exists
        vectorstore_full_path = os.path.join(vectorstore_path, "feedback_vectorstore")
        if not os.path.exists(vectorstore_full_path):
            return (False, 0)
        
        # ChromaDB client must point to feedback_vectorstore path
        # Collections are located in ./chroma/feedback_vectorstore, not ./chroma
        client = chromadb.PersistentClient(path=vectorstore_full_path)
        collections = client.list_collections()
        
        for collection in collections:
            if collection.name == collection_name:
                # Collection exists - retrieve document count
                try:
                    coll = client.get_collection(name=collection_name)
                    doc_count = coll.count()
                    return (True, doc_count)
                except Exception:
                    return (False, 0)
        
        # Collection not found
        return (False, 0)
        
    except Exception as e:
        print(f"⚠️ Error checking VectorStore: {e}")
        return (False, 0)


def get_model_name(model_type: str = "gpt4o") -> str:
    """
    Returns the correct model name based on Azure/OpenAI configuration.
    
    Args:
        model_type (str): Model type identifier:
                         - "gpt4o" for GPT-4 Omni
                         - "gpt4o_mini" for GPT-4 Omni Mini
                         Defaults to "gpt4o"
    
    Returns:
        str: Correct model name for Azure OpenAI deployment or standard OpenAI API
        
    Notes:
        - Azure OpenAI: Returns deployment names ("gpt-4o", "gpt-4o-mini")
        - Standard OpenAI: Returns API model names (same format)
        - Falls back to "gpt-4o-mini" for unknown model types
        - Uses is_azure_openai() to determine environment
    """
    if is_azure_openai():
        # Azure OpenAI Deployment-Namen (wie sie aktuell verwendet werden)
        if model_type == "gpt4o":
            return "gpt-4o"  # Azure Deployment Name
        elif model_type == "gpt4o_mini":
            return "gpt-4o-mini"  # Azure Deployment Name
        else:
            return "gpt-4o-mini"  # Fallback
    else:
        # Standard OpenAI API Modellnamen
        if model_type == "gpt4o":
            return "gpt-4o"  # Standard OpenAI Name
        elif model_type == "gpt4o_mini":
            return "gpt-4o-mini"  # Standard OpenAI Name
        else:
            return "gpt-4o-mini"  # Fallback


def load_csv(
    path: str = "./data/feedback_data.csv", 
    is_synthetic: bool = False,
    n_synthetic_samples: int=10000,
    synthetic_start_date: str='2023-01-01',
    synthetic_end_date: str=datetime.now().strftime('%Y-%m-%d'),
) -> pd.DataFrame:
    """
    Loads CSV file with optional enhancement.
    
    Two modes:
    1. is_synthetic=True: Loads synthetic data (already enhanced)
       - No PrepareCustomerData needed (saves ~50 seconds)
       - Uses pandas directly (fast)
       - Automatically generates new data if file doesn't exist
       
    2. is_synthetic=False: Loads original data (requires enhancement)
       - Full enhancement pipeline
       - NPS categorization, sentiment analysis, topic classification
       - Automatically saves enhanced CSV locally
    
    Args:
        path (str): Path to CSV file. Defaults to "./data/feedback_data.csv"
        is_synthetic (bool): True = synthetic data (no enhancement needed). Defaults to False
        n_synthetic_samples (int): Number of synthetic records (only if is_synthetic=True). Defaults to 10000
        synthetic_start_date (str): Start date for synthetic data (format: 'YYYY-MM-DD'). Defaults to '2023-01-01'
        synthetic_end_date (str): End date for synthetic data (format: 'YYYY-MM-DD'). Defaults to today
    
    Returns:
        pd.DataFrame: Enhanced or ready-to-use DataFrame with all required columns
        
    Notes:
        - Synthetic mode skips PrepareCustomerData (~50s time saving)
        - Original mode runs full NPS/sentiment/topic pipeline
        - Automatically generates synthetic data if file missing
        - Enhanced CSV is saved for future use
    """
    # Synthetische Daten laden
    if is_synthetic:
        if not os.path.exists(path):
            print(f"🤖 Generiere synthetische Daten...")
            generator = AdvancedSyntheticFeedbackGenerator(seed=42, enable_fun_mode=True)
            
            df_synthetic = generator.generate_enterprise_dataset(
                n_samples=n_synthetic_samples,
                start_date=synthetic_start_date,
                end_date=synthetic_end_date,
                ensure_diversity=True,
                include_metadata=True
            )
            
            # Speichere generierte Daten
            df_synthetic.to_csv(path, index=False, encoding='utf-8-sig')
            print(f"✅ {len(df_synthetic):,} synthetische Datensätze generiert und gespeichert: {path}")
            
            return df_synthetic
        
        # Synthetische Daten existieren → Laden mit Pandas
        df = pd.read_csv(path, encoding='utf-8-sig')
        print(f"✅ Synthetische Daten geladen (ohne Enhancement): {df.shape[0]} Einträge, Pfad: {path}")
        return df
    
    # Originale Daten laden
    csv_loader = CSVloader(path=path, encoding="utf-8")
    df = csv_loader.load_csv()

    # Prepare DataFrame with all enhancement features
    customer_data = PrepareCustomerData(
        data=df,
        nps_category_col_name="NPS",
        feedback_col_name="Verbatim",
        market_col_name="Market",
        feedback_token_model=get_model_name("gpt4o_mini")
    )

    df = customer_data.data

    # Write enhanced CSV locally (always)
    write_prepared_csv(df)

    print(f"✅ Original-Daten enhanced: {df.shape[0]} Einträge, Pfad: {path}")

    return df


def write_prepared_csv(
    data: pd.DataFrame, path: str = "./data/feedback_data_enhanced.csv"
) -> None:
    """
    Saves enhanced DataFrame as CSV file.
    
    Args:
        data (pd.DataFrame): Enhanced DataFrame to be saved
        path (str): Target path for CSV file. Defaults to "./data/feedback_data_enhanced.csv"
    
    Returns:
        None
    """
    data.to_csv(path, index=False, encoding="utf-8", mode="w")
    print(f"Enhanced CSV written to {path}")


def load_vectorstore(
    data: pd.DataFrame, 
    type: str = "chroma", 
    create_new_store: bool = False,
    embedding_model: str = "text-embedding-ada-002"
) -> Any | None:
    """
    Loads or creates a VectorStore.
    
    Args:
        data (pd.DataFrame): DataFrame containing customer feedback data
        type (str): VectorStore type (currently only "chroma" is supported). Defaults to "chroma"
        create_new_store (bool): If True, creates new VectorStore; if False, loads existing one. Defaults to False
        embedding_model (str): OpenAI embedding model. Defaults to "text-embedding-ada-002"
            - "text-embedding-ada-002": Best cross-lingual performance (78.4% avg similarity)
            - "text-embedding-3-small": Cheaper but worse cross-lingual performance (29.4%)
            - "text-embedding-3-large": More expensive but also poor cross-lingual performance (32.2%)
    
    Returns:
        Any | None: ChromaDB Collection object if successful, None on error
    """
    if type == "chroma":
        vectorstore_manager = ChromaVectorStore(
            data=data,
            file_path="./chroma",
            file_name="feedback_vectorstore",
            collection_name="feedback_data",
            batch_size=100,
            embedding_model=embedding_model,  # ✅ Übergebenes Modell verwenden
        )

        chroma_collection = vectorstore_manager.create_vectorstore(
            force_recreate=create_new_store
        )
        
        # Info-Ausgabe (inline statt separater Funktion)
        if chroma_collection:
            print(f"VectorStore loaded with {chroma_collection.count()} documents")

        # Check if collection was successfully created/loaded
        if chroma_collection is None:
            print("❌ ERROR: VectorStore could not be created/loaded!")
            return None
        
        return chroma_collection
    
    print(f"❌ ERROR: Unknown VectorStore type '{type}'. Must be 'chroma' for now.")
    return None


def get_azure_openai_client() -> AsyncAzureOpenAI | None:
    """
    Initializes Azure OpenAI client and sets it as default for agents.
    
    Required environment variables:
        - AZURE_OPENAI_API_KEY
        - AZURE_OPENAI_ENDPOINT
        - AZURE_OPENAI_API_VERSION
    
    Returns:
        AsyncAzureOpenAI | None: Initialized Azure OpenAI client or None on error
    
    Raises:
        ValueError: If required environment variables are not set
    """
    if not os.environ.get("AZURE_OPENAI_API_KEY", ""):
        raise ValueError("AZURE_OPENAI_API_KEY environment variable not set")
    if not os.environ.get("AZURE_OPENAI_ENDPOINT", ""):
        raise ValueError("AZURE_OPENAI_ENDPOINT environment variable not set")
    if not os.environ.get("AZURE_OPENAI_API_VERSION", ""):
        raise ValueError("AZURE_OPENAI_API_VERSION environment variable not set")

    try:
        azure_client = AsyncAzureOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", ""),
        )

        set_default_openai_client(azure_client)
        set_default_openai_api("chat_completions")
        set_tracing_disabled(True)

        print("✅ Azure OpenAI Client initialized")

        return azure_client
    except OpenAIError as e:
        print(f"OpenAI API Error: {str(e)}")
        print("❌ ERROR: Azure OpenAI Client could not be initialized!")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        print("❌ ERROR: Azure OpenAI Client could not be initialized!")
    return None


def get_openai_client() -> AsyncOpenAI | None:
    """
    Initializes standard OpenAI client.
    
    Required environment variables:
        - OPENAI_API_KEY
    
    Returns:
        AsyncOpenAI | None: Initialized OpenAI client or None on error
    
    Raises:
        ValueError: If OPENAI_API_KEY environment variable is not set
    """
    # Check required environment variables
    if not os.environ.get("OPENAI_API_KEY", ""):
        raise ValueError("OPENAI_API_KEY environment variable not set")

    try:
        openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
        print("✅ OpenAI Client initialized")
        return openai_client
    except OpenAIError as e:
        print(f"OpenAI API Error: {str(e)}")
        print("❌ ERROR: OpenAI Client could not be initialized!")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        print("❌ ERROR: OpenAI Client could not be initialized!")
    return None


def get_test_questions(
    test_meta: bool = True,
    test_feedback: bool = True,
    test_validation: bool = True,
    test_sentiment: bool = True,
    test_parameters: bool = True,
    test_complex: bool = True,
    test_edge: bool = False,
    questions_per_category: int = 2,
) -> list[str]:
    """
    Generates test questions based on provided flags.

    Args:
        test_meta (bool): Include meta questions (dataset information). Defaults to True
        test_feedback (bool): Include feedback analysis questions. Defaults to True
        test_validation (bool): Include market validation questions. Defaults to True
        test_sentiment (bool): Include sentiment analysis questions. Defaults to True
        test_parameters (bool): Include user parameter extraction questions. Defaults to True
        test_complex (bool): Include complex multi-criteria queries. Defaults to True
        test_edge (bool): Include edge cases (disabled by default). Defaults to False
        questions_per_category (int): Number of questions per enabled category. Defaults to 2

    Returns:
        list[str]: List of generated test questions
    """
    test_queries = []

    if test_meta:
        questions = TestQuestions.get_questions_by_category("META_QUESTIONS")
        if questions_per_category > 0 and questions_per_category <= len(questions):
            test_queries.extend(questions[:questions_per_category])
        else:
            test_queries.extend(questions)

    if test_feedback:
        questions = TestQuestions.get_questions_by_category(
            "FEEDBACK_ANALYSIS_QUESTIONS"
        )
        if questions_per_category > 0 and questions_per_category <= len(questions):
            test_queries.extend(questions[:questions_per_category])
        else:
            test_queries.extend(questions)

    if test_validation:
        questions = TestQuestions.get_questions_by_category(
            "MARKET_VALIDATION_QUESTIONS"
        )
        if questions_per_category > 0 and questions_per_category <= len(questions):
            test_queries.extend(questions[:questions_per_category])
        else:
            test_queries.extend(questions)

    if test_sentiment:
        questions = TestQuestions.get_questions_by_category("SENTIMENT_QUESTIONS")
        if questions_per_category > 0 and questions_per_category <= len(questions):
            test_queries.extend(questions[:questions_per_category])
        else:
            test_queries.extend(questions)

    if test_parameters:
        questions = TestQuestions.get_questions_by_category("USER_PARAMETER_QUESTIONS")
        if questions_per_category > 0 and questions_per_category <= len(questions):
            test_queries.extend(questions[:questions_per_category])
        else:
            test_queries.extend(questions)

    if test_complex:
        questions = TestQuestions.get_questions_by_category("COMPLEX_QUESTIONS")
        if questions_per_category > 0 and questions_per_category <= len(questions):
            test_queries.extend(questions[:questions_per_category])
        else:
            test_queries.extend(questions)

    if test_edge:
        questions = TestQuestions.get_questions_by_category("EDGE_CASES")
        if questions_per_category > 0 and questions_per_category <= len(questions):
            test_queries.extend(questions[:questions_per_category])
        else:
            test_queries.extend(questions)

    return test_queries


# ============================================================================
# VERSCHOBEN AUS streamlit_app.py - BUSINESS LOGIC & UTILITIES
# ============================================================================

def extract_chart_path(text: str) -> tuple[str, str | None]:
    """
    Extrahiert Chart-Pfad aus Response-Text (Format: __CHART__[pfad]__CHART__).
    
    Args:
        text: Text der möglicherweise Chart-Marker enthält
    
    Returns:
        tuple: (text_without_chart_marker, chart_path or None)
            - text_without_chart_marker: Bereinigter Text ohne Marker
            - chart_path: Pfad zum Chart oder None
    
    Beispiel:
        >>> text = "Analysis complete __CHART__./charts/plot.png__CHART__"
        >>> clean_text, path = extract_chart_path(text)
        >>> print(clean_text)  # "Analysis complete"
        >>> print(path)  # "./charts/plot.png"
    """
    pattern = r'__CHART__(.*?)__CHART__'
    match = re.search(pattern, text)
    
    if match:
        chart_path = match.group(1).strip()
        text_without_marker = re.sub(pattern, '', text).strip()
        return text_without_marker, chart_path
    
    return text, None


def limit_session_history(session, max_history: int | None = None):
    """
    Limits session history to the last N entries.
    IMPORTANT: Removes __CHART__ markers from history for agent context!
    
    Args:
        session (Any): SQLiteSession object containing conversation history
        max_history (int | None): Maximum number of history entries (None = unlimited). Defaults to None
    
    Returns:
        Any: Session with limited history and cleaned responses
    
    Notes:
        - Chart markers are removed to optimize token consumption
        - Charts are only relevant for UI, not for agent context
        - Returns original session on error (robustness)
    """
    try:
        # Get current history
        history = session.get_history()
        
        if not history:
            return session
        
        # Clean chart markers for token optimization
        # Charts are only relevant for UI, not for agent context
        cleaned_history = []
        for entry in history:
            # Create copy of entry
            cleaned_entry = entry.copy()
            
            # Clean response from chart markers
            if "content" in cleaned_entry:
                content = cleaned_entry["content"]
                if isinstance(content, list):
                    # Handle multi-part content
                    cleaned_content = []
                    for part in content:
                        if isinstance(part, dict) and "text" in part:
                            # Remove __CHART__path__CHART__ pattern
                            cleaned_text = re.sub(r'__CHART__[^_]+__CHART__', '', part["text"])
                            part["text"] = cleaned_text.strip()
                        cleaned_content.append(part)
                    cleaned_entry["content"] = cleaned_content
                elif isinstance(content, str):
                    # Handle simple string content
                    cleaned_entry["content"] = re.sub(r'__CHART__[^_]+__CHART__', '', content).strip()
            
            cleaned_history.append(cleaned_entry)
        
        # Limit history if necessary
        if max_history and len(cleaned_history) > max_history:
            cleaned_history = cleaned_history[-max_history:]
        
        # Set cleaned history back
        session.set_history(cleaned_history)
            
    except (AttributeError, Exception) as e:
        # If session has no history methods or error occurs,
        # return original (fallback for robustness)
        pass
    
    return session


async def process_query(customer_manager, user_input: str, session=None, history_limit: int | None = None):
    """
    Processes user query with multi-agent system.
    
    Args:
        customer_manager (Any): Customer Manager Agent instance
        user_input (str): User input query
        session (Any | None): SQLiteSession for context management (optional). Defaults to None
        history_limit (int | None): Maximum number of history entries (optional). Defaults to None
    
    Returns:
        Any | dict: Result object with agent.final_output attribute or error dictionary
            Error format: {"error": str, "error_type": str}
    
    Notes:
        - Automatic history limitation for token optimization
        - Tracing with session_id for debugging
        - Robust error handling
    """
    try:
        if session:
            # Limit history for token optimization
            if history_limit is not None:
                session = limit_session_history(session, history_limit)

            with trace(
                "Customer Feedback Multi-Agent Analysis",
                group_id=f"session_{session.session_id}",
            ):
                result = await Runner.run(customer_manager, user_input, session=session)
        else:
            # Fallback without session
            result = await Runner.run(customer_manager, user_input)

        return result

    except Exception as e:
        # Return error info for display
        return {"error": str(e), "error_type": type(e).__name__}


async def process_query_streamed(
    customer_manager, 
    user_input: str, 
    session=None, 
    history_limit: int | None = None
) -> AsyncGenerator[str | dict, None]:
    """
    Processes user query with REAL token streaming.
    
    Args:
        customer_manager (Any): Customer Manager Agent instance
        user_input (str): User input query
        session (Any | None): SQLiteSession for context management (optional). Defaults to None
        history_limit (int | None): Maximum number of history entries (optional). Defaults to None
    
    Yields:
        str | dict: Token-by-token text deltas (str) or final result/error (dict)
            Final result format: {"type": "final_result", "final_output": str, "agent_name": str, "full_text": str}
            Error format: {"type": "error", "error": str, "error_type": str}
    
    Notes:
        - Real token streaming from OpenAI API
        - Uses Runner.run_streamed() for token-by-token output
        - Compatible with st.write_stream() in Streamlit
    """
    try:
        if session:
            # Limit history for token optimization
            if history_limit is not None:
                session = limit_session_history(session, history_limit)

            with trace(
                "Customer Feedback Multi-Agent Analysis (Streamed)",
                group_id=f"session_{session.session_id}",
            ):
                result = Runner.run_streamed(customer_manager, user_input, session=session)
        else:
            # Fallback without session
            result = Runner.run_streamed(customer_manager, user_input)

        # Collect complete response for history
        full_text = []
        agent_name = None
        
        # Stream events
        async for event in result.stream_events():
            # Stream token-by-token text deltas
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                token = event.data.delta
                full_text.append(token)
                yield token  # Real token streaming
            
            # Agent tracking
            elif event.type == "agent_updated_stream_event":
                agent_name = event.new_agent.name
        
        # After streaming: final_output is now available
        # Use result.final_output if available, otherwise fallback to full_text
        final_output = result.final_output if result.final_output is not None else "".join(full_text)
        
        yield {
            "type": "final_result",
            "final_output": final_output,
            "agent_name": agent_name or (result.last_agent.name if result.last_agent else 'Assistant'),
            "full_text": "".join(full_text)  # For debugging/comparison
        }

    except Exception as e:
        # Return error info
        yield {
            "type": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }


def initialize_system(
    is_azure_openai: bool = False,
    csv_path: str = "./data/feedback_data.csv",
    vectorstore_type: str = "chroma",
    create_new_store: bool = False,
    embedding_model: str = "text-embedding-ada-002",
    is_synthetic_data: bool = False,
    n_synthetic_samples: int = 10000,
    synthetic_start_date: str = '2023-01-01',
    synthetic_end_date: str = datetime.now().strftime('%Y-%m-%d')
):
    """
    Initializes the RAG system with all components.
    
    Args:
        is_azure_openai (bool): If True uses Azure OpenAI, if False uses standard OpenAI. Defaults to False
        csv_path (str): Path to CSV file with feedback data. Defaults to "./data/feedback_data.csv"
        vectorstore_type (str): Type of VectorStore (currently only "chroma" supported). Defaults to "chroma"
        create_new_store (bool): If True creates new VectorStore. Defaults to False
        embedding_model (str): OpenAI embedding model for VectorStore. Defaults to "text-embedding-ada-002"
            - "text-embedding-ada-002": Best cross-lingual performance (78.4%)
            - "text-embedding-3-small": Cheaper but weaker cross-lingual (29.4%)
            - "text-embedding-3-large": More expensive but also weak cross-lingual (32.2%)
        is_synthetic_data (bool): If True uses synthetic data (no enhancement), if False uses original data. Defaults to False
        n_synthetic_samples (int): Number of synthetic records (only if is_synthetic_data=True). Defaults to 10000
        synthetic_start_date (str): Start date for synthetic data (format: 'YYYY-MM-DD'). Defaults to '2023-01-01'
        synthetic_end_date (str): End date for synthetic data (format: 'YYYY-MM-DD'). Defaults to current date
    
    Returns:
        tuple[Any, Any]: (customer_manager, collection) where:
            - customer_manager (Any): Configured Customer Manager Agent instance
            - collection (Any): ChromaDB Collection instance
    
    Raises:
        ValueError: If API keys are missing or VectorStore cannot be created
        FileNotFoundError: If CSV file does not exist (for original data)
    
    Notes:
        - Initializes OpenAI client (Azure or standard)
        - Loads and enhances CSV data (automatically saved for original data)
        - Creates/loads VectorStore with chosen embedding model
        - Configures multi-agent system
    """
    # Import agent modules locally to avoid circular imports
    from customer_agents.chart_creator_agent import create_chart_creator_agent
    from customer_agents_tools.search_tool import SearchToolFactory
    from customer_agents.feedback_analysis_agent import create_feedback_analysis_agent
    from customer_agents.customer_manager_agent import create_customer_manager_agent
    from customer_agents_tools.get_metadata_tool import create_metadata_tool
    from customer_agents_tools.create_charts_tool import create_chart_creation_tool
    from customer_agents.output_summarizer_agent import create_output_summarizer_agent
    
    # Initialize OpenAI client FIRST (required for VectorStore)
    if is_azure_openai:
        azure_client = get_azure_openai_client()
        if azure_client is None:
            raise ValueError("❌ Azure OpenAI Client could not be initialized!")
    else:
        openai_client = get_openai_client()
        if openai_client is None:
            raise ValueError("❌ OpenAI Client could not be initialized!")
    
    # Load and enhance CSV data (conditional based on data type)
    if not is_synthetic_data and not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
    customer_data = load_csv(
        path=csv_path, 
        is_synthetic=is_synthetic_data,
        n_synthetic_samples=n_synthetic_samples,
        synthetic_start_date=synthetic_start_date,
        synthetic_end_date=synthetic_end_date
    )

    # Load or create VectorStore with specified embedding model
    collection = load_vectorstore(
        data=customer_data, 
        type=vectorstore_type, 
        create_new_store=create_new_store,
        embedding_model=embedding_model
    )
    
    if collection is None:
        raise ValueError("❌ VectorStore could not be created/loaded!")
    
    if collection.count() == 0:
        raise ValueError("❌ VectorStore is empty - no documents were created!")

    # Create tools for agents
    search_customer_feedback = SearchToolFactory.create_search_tool(collection)
    build_metadata_snapshot = create_metadata_tool(collection)
    
    # Build metadata snapshot (pre-compute all metadata for Customer Manager)
    # This avoids repeated tool calls and embeds metadata directly in the agent instructions
    metadata_snapshot = build_metadata_snapshot()

    # Create agent hierarchy with native handoffs
    output_summarizer = create_output_summarizer_agent()

    # Create Feedback Analysis Agent (focused on search and content analysis)
    feedback_analysis_agent = create_feedback_analysis_agent(
        search_tool=search_customer_feedback,
        handoff_agents=[output_summarizer],
    )

    # Create Chart Creator Agent (reads market mappings from Session Context)
    chart_creation_agent = create_chart_creator_agent(
        chart_creation_tool=create_chart_creation_tool(collection)
    )

    # Customer Manager with embedded metadata snapshot (no metadata_analysis_agent needed)
    customer_manager = create_customer_manager_agent(
        metadata_snapshot=metadata_snapshot,  # Pre-computed metadata embedded in instructions
        handoff_agents=[
            feedback_analysis_agent,  # For content analysis
            chart_creation_agent,     # For visualizations
        ],
    )

    return customer_manager, collection
