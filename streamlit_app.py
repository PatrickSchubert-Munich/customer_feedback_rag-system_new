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
    "Top 5 Kundenbeschwerden?",
    "Analysiere negative Feedbacks",
    "Sentiment der Promoter?",
]

# Removed render_native_response and render_structured_summary functions
# All responses are now handled uniformly with streaming

def ensure_session_initialized():
    """Stellt sicher, dass die Session initialisiert ist. Wiederverwendbare Funktion."""
    if "session" not in st.session_state:
        st.session_state.session = SQLiteSession(
            "streamlit_feedback_session", 
            "streamlit_conversation_history.db"
        )
    return st.session_state.session


@st.cache_data(ttl=1)  # Cache for 1 second to reduce multiple calls in same render
def get_cached_conversation_stats():
    """Cached wrapper für conversation stats um multiple API-Calls zu vermeiden."""
    return st.session_state.conversation.get_summary_stats()


def stream_response(response: str, delay: float = 0.05):
    """
    Streamt Text wortweise für natürliche Anzeige mit Streamlit.
    
    Args:
        response: Der zu streamende Text
        delay: Delay zwischen Wörtern in Sekunden (schneller für bessere UX)
    """
    response = response.copy()
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
        if isinstance(response, dict) and "error" in response:
            # Handle error case
            error_message = f"**ERROR ({response.get('error_type', 'Unknown')}):** {response['error']}"
            placeholder.error(error_message)
            response_content = error_message
        else:
            # Handle success case - result has final_output attribute
            raw_response = str(response.final_output) # type: ignore
        
            # Stream response to user
            full_response = placeholder.write_stream(stream_response(raw_response))
            
            # Extract response content from stream
            response_content = (full_response 
                if isinstance(full_response, str) 
                else "".join(str(chunk) for chunk in full_response)
            )
        
        # Always add to conversation history (both success and error cases)
        # Note: Agent name is "Assistant" as responses may come from various specialized agents
        st.session_state.conversation.add_interaction(
            user_input=user_input,
            agent_response=response_content,
            agent_name="Assistant")


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

    # Create Sentiment Analysis Agent - identical to app.py
    chart_creation_agent = create_chart_creator_agent(
        chart_creation_tool=create_chart_creation_tool(collection)
    )

    # Customer Manager with all specialized agents - identical to app.py
    customer_manager = create_customer_manager_agent(
        handoff_agents=[
            metadata_analysis_agent,  # NEW: Dedicated metadata expert
            feedback_analysis_agent,
            chart_creation_agent,
        ]
    )

    return customer_manager, collection


def limit_session_history(session, max_history: int | None = None):
    """
    Begrenzt die Session-Historie auf die letzten N Einträge.
    
    Args:
        session: SQLiteSession Objekt
        max_history: Maximale Anzahl Historie-Einträge (None = unbegrenzt)
    
    Returns:
        Session mit begrenzter Historie (oder Original wenn nicht begrenzt)
    """
    if max_history is None or max_history <= 0:
        return session
    
    try:
        # Hole aktuelle Historie
        history = session.get_history()
        
        # Wenn Historie zu lang ist, behalte nur die letzten N Einträge
        if len(history) > max_history:
            # Lösche ältere Einträge aus der Datenbank
            entries_to_keep = history[-max_history:]
            
            # Erstelle neue Session mit begrenzter Historie
            # (Die alte Session wird intern begrenzt)
            session.set_history(entries_to_keep)
            
    except (AttributeError, Exception) as e:
        # Falls Session keine History-Methoden hat, gib Original zurück
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
                # Process example query directly and trigger rerun
                process_user_query(query)
                st.rerun()

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
    # CHAT INPUT AT BOTTOM - Fixed position
    # ============================================================================

    # User input at the bottom of the page
    user_input = st.chat_input("Ask about customer feedback...")

    # Process chat input if provided (this adds to history internally)
    if user_input:
        # Use unified query processing function with direct chat integration
        process_user_query(user_input)

    # ============================================================================
    # CHAT HISTORY DISPLAY - Shows all previous messages
    # ============================================================================
    
    # Load history AFTER potential processing to include new messages
    history = st.session_state.conversation.get_history()
    
    # Chat container with all messages (static display)
    chat_container = st.container()

    with chat_container:
        for _ , entry in enumerate(history):
            # User message
            with st.chat_message(name="user", avatar="🧑"):
                st.write(entry["user"])

            # Assistant response
            with st.chat_message(name="assistant", avatar="🤖"):
                response_text = entry["response"]
                if response_text.startswith("❌ **ERROR:**"):
                    st.error(response_text)
                else:
                    st.markdown(response_text)

    # ============================================================================
    # FOOTER - Modular Footer with Live Statistics
    # ============================================================================

    # Use modular footer component with cached stats
    stats = get_cached_conversation_stats()
    render_footer(stats)


if __name__ == "__main__":
    main()
