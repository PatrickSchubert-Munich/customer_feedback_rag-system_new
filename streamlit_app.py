#!/usr/bin/env python3
"""
Streamlit Chat UI für Customer Feedback RAG System.
Identical functionality to app.py with clean main() structure.
"""

import streamlit as st
import asyncio
import time
from agents import SQLiteSession
from dotenv import load_dotenv

# Import existing system components - identical to app.py
from agents import Runner
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
    load_csv,
    load_vectorstore,
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
VECTORSTORE_TYPE = "chroma"


def render_native_response(result):
    """Rendert die native SDK Response als Streamlit-Komponenten - optimiert für UI"""
    if not hasattr(result, "final_output"):
        return False
    final_output = str(result.final_output)

    # Prüfe ob es vom Output Summarizer kommt (enthält typische Markdown-Strukturen)
    if (
        "Executive Summary" in final_output
        or "Key Insights" in final_output
        or "Handlungsempfehlungen" in final_output
    ):
        render_structured_summary(final_output)
        return True
    else:
        # Unbekanntes Format: nichts rendern; Aufrufer streamt Text
        return False


def render_structured_summary(summary):
    """Rendert die benutzerfreundliche Textausgabe des Output Summarizer Agents direkt"""
    # Der Agent gibt jetzt bereits formatierte, benutzerfreundliche Markdown-Ausgaben
    st.markdown(str(summary))


def get_raw_response_text(result):
    """Extrahiert den rohen Response-Text für Conversation Tracking"""
    return str(result.final_output) if hasattr(result, "final_output") else str(result)


def ensure_session_initialized():
    """Stellt sicher, dass die Session initialisiert ist. Wiederverwendbare Funktion."""
    if "session" not in st.session_state:
        st.session_state.session = SQLiteSession(
            "streamlit_feedback_session", "streamlit_conversation_history.db"
        )
    return st.session_state.session


@st.cache_data(ttl=1)  # Cache for 1 second to reduce multiple calls in same render
def get_cached_conversation_stats():
    """Cached wrapper für conversation stats um multiple API-Calls zu vermeiden."""
    return st.session_state.conversation.get_summary_stats()


def process_user_query(user_input: str) -> None:
    """
    Verarbeitet eine Benutzereingabe mit Live-Streaming der neuen Antwort.
    """
    # Ensure session is initialized
    session = ensure_session_initialized()

    # 1. User-Nachricht anzeigen
    with st.chat_message("user"):
        st.write(user_input)

    # 2. Assistant-Nachricht mit Streaming
    with st.chat_message("assistant"):
        # Thinking-Status anzeigen
        thinking_placeholder = st.empty()
        thinking_placeholder.write("🤔 **Thinking...**")

        # Backend-Verarbeitung
        result = asyncio.run(
            process_query(st.session_state.customer_manager, user_input, session)
        )

        # Thinking-Status entfernen
        thinking_placeholder.empty()

        # Response verarbeiten und streamen
        if isinstance(result, dict) and "error" in result:
            raw_response = f"Error: {result['error']}"
            st.write_stream(stream_response(
                f"❌ **ERROR:** {result['error']}\n\n**Error Type:** {result.get('error_type', 'Unknown')}"
            ))
        else:
            raw_response = get_raw_response_text(result)

            # Versuche strukturierte Darstellung - falls nicht möglich, streame Text
            is_structured_rendered = render_native_response(result)

            # Wenn keine strukturierte Darstellung möglich war, streame Text
            if not is_structured_rendered:
                st.write_stream(stream_response(f"**Customer Manager:**\n\n{raw_response}"))
                

    # Add to conversation history
    st.session_state.conversation.add_interaction(
        user_input=user_input,
        agent_response=raw_response,
        agent_name="Customer Manager",
    )

    # Show stats as toast
    fresh_stats = st.session_state.conversation.get_summary_stats()
    st.toast(
        f"💬 Conversation: {fresh_stats['total_interactions']} interactions | Session: {fresh_stats['session_id']}",
        icon="📊",
    )

    # Mark that we just processed a query (to avoid showing it twice in history)
    st.session_state.just_processed_query = True


