#!/usr/bin/env python3
"""
Streamlit Chat UI für Customer Feedback RAG System.
Identical functionality to app.py with clean main() structure.
"""

import streamlit as st
import asyncio
import os
import time
from agents import SQLiteSession
from dotenv import load_dotenv

# Import existing system components - identical to app.py
from agents import Runner, trace
from prepare_customer_data import PrepareCustomerData
from customer_agents.chart_creator_agent import create_chart_creator_agent
from customer_agents_tools.robust_search_tool_factory import RobustSearchToolFactory
from customer_agents.feedback_analysis_agent import create_feedback_analysis_agent
from customer_agents.customer_manager_agent import create_customer_manager_agent
from customer_agents_tools.get_metadata_tool import create_metadata_tool
from customer_agents_tools.create_charts_tool import create_chart_creation_tool
from customer_agents.metadata_analysis_agent import create_metadata_analysis_agent
from customer_agents.output_summarizer_agent import create_output_summarizer_agent

from helper_functions import (
    get_azure_openai_client,
    get_openai_client,
    load_csv,
    load_vectorstore,
    is_azure_openai,
)

# Import our simple history manager
from utils.simple_history import SimpleConversationHistory

# Import modular style components
from streamlit_styles.header_styles import render_header_section
from streamlit_styles.footer_styles import render_footer
from streamlit_styles.layout_styles import apply_main_layout_styles

load_dotenv()

# Configuration - identical to app.py
FILE_PATH_CSV = "./data/feedback_data.csv"
# FILE_PATH_CSV = f"{FILE_PATH_CSV_RAW.split(".csv")[0]}_enhanced.csv"
VECTORSTORE_TYPE = "chroma"

# AZURE OPENAI OR OPENAI - Automatische Erkennung basierend auf Umgebungsvariablen
IS_AZURE_OPENAI = is_azure_openai()

# HISTORY LIMIT - Begrenzt die Anzahl der Historie-Turns an die LLM
# None = unbegrenzt (alle Historie wird gesendet)
# 5 = nur die letzten 5 Interaktionen werden gesendet
# Empfohlen: 3-5 für Balance zwischen Kontext und Kosten
HISTORY_LIMIT = 5  # Begrenzt auf letzte 5 Interaktionen

# EXAMPLE QUERIES - Vordefinierte Beispiel-Fragen für die Sidebar
# Diese können leicht angepasst werden, um verschiedene Use Cases zu demonstrieren
EXAMPLE_QUERIES = [
    "Welche Märkte gibt es?",
    "Wie ist die NPS-Verteilung?",
    "Top 5 Kundenbeschwerden",
    "Analysiere negative Feedbacks",
    "Sentiment der Promoter",
    "Balkenchart mit Märkten und Sentiments"
]

# Removed render_native_response and render_structured_summary functions
# All responses are now handled uniformly with streaming

def ensure_session_initialized():
    """
    Stellt sicher, dass die Session initialisiert ist.
    Verwendet In-Memory SQLite (:memory:) für nicht-persistente Sessions.
    Session existiert nur während der aktuellen Browser-Session.
    """
    if "session" not in st.session_state:
        st.session_state.session = SQLiteSession(
            "streamlit_feedback_session", 
            ":memory:"  # In-Memory Datenbank - keine Persistenz
        )
    return st.session_state.session


@st.cache_data(ttl=1)  # Cache for 1 second to reduce multiple calls in same render
def get_cached_conversation_stats():
    """Cached wrapper für conversation stats um multiple API-Calls zu vermeiden."""
    return st.session_state.conversation.get_summary_stats()


def extract_chart_path(text: str) -> tuple[str, str | None]:
    """
    Extrahiert Chart-Pfad aus Response-Text (Format: __CHART__[pfad]__CHART__).
    
    Returns:
        tuple: (text_without_chart_marker, chart_path or None)
    """
    import re
    pattern = r'__CHART__(.*?)__CHART__'
    match = re.search(pattern, text)
    
    if match:
        chart_path = match.group(1).strip()
        text_without_marker = re.sub(pattern, '', text).strip()
        return text_without_marker, chart_path
    
    return text, None


def render_chart(chart_path: str, size: str = "Mittel") -> None:
    """
    Zeigt Chart mit gewählter Größe an (Klein/Mittel/Groß).
    
    Args:
        chart_path: Pfad zum Chart
        size: Größe ("Klein", "Mittel", "Groß")
    """
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


def stream_response(response: str, delay: float = 0.05):
    """
    Streamt Text wortweise für natürliche Anzeige mit Streamlit.
    
    Args:
        response: Der zu streamende Text
        delay: Delay zwischen Wörtern in Sekunden (schneller für bessere UX)
    """
    for word in response.split():
        yield word + " "
        time.sleep(delay)


