#!/usr/bin/env python3
"""
Streamlit Chat UI for Customer Feedback RAG System.
Identical functionality to app.py with clean main() structure.
"""

import streamlit as st
import os
from agents import SQLiteSession
from dotenv import load_dotenv

from utils.helper_functions import (
    is_azure_openai,
    check_vectorstore_exists,
    extract_chart_path,
    extract_all_chart_paths,  # ✅ Für Multi-Chart Support
    process_query_streamed,  # ✅ Echtes Token-Streaming
    initialize_system
)

# Import test questions for example queries
from test.test_questions import TestQuestions

# Import our simple history manager (for UI display)
from utils.simple_history import SimpleConversationHistory

# Import modular style components
from streamlit_styles.header_styles import render_header_section
from streamlit_styles.footer_styles import render_footer
from streamlit_styles.layout_styles import apply_main_layout_styles

load_dotenv()

# ============================================================================
# DATA SOURCE CONFIGURATION
# ============================================================================
# Flag to choose between synthetic or original data
USE_SYNTHETIC_DATA = True  # Set to False to use original data (feedback_data.csv)

# File paths
FILE_PATH_SYNTHETIC = "./data/feedback_synthetic.csv"
FILE_PATH_ORIGINAL = "./data/feedback_data.csv"

# Determine active CSV path based on flag
FILE_PATH_CSV = FILE_PATH_SYNTHETIC if USE_SYNTHETIC_DATA else FILE_PATH_ORIGINAL

# VectorStore Configuration
VECTORSTORE_TYPE = "chroma"
VECTORSTORE_PATH = "./chroma"
VECTORSTORE_COLLECTION_NAME = "feedback_data"
FORCE_RECREATE_VECTORSTORE = False  # ⚠️ ACHTUNG: True = VectorStore wird IMMER neu erstellt (löscht alte Daten!)

# AZURE OPENAI OR OPENAI - Automatische Erkennung basierend auf Umgebungsvariablen
IS_AZURE_OPENAI = is_azure_openai()

# HISTORY LIMIT - Begrenzt die Anzahl der Historie-Turns an die LLM
# None = unbegrenzt (alles wird gesendet)
# 4 = nur die letzten 4 Interaktionen werden gesendet
# Empfohlen: 3-5 für Balance zwischen Kontext und Token-Kosten
HISTORY_LIMIT = 4

# EXAMPLE QUERIES - Strategisch ausgewählte Fragen für maximalen "AHA-Effekt"
EXAMPLE_QUERIES = [
    # 1. META-FRAGE - Zeigt metadata_tool in Aktion (schnelle, präzise Antwort)
    TestQuestions.META_QUESTIONS[1],  # "Wie ist die NPS-Verteilung in deinem Datensatz?"
    
    # 2. KOMPLEXE ANALYSE - Nutzt search_customer_feedback mit Multi-Kriterien
    TestQuestions.FEEDBACK_ANALYSIS_QUESTIONS[2],  # "Was sind die Top 5 Beschwerden?"
    
    # 3. SENTIMENT + NPS - Zeigt intelligente Filterung und Sentiment-Analyse
    TestQuestions.SENTIMENT_QUESTIONS[1],  # "Analysiere das Sentiment der Promoter"
    
    # 4. GEOGRAFISCHE ANALYSE - Demonstriert Markt-Filter und regionale Insights
    TestQuestions.FEEDBACK_ANALYSIS_QUESTIONS[1],  # "Zeige mir negative Feedbacks aus Deutschland"
    
    # 5. CHART-GENERATION - Zeigt chart_creator_agent für visuelle Insights
    "Erstelle ein Balkendiagramm der Top 5 Themen mit NPS-Scores",
]

# Removed render_native_response and render_structured_summary functions
# All responses are now handled uniformly with streaming

def ensure_session_initialized():
    """
    Ensures that the session is initialized.
    Uses in-memory SQLite (:memory:) for non-persistent sessions.
    Session exists only during the current browser session.
    
    Returns:
        SQLiteSession: Initialized session object from st.session_state
    """
    if "session" not in st.session_state:
        st.session_state.session = SQLiteSession(
            "streamlit_feedback_session", 
            ":memory:"  # In-Memory Datenbank - keine Persistenz
        )
    return st.session_state.session


@st.cache_data(ttl=1)  # Cache for 1 second to reduce multiple calls in same render
def get_cached_conversation_stats():
    """
    Cached wrapper for conversation stats to avoid multiple API calls.
    
    Returns:
        dict: Dictionary containing conversation statistics
    """
    return st.session_state.conversation.get_summary_stats()


