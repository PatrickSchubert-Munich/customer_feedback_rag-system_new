"""
📊 Sidebar Styles - Sidebar Components and Rendering

Components for the sidebar including example queries, chart settings,
export options, system info, and agent information.
"""

import streamlit as st
from typing import List, Dict, Any, Optional


def render_example_queries(example_queries: List[str]) -> None:
    """
    Renders example query buttons in the sidebar.
    
    Args:
        example_queries (List[str]): List of example query strings to display as buttons
        
    Returns:
        None
        
    Features:
        - Full-width buttons for each query
        - Sets pending_query in session state when clicked
        - Triggers rerun for immediate query execution
    """
    st.subheader("💡 Beispiel-Fragen")
    
    for query in example_queries:
        if st.button(query, key=f"sidebar_{query}", use_container_width=True):
            st.session_state.pending_query = query
            st.rerun()


def render_chart_size_selector() -> None:
    """
    Renders chart size radio button selector and auto-delete checkbox in the sidebar.
    
    Returns:
        None
        
    Features:
        - Radio buttons with three size options: Klein, Mittel, Groß
        - Horizontal layout for compact display
        - Persists selection in session state as 'chart_size'
        - Default selection is 'Mittel'
        - Auto-delete checkbox for automatic cleanup of old charts (60 min)
        - Checkbox state saved in session state as 'auto_delete_charts'
    """
    st.subheader("📊 Chart-Größe")
    
    chart_size = st.radio(
        "Größe wählen",
        options=["Klein", "Mittel", "Groß"],
        index=1 if st.session_state.get('chart_size', 'Mittel') == 'Mittel' 
              else (0 if st.session_state.get('chart_size', 'Mittel') == 'Klein' else 2),
        label_visibility="collapsed",
        horizontal=True
    )
    st.session_state['chart_size'] = chart_size
    
    # Auto-delete charts checkbox with unique key for proper state management
    st.checkbox(
        "🗑️ Charts nach 60 min. automatisch löschen",
        value=False,
        key='auto_delete_charts',
        help="Alte Chart-Dateien werden automatisch nach 60 Minuten gelöscht, um Speicherplatz zu sparen"
    )