def process_user_query(user_input: str) -> None:
    """
    Verarbeitet eine Benutzereingabe mit gestreamter Antwort.
    Flow: Zeige Frage → Zeige "Thinking..." → Streame Antwort → Speichere in History
    """
    # Ensure session is initialized
    session = ensure_session_initialized()

    # 1. Zeige User-Frage sofort an
    with st.chat_message("user", avatar="🧑"):
        st.write(user_input)

    # 2. Zeige "Thinking..." Placeholder
    with st.chat_message("assistant", avatar="🧠"):
        placeholder = st.empty()
        placeholder.markdown("Thinking...")
        
        # Backend-Verarbeitung
        response = asyncio.run(
            process_query(st.session_state.customer_manager, user_input, session)
        )
        
        # Handle both success and error cases
        agent_name_str = "Assistant"  # Default fallback
        
        if isinstance(response, dict) and "error" in response:
            # Handle error case
            error_message = f"**ERROR ({response.get('error_type', 'Unknown')}):** {response['error']}"
            placeholder.error(error_message)
            response_content = error_message
        else:
            # Handle success case - result has final_output attribute
            raw_response = str(response.final_output) # type: ignore
            
            # ✅ Agent-Tracking: Extrahiere Agent-Namen aus Response
            agent_name = getattr(response, 'agent', None)
            if agent_name and hasattr(agent_name, 'name'):
                agent_name_str = agent_name.name
            
            # ✅ Chart-Erkennung: Extrahiere Chart-Pfad falls vorhanden
            text_content, chart_path = extract_chart_path(raw_response)
        
            # Stream response to user (visual effect only)
            placeholder.write_stream(stream_response(text_content))
            
            # Clear placeholder and replace with properly formatted Markdown
            # This ensures correct rendering of headers (##), bold text (**), lists, etc.
            placeholder.empty()
            placeholder.markdown(text_content)
            
            # ✅ Chart-Anzeige: Zeige Chart falls vorhanden
            if chart_path:
                chart_size = st.session_state.get('chart_size', 'Mittel')
                render_chart(chart_path, size=chart_size)
            
            # ✅ WICHTIG: Speichere RAW response MIT Chart-Marker für History
            # Damit Charts auch beim Neuladen der History angezeigt werden
            response_content = raw_response
        
        # ✅ Add to conversation history with actual agent name
        st.session_state.conversation.add_interaction(
            user_input=user_input,
            agent_response=response_content,
            agent_name=agent_name_str)


@st.cache_resource(show_spinner=False)
def initialize_system(is_azure_openai: bool=False):
    """Initialize the RAG system components - identical structure to app.py main()"""

    if is_azure_openai:
        # Initialize OpenAI client FIRST (required for VectorStore) - identical to app.py
        azure_client = get_azure_openai_client()
        if azure_client is None:
            st.error("❌ Azure OpenAI Client konnte nicht initialisiert werden!")
            st.stop()
    else:
        openai_client = get_openai_client()
        if openai_client is None:
            st.error("❌ OpenAI Client konnte nicht initialisiert werden!")
            st.stop()
    
    if os.path.exists(FILE_PATH_CSV):
        # Load data and tools - identical to app.py
        customer_data = load_csv(path=FILE_PATH_CSV, write_local=True)
    else:
        raise FileNotFoundError(f"CSV - File {FILE_PATH_CSV} not found.")

    # Versuche zuerst existierenden VectorStore zu laden
    collection = load_vectorstore(
        data=customer_data, type=VECTORSTORE_TYPE, create_new_store=False
    )

    # VALIDIERUNG: Erstelle neuen VectorStore nur wenn er nicht existiert ODER leer ist
    if collection is None:
        st.warning("⚠️ VectorStore existiert nicht. Erstelle neuen VectorStore...")
        collection = load_vectorstore(
            data=customer_data, type=VECTORSTORE_TYPE, create_new_store=True
        )
    elif collection.count() == 0:
        st.warning("⚠️ VectorStore ist leer. Erstelle neuen VectorStore für funktionierende App...")
        collection = load_vectorstore(
            data=customer_data, type=VECTORSTORE_TYPE, create_new_store=True
        )
    else:
        st.success(f"✅ Existierender VectorStore geladen mit {collection.count():,} Dokumenten")
    
    # Finale Validierung nach möglicher Neuerstellung
    if collection is None:
        st.error("❌ VectorStore konnte nicht erstellt werden!")
        st.stop()
    if collection.count() == 0:
        st.error("❌ VectorStore ist nach Erstellung immer noch leer!")
        st.stop()

    # Use enhanced search tool with better error handling - identical to app.py
    search_customer_feedback = RobustSearchToolFactory.create_enhanced_search_tool(
        collection
    )

    # Create metadata tools (unified approach) - identical to app.py
    metadata_tools = create_metadata_tool(collection)  # Returns dict of tools

    # Create agent hierarchy with native handoffs - identical to app.py
    output_summarizer = create_output_summarizer_agent()

    # Create specialized Metadata Analysis Agent (no handoffs - only serves Customer Manager) - identical to app.py
    metadata_analysis_agent = create_metadata_analysis_agent(
        metadata_tools=metadata_tools,
    )

    # Create Feedback Analysis Agent (focused on search and content analysis) - identical to app.py
    feedback_analysis_agent = create_feedback_analysis_agent(
        search_tool=search_customer_feedback,
        handoff_agents=[output_summarizer],
    )

    # Create Chart Creator Agent (reads market mappings from Session Context)
    chart_creation_agent = create_chart_creator_agent(
        chart_creation_tool=create_chart_creation_tool(collection)
    )

    # Customer Manager with all specialized agents + metadata tools for market mapping
    customer_manager = create_customer_manager_agent(
        handoff_agents=[
            metadata_analysis_agent,  # Dedicated metadata expert
            feedback_analysis_agent,
            chart_creation_agent,
        ],
        metadata_tools=metadata_tools  # For Two-Step Handoff (Manager resolves markets before Chart Creator)
    )

    return customer_manager, collection