def render_chart(chart_path: str, size: str = "Mittel"):
    """
    Displays chart with selected size (Small/Medium/Large).
    
    Args:
        chart_path (str): Path to the chart file
        size (str): Size option ("Klein", "Mittel", "Groß"). Defaults to "Mittel"
    
    Returns:
        None
    """
    # Konvertiere relativen Pfad zu absolutem Pfad
    if not os.path.isabs(chart_path):
        chart_path = os.path.abspath(chart_path)
    
    if not os.path.exists(chart_path):
        st.warning(f"⚠️ Chart nicht gefunden: {os.path.basename(chart_path)}")
        return
    
    # Größen-Konfiguration: [left_margin, center_content, right_margin]
    size_config = {
        "Klein": [2, 2, 2],   # Schmal in der Mitte
        "Mittel": [1, 3, 1],  # Standard
        "Groß": [0, 1, 0]     # Vollbild
    }
    
    cols = size_config.get(size, [1, 3, 1])
    
    try:
        if cols == [0, 1, 0]:
            # Vollbild
            st.image(chart_path, use_container_width=True, 
                    caption=f"📊 {os.path.basename(chart_path)}")
        else:
            # Mit Margins
            col1, col2, col3 = st.columns(cols)
            with col2:
                st.image(chart_path, use_container_width=True,
                        caption=f"📊 {os.path.basename(chart_path)}")
    except Exception as e:
        st.error(f"❌ Fehler beim Anzeigen: {e}")


async def stream_agent_response(customer_manager, user_input: str, session, history_limit: int):
    """
    Async generator for real token streaming from agent.
    Streamlit automatically converts async generator to sync!
    
    Args:
        customer_manager (Any): Customer Manager Agent instance
        user_input (str): User input text
        session (SQLiteSession): SQLite session object
        history_limit (int): History limit for conversation context
    
    Yields:
        str: Tokens for Streamlit streaming display
    """
    async for chunk in process_query_streamed(customer_manager, user_input, session, history_limit):
        if isinstance(chunk, str):
            # Token-by-Token Text - wird direkt gestreamt
            yield chunk
        elif isinstance(chunk, dict):
            # Final result oder Error - speichere für späteren Zugriff
            st.session_state._streaming_final_result = chunk


@st.cache_resource(show_spinner=False)
def initialize_system_cached(is_azure_openai: bool=False, csv_path: str=FILE_PATH_CSV, is_synthetic: bool=False):
    """
    Streamlit wrapper for initialize_system with caching.
    Calls business logic from helper_functions and adds UI-specific validation.
    
    Args:
        is_azure_openai (bool): If True uses Azure OpenAI, if False uses standard OpenAI. Defaults to False
        csv_path (str): Path to CSV file. Defaults to FILE_PATH_CSV
        is_synthetic (bool): If True uses synthetic data, if False uses original data. Defaults to False
    
    Returns:
        tuple[Any, Any]: Tuple containing (customer_manager, collection) where:
            - customer_manager (Any): Initialized Customer Manager Agent
            - collection (Any): ChromaDB collection instance
    
    Raises:
        ValueError: If initialization fails due to missing API keys or invalid configuration
        FileNotFoundError: If CSV file does not exist
    """
    try:
        # Rufe die core Business-Logic auf (aus helper_functions)
        customer_manager, collection = initialize_system(
            is_azure_openai=is_azure_openai,
            csv_path=csv_path,
            vectorstore_type=VECTORSTORE_TYPE,
            create_new_store=False,  # Gecachte Version lädt immer existierenden VectorStore
            embedding_model="text-embedding-ada-002",
            is_synthetic_data=is_synthetic
        )
        
        return customer_manager, collection
        
    except ValueError as e:
        # Handle initialization errors with Streamlit UI
        st.error(str(e))
        st.stop()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()
    except Exception as e:
        st.error(f"❌ Unerwarteter Fehler bei System-Initialisierung: {e}")
        st.stop()


# process_query ist jetzt in utils.helper_functions
# und wird direkt von dort importiert und verwendet
# (limit_session_history wird intern von process_query aufgerufen)


