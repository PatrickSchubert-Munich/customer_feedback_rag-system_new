import os
import re
import chromadb
from agents import (
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
    Runner,
    trace,
)
from openai import AsyncAzureOpenAI, AsyncOpenAI, OpenAIError
from typing import Any
import pandas as pd

# Import base utilities (avoid circular imports by importing agents only in initialize_system)
from utils.clean_csv_file import CSVloader
from utils.prepare_customer_data import PrepareCustomerData
from db.vectorstore_chroma import ChromaVectorStore
from test.test_questions import TestQuestions


def is_azure_openai() -> bool:
    """Prüft ob Azure OpenAI konfiguriert ist basierend auf Umgebungsvariablen"""
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
    Prüft ob VectorStore existiert und gibt Anzahl der Dokumente zurück.
    
    Args:
        vectorstore_path: Pfad zum VectorStore-Verzeichnis
        collection_name: Name der ChromaDB-Collection
    
    Returns:
        tuple[bool, int]: (exists, document_count)
            - exists: True wenn VectorStore existiert
            - document_count: Anzahl der Dokumente im VectorStore (0 wenn nicht existiert)
    """
    try:
        # Prüfe ob Verzeichnis existiert
        vectorstore_full_path = os.path.join(vectorstore_path, "feedback_vectorstore")
        if not os.path.exists(vectorstore_full_path):
            return (False, 0)
        
        # Prüfe ob Collection existiert
        client = chromadb.PersistentClient(path=vectorstore_path)
        collections = client.list_collections()
        
        for collection in collections:
            if collection.name == collection_name:
                # Collection existiert - hole Anzahl der Dokumente
                try:
                    coll = client.get_collection(name=collection_name)
                    doc_count = coll.count()
                    return (True, doc_count)
                except Exception:
                    return (False, 0)
        
        # Collection nicht gefunden
        return (False, 0)
        
    except Exception as e:
        print(f"⚠️ Fehler beim Prüfen des VectorStore: {e}")
        return (False, 0)


def get_model_name(model_type: str = "gpt4o") -> str:
    """
    Gibt den korrekten Modellnamen basierend auf Azure/OpenAI Konfiguration zurück
    
    Args:
        model_type: "gpt4o" für GPT-4 Omni oder "gpt4o_mini" für GPT-4 Omni Mini
    
    Returns:
        str: Korrekter Modellname für Azure OpenAI oder Standard OpenAI
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


def load_csv(path: str, write_local: bool = False) -> pd.DataFrame:
    """
    Lädt CSV-Datei und führt automatisches Enhancement durch.
    
    Enhancement umfasst:
    - NPS-Kategorisierung (Detractor/Passive/Promoter)
    - Market-Split in Region/Country
    - Token-Count Berechnung
    - Sentiment-Analyse
    - Topic-Klassifizierung
    
    Args:
        path: Pfad zur CSV-Datei
        write_local: True = Speichert enhanced CSV in ./data/feedback_data_enhanced.csv
    
    Returns:
        Enhanced DataFrame mit zusätzlichen Spalten
    """
    csv_loader = CSVloader(path=path, encoding="utf-8")
    df = csv_loader.load_csv()

    # Prepare DataFrame with all enhancement features (automatic)
    customer_data = PrepareCustomerData(
        data=df,
        nps_category_col_name="NPS",
        feedback_col_name="Verbatim",
        market_col_name="Market",
        feedback_token_model=get_model_name("gpt4o_mini")
    )

    df = customer_data.data

    # Optionally write enhanced CSV locally
    if write_local:
        write_prepared_csv(df)

    print(f"✅ CSV-Daten geladen: {df.shape[0]} Einträge")

    return df


def write_prepared_csv(
    data: pd.DataFrame, path: str = "./data/feedback_data_enhanced.csv"
) -> None:
    """
    Speichert enhanced DataFrame als CSV-Datei.
    
    Args:
        data: Enhanced DataFrame
        path: Ziel-Pfad für CSV-Datei
    """
    data.to_csv(path, index=False, encoding="utf-8", mode="w")
    print(f"Enhanced CSV written to {path}")