def limit_session_history(session, max_history: int | None = None):
    """
    Begrenzt die Session-Historie auf die letzten N Einträge.
    WICHTIG: Entfernt __CHART__ Marker aus History für Agent-Kontext!
    
    Args:
        session: SQLiteSession Objekt
        max_history: Maximale Anzahl Historie-Einträge (None = unbegrenzt)
    
    Returns:
        Session mit begrenzter Historie und bereinigten Responses
    """
    import re
    
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


async def process_query(customer_manager, user_input: str, session=None):
    """Process user query with enhanced functionality - returns result object for Streamlit rendering"""
    try:
        if session:
            # HISTORIE BEGRENZEN für Token-Optimierung
            session = limit_session_history(session, HISTORY_LIMIT)

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


def main():
    """Main Streamlit application."""

    # Page config
    st.set_page_config(
        page_title="Customer Feedback RAG Chat",
        page_icon="💬",
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

    if "system_initialized" not in st.session_state:
        with st.spinner("🔄 Initializing RAG system..."):
            try:
                customer_manager, collection = initialize_system(is_azure_openai=IS_AZURE_OPENAI)
                st.session_state.customer_manager = customer_manager
                st.session_state.collection = collection
                st.session_state.system_initialized = True
                st.info(
                    f"System initialized with {collection.count():,} documents in vectorstore"
                )
            except Exception as e:
                st.error(f"❌ Failed to initialize system: {e}")
                st.stop()

    # ============================================================================
    # SIDEBAR - Settings and Statistics
    # ============================================================================

    with st.sidebar:
        # Predefined example queries - moved to top
        st.subheader("💡 Example Queries")

        # Use globally defined example queries from configuration section
        for query in EXAMPLE_QUERIES:
            if st.button(query, key=f"sidebar_{query}", use_container_width=True):
                # Store query to be processed outside sidebar (in main area)
                st.session_state.pending_example_query = query
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
    
    # Chat container with all messages (static display)
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
                # ✅ Check for charts in history
                text_content, chart_path = extract_chart_path(response_text)
                st.markdown(text_content)
                
                # ✅ Render chart if found in history
                if chart_path:
                    chart_size = st.session_state.get('chart_size', 'Mittel')
                    render_chart(chart_path, size=chart_size)

# ============================================================================
# CHAT INPUT AT BOTTOM - Fixed position
# ============================================================================

    # Check for pending example query from sidebar (must be processed in main area)
    if "pending_example_query" in st.session_state:
        query = st.session_state.pending_example_query
        del st.session_state.pending_example_query
        process_user_query(query)

    # User input at the bottom of the page
    user_input = st.chat_input("Ask about customer feedback...")

    # Process chat input if provided (this adds to history internally)
    if user_input:
        # Use unified query processing function with direct chat integration
        process_user_query(user_input)

# ============================================================================
# FOOTER - Modular Footer with Live Statistics
# ============================================================================

    # Use modular footer component with cached stats
    stats = get_cached_conversation_stats()
    render_footer(stats)


if __name__ == "__main__":
    main()