def main():
    """
    Main Streamlit application.
    
    Initializes the RAG system, handles user interactions, displays chat history,
    and manages the overall UI flow.
    
    Returns:
        None
    """

    # Page config
    st.set_page_config(
        page_title="Customer Feedback App",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Apply main layout styles
    apply_main_layout_styles()

    # ============================================================================
    # HEADER SECTION - Title with Clear Chat Button
    # ============================================================================

    col_header, col_button = st.columns([5, 1])

    with col_header:
        # Use modular header components
        render_header_section()

    with col_button:
        st.write("")  # Spacer for better alignment
        if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat_header"):
            st.session_state.conversation.clear_history()
            st.toast("✅ Chat cleared!", icon="🗑️")
            st.rerun()

    st.divider()
    
    # ============================================================================
    # SESSION STATE INITIALIZATION
    # ============================================================================

    if "conversation" not in st.session_state:
        st.session_state.conversation = SimpleConversationHistory()
    
    # Ensure SQLiteSession is initialized (in-memory) for agents
    ensure_session_initialized()

    if "system_initialized" not in st.session_state:
        st.session_state.system_initialized = False
    
    # System-Initialisierung nur beim ersten Mal durchführen
    if not st.session_state.system_initialized:
        # Prüfe VectorStore Status
        vectorstore_exists, vectorstore_count = check_vectorstore_exists(
            vectorstore_path=VECTORSTORE_PATH,
            collection_name=VECTORSTORE_COLLECTION_NAME
        )
        
        # Bestimme ob VectorStore neu erstellt werden muss
        # LOGIK:
        # 1. FORCE_RECREATE_VECTORSTORE = True → IMMER neu erstellen
        # 2. VectorStore existiert nicht → neu erstellen
        # 3. VectorStore ist leer (count == 0) → neu erstellen
        # 4. Sonst → existierenden laden
        create_new_vectorstore = (
            FORCE_RECREATE_VECTORSTORE or 
            not vectorstore_exists or 
            vectorstore_count == 0
        )
        
        if create_new_vectorstore:
            # VectorStore muss (neu) erstellt werden
            data_source = "synthetischen" if USE_SYNTHETIC_DATA else "originalen"
            with st.spinner(f"🔨 Erstelle VectorStore mit {data_source} Daten... Dies kann einige Minuten dauern..."):
                try:
                    customer_manager, collection = initialize_system(
                        is_azure_openai=IS_AZURE_OPENAI,
                        csv_path=FILE_PATH_CSV,
                        vectorstore_type=VECTORSTORE_TYPE,
                        create_new_store=True,
                        embedding_model="text-embedding-ada-002",
                        is_synthetic_data=USE_SYNTHETIC_DATA 
                    )
                    st.session_state.customer_manager = customer_manager
                    st.session_state.collection = collection
                    st.session_state.system_initialized = True
                    st.success(f"✅ VectorStore erfolgreich erstellt mit {collection.count():,} Dokumenten!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Fehler beim Erstellen des VectorStore: {e}")
                    st.stop()
        else:
            # VectorStore existiert bereits - nutze gecachte Version
            with st.spinner("🔄 Initialisiere RAG-System..."):
                try:
                    customer_manager, collection = initialize_system_cached(
                        is_azure_openai=IS_AZURE_OPENAI,
                        csv_path=FILE_PATH_CSV,
                        is_synthetic=USE_SYNTHETIC_DATA  # ✅ FLAG übergeben
                    )
                    st.session_state.customer_manager = customer_manager
                    st.session_state.collection = collection
                    st.session_state.system_initialized = True
                    
                    data_source = "synthetischen" if USE_SYNTHETIC_DATA else "originalen"
                    st.success(f"✅ System initialisiert mit {collection.count():,} Dokumenten aus {data_source} Daten")
                except Exception as e:
                    st.error(f"❌ Fehler bei System-Initialisierung: {e}")
                    st.stop()
    
    # SIDEBAR - Settings and Statistics
    # ============================================================================

    with st.sidebar:
        # Predefined example queries - moved to top
        st.subheader("💡 Example Queries")

        # Use globally defined example queries from configuration section
        for query in EXAMPLE_QUERIES:
            # ✅ Set pending query in session state instead of callback
            if st.button(query, key=f"sidebar_{query}", use_container_width=True):
                st.session_state.pending_query = query
                st.rerun()

        st.divider()
        
        # ✅ Chart Size Selector (Clean & Simple)
        st.subheader("📊 Chart-Größe")
        
        # Use radio buttons instead - no cutoff issues
        chart_size = st.radio(
            "Größe wählen",
            options=["Klein", "Mittel", "Groß"],
            index=1 if st.session_state.get('chart_size', 'Mittel') == 'Mittel' 
                  else (0 if st.session_state.get('chart_size', 'Mittel') == 'Klein' else 2),
            label_visibility="collapsed",
            horizontal=True
        )
        st.session_state['chart_size'] = chart_size

        st.divider()

        # Export options
        st.subheader("📄 Export Options")

        if st.button("📋 Export as Text", use_container_width=True):
            if st.session_state.conversation.get_conversation_count() > 0:
                export_stats = get_cached_conversation_stats()
                export_text = st.session_state.conversation.export_history("text")
                st.download_button(
                    "💾 Download Text",
                    export_text,
                    file_name=f"conversation_{export_stats['session_id']}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            else:
                st.warning("No conversation to export")

        if st.button("🧹 Clear History", use_container_width=True):
            st.session_state.conversation.clear_history()
            st.rerun()

        st.divider()
        st.subheader("📈 System Info")

        st.info(f"Documents: {st.session_state.collection.count():,}")
        
        # History Limit Info
        if HISTORY_LIMIT:
            st.caption(f"💡 Historie-Limit: {HISTORY_LIMIT} Turns (spart Token-Kosten)")
        else:
            st.caption("⚠️ Historie unbegrenzt (höhere Token-Kosten)")

        # Combined Conversation Statistics - moved to bottom
        stats = get_cached_conversation_stats()

        if stats["total_interactions"] > 0:
            st.divider()
            st.subheader("📊 Konversations-Summary")
            st.write(f"Interactions: {stats['total_interactions']}")
            st.write(f"Avg Input: {stats['avg_user_input_length']} chars")
            st.write(f"Avg Response: {stats['avg_response_length']} chars")
            st.write("Used Agents:")
            for agent, count in stats["agents_used"].items():
                st.write(f"• {agent}: {count}x")

# ============================================================================
# CHAT HISTORY DISPLAY - Shows all previous messages
# ============================================================================
    
    # Load and display history FIRST (before processing new queries)
    history = st.session_state.conversation.get_history()
    
    # Display all history messages
    for _ , entry in enumerate(history):
        # User message
        with st.chat_message(name="user", avatar="🧑"):
            st.write(entry["user"])

        # Assistant response
        with st.chat_message(name="assistant", avatar="🧠"):
            response_text = entry["response"]
            if response_text.startswith("❌ **ERROR:**"):
                st.error(response_text)
            else:
                # ✅ Check for charts in history (handle multiple charts)
                text_content, chart_paths = extract_all_chart_paths(response_text)
                
                st.markdown(text_content)
                
                # ✅ Render ALL charts if found in history
                if chart_paths:
                    chart_size = st.session_state.get('chart_size', 'Mittel')
                    for chart_path in chart_paths:
                        render_chart(chart_path, size=chart_size)

# ============================================================================
# CHAT INPUT AT BOTTOM - Fixed position
# ============================================================================

    # ✅ Check for pending query from sidebar
    if "pending_query" in st.session_state:
        user_input = st.session_state.pending_query
        del st.session_state.pending_query
    else:
        # User input at the bottom of the page
        user_input = st.chat_input("Ask about customer feedback...")

    # ✅ Process query with LIVE streaming, then rerun
    if user_input:
        # Show user message immediately
        with st.chat_message("user", avatar="🧑"):
            st.write(user_input)
        
        # Show streaming response with "Thinking..." indicator
        with st.chat_message("assistant", avatar="🧠"):
            # ✅ Create placeholder for progressive display
            response_placeholder = st.empty()
            
            # ✅ Show "Thinking..." while waiting for first token
            response_placeholder.markdown("_Thinking..._")
            
            # ✅ LIVE Token-Streaming from OpenAI (replaces "Thinking...")
            streamed_text = response_placeholder.write_stream(
                stream_agent_response(
                    st.session_state.customer_manager,
                    user_input,
                    ensure_session_initialized(),
                    HISTORY_LIMIT
                )
            )
            
            # After streaming, check for charts (handle multiple)
            final_result = st.session_state.get('_streaming_final_result', None)
            if final_result and final_result.get("type") != "error":
                raw_response = final_result.get('final_output', streamed_text)
                text_content, chart_paths = extract_all_chart_paths(raw_response)
                if chart_paths:
                    chart_size = st.session_state.get('chart_size', 'Mittel')
                    for chart_path in chart_paths:
                        render_chart(chart_path, size=chart_size)
        
        # After display, save to history and trigger rerun
        # Process in background to save to history
        final_result = st.session_state.get('_streaming_final_result', None)
        
        if final_result and final_result.get("type") == "error":
            error_message = f"❌ **ERROR ({final_result.get('error_type', 'Unknown')}):** {final_result['error']}"
            response_content = error_message
            agent_name_str = "Assistant"
        elif final_result:
            raw_response = final_result.get('final_output', streamed_text)
            agent_name_str = final_result.get('agent_name', 'Assistant')
            response_content = raw_response
        else:
            response_content = streamed_text
            agent_name_str = "Assistant"
        
        # Cleanup
        if '_streaming_final_result' in st.session_state:
            del st.session_state._streaming_final_result
        
        # Save to history - ensure response_content is string
        st.session_state.conversation.add_interaction(
            user_input=user_input,
            agent_response=str(response_content) if response_content else "",
            agent_name=agent_name_str)
        
        # Trigger rerun to show clean history
        st.rerun()

# ============================================================================
# FOOTER - Modular Footer with Live Statistics
# ============================================================================

    # Use modular footer component with cached stats
    stats = get_cached_conversation_stats()
    render_footer(stats)


if __name__ == "__main__":
    main()