def stream_response(response: str, delay: float = 0.05):
    """
    Streamt Text Zeichen für Zeichen für eine natürliche Anzeige.

    Args:
        text: Der zu streamende Text
        delay: Delay zwischen Zeichen in Sekunden
    """
    for word in response.split():
        yield word + " "
        time.sleep(delay)


@st.cache_resource(show_spinner=False)
def initialize_system():
    """Initialize the RAG system components - identical structure to app.py main()"""

    # Initialize OpenAI client FIRST (required for VectorStore) - identical to app.py
    azure_client = get_azure_openai_client()
    if azure_client is None:
        st.error("❌ Azure OpenAI Client konnte nicht initialisiert werden!")
        st.stop()

    # Load data and tools - identical to app.py
    customer_data = load_csv(path=FILE_PATH_CSV, write_local=False)

    # Log loaded data count
    collection = load_vectorstore(
        data=customer_data, type=VECTORSTORE_TYPE, create_new_store=False
    )

    # VALIDIERUNG: VectorStore muss Daten enthalten - identical to app.py
    if collection is None:
        st.error("❌ VectorStore collection is None!")
        st.stop()
    if collection.count() == 0:
        st.error("❌ VectorStore is empty!")
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


async def process_query(customer_manager, user_input: str, session=None):
    """Process user query with enhanced functionality - returns result object for Streamlit rendering"""
    try:
        if session:
            # Session-aware execution with automatic history management and enhanced tracing - identical to app.py
            from agents import trace

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
                customer_manager, collection = initialize_system()
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

        example_queries = [
            "Welche Märkte gibt es?",
            "Wie ist die NPS-Verteilung?",
            "Top 5 Kundenbeschwerden?",
            "Negative Feedbacks analysieren",
            "Sentiment der Promoter?",
        ]

        for query in example_queries:
            if st.button(query, key=f"sidebar_{query}", use_container_width=True):
                # Set query in session state for processing in main area
                st.session_state.pending_query = query

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

    # Main chat interface - now full width
    # Display conversation history (exclude the currently processed query to avoid duplicates)
    history = st.session_state.conversation.get_history()

    # Exclude the last entry if we just processed a query
    if (
        hasattr(st.session_state, "just_processed_query")
        and st.session_state.just_processed_query
    ):
        history = history[:-1]  # Exclude the latest entry
        st.session_state.just_processed_query = False

    # Chat container with fixed height and scrolling
    chat_container = st.container()

    with chat_container:
        for i, entry in enumerate(history):
            with st.chat_message(name="user", avatar="🧑"):
                st.write(f"{entry['user']}")

            with st.chat_message(name="assistant", avatar="🤖"):
                # Display response in a clean format
                if entry["response"].startswith("Error:"):
                    st.error(entry["response"])
                else:
                    # Prüfe ob es eine strukturierte Summarizer-Antwort ist
                    response_text = entry["response"]
                    if (
                        "executive_summary=" in response_text
                        and "key_insights=" in response_text
                    ):
                        # Das ist eine UserFriendlySummary - zeige direkt an
                        st.write(response_text)
                    else:
                        # Normale Textantwort
                        if len(response_text) > 500:
                            st.write(response_text[:500] + "...")
                            with st.expander("Show full response"):
                                st.write(response_text)
                        else:
                            st.write(response_text)

    # ============================================================================
    # PROCESS PENDING QUERIES FROM SIDEBAR
    # ============================================================================

    # Check for pending query from Example Query buttons
    if hasattr(st.session_state, "pending_query"):
        query = st.session_state.pending_query
        delattr(st.session_state, "pending_query")
        # Process in main area (not sidebar)
        process_user_query(query)

    # ============================================================================
    # CHAT INPUT AT BOTTOM - Fixed position
    # ============================================================================

    # User input at the bottom of the page
    user_input = st.chat_input("Ask about customer feedback...")

    # Process chat input if provided
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