def render_export_options(get_stats_callback) -> None:
    """
    Renders export and history management options in the sidebar.
    
    Args:
        get_stats_callback (callable): Function to retrieve conversation statistics
        
    Returns:
        None
        
    Features:
        - Export conversation as text file
        - Download button for text export
        - Clear history button with immediate rerun
        - Warning if no conversation exists
    """
    st.subheader("📄 Export-Optionen")
    
    if st.button("📋 Als Text exportieren", use_container_width=True):
        if st.session_state.conversation.get_conversation_count() > 0:
            export_stats = get_stats_callback()
            export_text = st.session_state.conversation.export_history("text")
            st.download_button(
                "💾 Text herunterladen",
                export_text,
                file_name=f"conversation_{export_stats['session_id']}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        else:
            st.warning("Keine Konversation zum Exportieren vorhanden")
    
    if st.button("🧹 Historie löschen", use_container_width=True):
        st.session_state.conversation.clear_history()
        st.rerun()


def render_system_info(document_count: int) -> None:
    """
    Renders system information in the sidebar.
    
    Args:
        document_count (int): Number of documents in the vector store
        
    Returns:
        None
        
    Features:
        - Displays document count with thousand separators
    """
    st.subheader("📈 System-Info")
    st.info(f"Dokumente: {document_count:,}")


def render_history_limit_caption(history_limit: Optional[int] = None) -> None:
    """
    Renders history limit information as caption below agent info.
    
    Args:
        history_limit (int, optional): History limit for conversation context. 
                                       None means unlimited. Defaults to None.
        
    Returns:
        None
        
    Features:
        - Shows history limit status with icon indicators
        - Warning for unlimited history (higher token costs)
        - Rendered as small caption text
    """
    if history_limit:
        st.caption(f"💡 Historie-Limit: {history_limit} Turns (spart Token-Kosten)")
    else:
        st.caption("⚠️ Historie unbegrenzt (höhere Token-Kosten)")


def render_agent_info_expander() -> None:
    """
    Renders expandable agent information section in the sidebar.
    
    Returns:
        None
        
    Features:
        - Collapsible expander with info icon
        - Descriptions of three main agents:
          * Customer Manager (coordination)
          * Feedback Analysis Expert (semantic search)
          * Chart Creator Expert (visualizations)
        - Bullet-point format for quick readability
    """
    with st.expander("ℹ️ Verfügbare Agenten"):
        st.markdown("""
        **Customer Manager:**
        - Koordiniert alle Anfragen und wählt den passenden Spezialisten
        - Entscheidet zwischen Metadata-, Feedback- oder Chart-Analysen
        - Fasst Ergebnisse zusammen und liefert finale Antworten
        
        **Feedback Analysis Expert:**
        - Analysiert Kundenfeedback mit semantischer Suche
        - Filtert nach NPS, Sentiment, Markt, Topic und Autohaus
        - Liefert detaillierte Insights aus der Vektor-Datenbank
        
        **Chart Creator Expert:**
        - Erstellt aussagekräftige Visualisierungen
        - Unterstützt 13+ Chart-Typen (Bar, Pie, Time-Series, etc.)
        - Generiert automatisch optimierte Datenvisualisierungen
        """)


def render_conversation_summary(stats: Dict[str, Any]) -> None:
    """
    Renders conversation statistics summary in the sidebar.
    
    Args:
        stats (Dict[str, Any]): Dictionary containing conversation statistics with keys:
            - total_interactions (int): Number of conversation turns
            - avg_user_input_length (int): Average user input in tokens
            - avg_response_length (int): Average response in tokens
            - agents_used (dict): Dictionary mapping agent names to usage counts
            
    Returns:
        None
        
    Features:
        - Shows total interaction count (even if 0)
        - Displays average token counts for input and responses
        - Lists ALL three agents with call counts (shows 0x if not used)
        - Indented bullet-point format for agent list
        - Always visible for transparency
        - Consistent layout (no jumping when agents are first used)
    """
    st.divider()
    st.subheader("📊 Konversations-Zusammenfassung")
    st.write(f"Interaktionen: {stats.get('total_interactions', 0)}")
    
    # Show averages (0 if no interactions yet)
    avg_input = stats.get('avg_user_input_length', 0)
    avg_response = stats.get('avg_response_length', 0)
    st.write(f"Avg. Eingabe: {avg_input} Tokens")
    st.write(f"Avg. Antwort: {avg_response} Tokens")
    
    # Show all agents (always display all three with counts)
    st.write("**Verwendete Agenten:**")
    agents_used = stats.get('agents_used', {})
    
    # Define all three agents with their display order
    all_agents = [
        "Customer Manager",
        "Feedback Analysis Expert",
        "Chart Creator Expert"
    ]
    
    # Display each agent with their count (0 if not used)
    for agent in all_agents:
        count = agents_used.get(agent, 0)
        st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;• {agent}: {count}x", unsafe_allow_html=True)


def render_sidebar_content(
    example_queries: List[str],
    get_stats_callback,
    document_count: int,
    history_limit: Optional[int] = None
) -> None:
    """
    Main function to render complete sidebar content.
    
    Args:
        example_queries (List[str]): List of example query strings
        get_stats_callback (callable): Function to retrieve conversation statistics
        document_count (int): Number of documents in vector store
        history_limit (int, optional): History limit for conversation. Defaults to None.
        
    Returns:
        None
        
    Features:
        - Renders all sidebar components in proper order
        - Adds dividers between sections for visual separation
        - Handles conversation stats dynamically
        
    Component Order:
        1. Example Queries
        2. Chart Size Selector
        3. Export Options
        4. System Info (Documents)
        5. Agent Information (expandable)
        6. History Limit Caption
        7. Conversation Summary (always visible)
    """
    # Example Queries Section
    render_example_queries(example_queries)
    st.divider()
    
    # Chart Size Selector
    render_chart_size_selector()
    st.divider()
    
    # Export Options
    render_export_options(get_stats_callback)
    st.divider()
    
    # System Info (Documents only)
    render_system_info(document_count)
    
    # Agent Information Expander
    render_agent_info_expander()
    
    # History Limit Caption (below agents)
    render_history_limit_caption(history_limit)
    
    # Conversation Statistics (always visible)
    stats = get_stats_callback()
    render_conversation_summary(stats)