def load_vectorstore(
    data: pd.DataFrame, 
    type: str = "chroma", 
    create_new_store: bool = False,
    embedding_model: str = "text-embedding-ada-002"  # ✅ KORRIGIERT: Ada-002 als Default
) -> Any | None:
    """
    Lädt oder erstellt einen VectorStore.
    
    Args:
        data: DataFrame mit Customer-Feedback-Daten
        type: VectorStore-Typ (aktuell nur "chroma" unterstützt)
        create_new_store: True = VectorStore neu erstellen, False = existierenden laden
        embedding_model: OpenAI Embedding-Modell (Default: "text-embedding-ada-002")
            - "text-embedding-ada-002": Beste Cross-Lingual Performance (78.4% avg similarity)
            - "text-embedding-3-small": Günstiger, aber schlechtere Cross-Lingual (29.4%)
            - "text-embedding-3-large": Teurer, aber auch schlechte Cross-Lingual (32.2%)
    
    Returns:
        ChromaDB Collection oder None bei Fehler
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

        # Prüfe ob Collection erfolgreich erstellt/geladen wurde
        if chroma_collection is None:
            print("❌ FEHLER: VectorStore konnte nicht erstellt/geladen werden!")
            return None
        
        return chroma_collection
    
    print(f"❌ FEHLER: Unbekannter VectorStore-Typ '{type}'. Have to be 'chroma' for now.")
    return None


def get_azure_openai_client() -> AsyncAzureOpenAI | None:
    """
    Initialisiert Azure OpenAI Client und setzt als Default für agents.
    
    Benötigte Umgebungsvariablen:
    - AZURE_OPENAI_API_KEY
    - AZURE_OPENAI_ENDPOINT
    - AZURE_OPENAI_API_VERSION
    
    Returns:
        AsyncAzureOpenAI Client oder None bei Fehler
    
    Raises:
        ValueError: Wenn erforderliche Umgebungsvariablen fehlen
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
        print("❌ FEHLER: Azure OpenAI Client konnte nicht initialisiert werden!")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        print("❌ FEHLER: Azure OpenAI Client konnte nicht initialisiert werden!")
    return None


def get_openai_client() -> AsyncOpenAI | None:
    """
    Initialisiert Standard OpenAI Client.
    
    Benötigte Umgebungsvariablen:
    - OPENAI_API_KEY
    
    Returns:
        AsyncOpenAI Client oder None bei Fehler
    
    Raises:
        ValueError: Wenn OPENAI_API_KEY nicht gesetzt ist
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
        print("❌ FEHLER: OpenAI Client konnte nicht initialisiert werden!")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        print("❌ FEHLER: OpenAI Client konnte nicht initialisiert werden!")
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
    Generiert Testfragen basierend auf den übergebenen Flags.

    Args:
        test_meta: Meta-Fragen (Datensatz-Informationen)
        test_feedback: Feedback-Analysen
        test_validation: Markt-Validierung
        test_sentiment: Sentiment-Analysen
        test_parameters: User-Parameter Extraktion
        test_complex: Komplexe Multi-Kriterien Queries
        test_edge: Edge Cases (standardmäßig deaktiviert)
        questions_per_category: Anzahl Fragen pro aktivierter Kategorie

    Returns:
        Liste der generierten Testfragen
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
    Begrenzt die Session-Historie auf die letzten N Einträge.
    WICHTIG: Entfernt __CHART__ Marker aus History für Agent-Kontext!
    
    Args:
        session: SQLiteSession Objekt
        max_history: Maximale Anzahl Historie-Einträge (None = unbegrenzt)
    
    Returns:
        Session mit begrenzter Historie und bereinigten Responses
    
    Note:
        - Chart-Marker werden entfernt um Token-Konsum zu optimieren
        - Charts sind nur für UI relevant, nicht für Agent-Kontext
        - Bei Fehler wird Original-Session zurückgegeben (Robustheit)
    """
    try:
        # Hole aktuelle Historie
        history = session.get_history()
        
        if not history:
            return session
        
        # ✅ CHART-BEREINIGUNG: Entferne __CHART__ Marker für Token-Optimierung
        # Charts sind nur für UI relevant, nicht für Agent-Kontext!
        cleaned_history = []
        for entry in history:
            # Erstelle Kopie des Eintrags
            cleaned_entry = entry.copy()
            
            # Bereinige Response von Chart-Markern
            if "content" in cleaned_entry:
                content = cleaned_entry["content"]
                if isinstance(content, list):
                    # Handle multi-part content
                    cleaned_content = []
                    for part in content:
                        if isinstance(part, dict) and "text" in part:
                            # Entferne __CHART__pfad__CHART__ Pattern
                            cleaned_text = re.sub(r'__CHART__[^_]+__CHART__', '', part["text"])
                            part["text"] = cleaned_text.strip()
                        cleaned_content.append(part)
                    cleaned_entry["content"] = cleaned_content
                elif isinstance(content, str):
                    # Handle simple string content
                    cleaned_entry["content"] = re.sub(r'__CHART__[^_]+__CHART__', '', content).strip()
            
            cleaned_history.append(cleaned_entry)
        
        # Begrenze History falls nötig
        if max_history and len(cleaned_history) > max_history:
            cleaned_history = cleaned_history[-max_history:]
        
        # Setze bereinigte History zurück
        session.set_history(cleaned_history)
            
    except (AttributeError, Exception) as e:
        # Falls Session keine History-Methoden hat oder Fehler auftritt,
        # gib Original zurück (Fallback für Robustheit)
        pass
    
    return session


async def process_query(customer_manager, user_input: str, session=None, history_limit: int | None = None):
    """
    Verarbeitet User-Query mit Multi-Agent-System.
    
    Args:
        customer_manager: Customer Manager Agent
        user_input: Benutzer-Eingabe
        session: SQLiteSession für Kontext-Verwaltung (optional)
        history_limit: Maximale Anzahl Historie-Einträge (optional)
    
    Returns:
        Result-Objekt mit agent.final_output Attribut oder Error-Dict
    
    Error-Format:
        {"error": str, "error_type": str}
    
    Note:
        - Automatische Historie-Begrenzung für Token-Optimierung
        - Tracing mit session_id für Debugging
        - Robuste Error-Handling
    """
    try:
        if session:
            # HISTORIE BEGRENZEN für Token-Optimierung
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


def initialize_system(
    is_azure_openai: bool = False,
    csv_path: str = "./data/feedback_data.csv",
    write_enhanced_csv: bool = True,
    vectorstore_type: str = "chroma",
    create_new_store: bool = False,
    embedding_model: str = "text-embedding-ada-002"  # Ada-002: Superior Cross-Lingual (92% avg)
):
    """
    Initialisiert das RAG-System mit allen Komponenten.
    
    Args:
        is_azure_openai: True = Azure OpenAI, False = Standard OpenAI
        csv_path: Pfad zur CSV-Datei mit Feedback-Daten
        write_enhanced_csv: True = Speichert enhanced CSV lokal
        vectorstore_type: Typ des VectorStore (aktuell nur "chroma")
        create_new_store: True = VectorStore neu erstellen
        embedding_model: OpenAI Embedding-Modell für VectorStore
                        Default: text-embedding-ada-002 (beste Cross-Lingual Performance)
                        Alternative: text-embedding-3-small, text-embedding-3-large
            - "text-embedding-ada-002": Beste Cross-Lingual Performance (78.4%)
            - "text-embedding-3-small" (Default): Günstiger, aber schwächer (29.4%)
            - "text-embedding-3-large": Teurer, aber auch schwach (32.2%)
    
    Returns:
        tuple: (customer_manager, collection)
            - customer_manager: Konfigurierter Customer Manager Agent
            - collection: ChromaDB Collection
    
    Raises:
        ValueError: Bei fehlenden API-Keys
        FileNotFoundError: Wenn CSV nicht existiert
    
    Note:
        - Initialisiert OpenAI Client (Azure oder Standard)
        - Lädt und enhanced CSV-Daten
        - Erstellt/lädt VectorStore mit gewähltem Embedding-Modell
        - Konfiguriert Multi-Agent-System
    """
    # Import agent modules locally to avoid circular imports
    from customer_agents.chart_creator_agent import create_chart_creator_agent
    from customer_agents_tools.search_tool import RobustSearchToolFactory
    from customer_agents.feedback_analysis_agent import create_feedback_analysis_agent
    from customer_agents.customer_manager_agent import create_customer_manager_agent
    from customer_agents_tools.get_metadata_tool import create_metadata_tool
    from customer_agents_tools.create_charts_tool import create_chart_creation_tool
    from customer_agents.output_summarizer_agent import create_output_summarizer_agent
    
    # Initialize OpenAI client FIRST (required for VectorStore)
    if is_azure_openai:
        azure_client = get_azure_openai_client()
        if azure_client is None:
            raise ValueError("❌ Azure OpenAI Client konnte nicht initialisiert werden!")
    else:
        openai_client = get_openai_client()
        if openai_client is None:
            raise ValueError("❌ OpenAI Client konnte nicht initialisiert werden!")
    
    # Load and enhance CSV data
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV-Datei nicht gefunden: {csv_path}")
        
    customer_data = load_csv(path=csv_path, write_local=write_enhanced_csv)

    # Load or create VectorStore with specified embedding model
    collection = load_vectorstore(
        data=customer_data, 
        type=vectorstore_type, 
        create_new_store=create_new_store,
        embedding_model=embedding_model  # ✅ Übergebenes Modell verwenden
    )
    
    if collection is None:
        raise ValueError("❌ VectorStore konnte nicht erstellt/geladen werden!")
    
    if collection.count() == 0:
        raise ValueError("❌ VectorStore ist leer - keine Dokumente wurden erstellt!")

    # Create tools for agents
    search_customer_feedback = RobustSearchToolFactory.create_search_tool(collection)
    build_metadata_snapshot = create_metadata_tool(collection)
    
    # ✅ BUILD METADATA SNAPSHOT (Pre-compute all metadata for Customer Manager)
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

    # ✅ Customer Manager with embedded metadata snapshot (NO metadata_analysis_agent needed!)
    customer_manager = create_customer_manager_agent(
        metadata_snapshot=metadata_snapshot,  # Pre-computed metadata embedded in instructions
        handoff_agents=[
            feedback_analysis_agent,  # For content analysis
            chart_creation_agent,     # For visualizations
        ],
    )

    return customer_manager, collection
