"""
🦶 Footer Styles - Sticky Footer mit Live-Statistiken

Responsive Footer-Komponente mit System-Status und Design-System.
Refactoriert für bessere Wartbarkeit und cleanes Design.
"""

import streamlit as st
from .theme_config import COLORS


def _generate_footer_css() -> str:
    """
    Generiert das CSS für den Footer mit Theme-Farben.

    Returns:
        str: CSS-Styles für den Footer
    """
    return f"""
    <style>
    .custom-footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: {COLORS["footer_bg"]};
        color: {COLORS["text_primary"]};
        text-align: center;
        padding: 12px 20px;
        font-size: 14px;
        z-index: 999;
        border-top: 1px solid {COLORS["border_default"]};
        backdrop-filter: blur(12px);
        box-shadow: 0 -2px 20px rgba(0, 0, 0, 0.3);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    .footer-main-content {{
        font-weight: 400;
        color: {COLORS["text_secondary"]};
        margin-bottom: 4px;
        opacity: 1.0;
    }}
    
    .footer-stats {{
        font-size: 12px;
        color: {COLORS["text_secondary"]};
        opacity: 0.6;
    }}
    
    .footer-stats .stat-item {{
        margin: 0 8px;
        display: inline-block;
    }}
    
    .footer-stats .stat-emoji {{
        color: {COLORS["text_secondary"]};
        margin-right: 4px;
    }}
    
    /* Abstand zum Footer für den Content */
    .main .block-container {{
        padding-bottom: 100px !important;
    }}
    
    /* Chat Input Container Anpassung */
    .stChatInput > div {{
        margin-bottom: 50px !important;
    }}
    
    /* Responsive Design */
    @media (max-width: 768px) {{
        .custom-footer {{
            padding: 10px 15px;
            font-size: 11px;
        }}
        
        .footer-stats .stat-item {{
            margin: 0 4px;
        }}
    }}
    </style>
    """


def _build_stats_content(history_stats: dict, chart_stats: dict | None = None) -> str:
    """
    Erstellt den Statistik-Content für den Footer.

    Args:
        history_stats: Dictionary mit Historie-Statistiken
        chart_stats: Dictionary mit Chart-Statistiken (optional)

    Returns:
        str: Formatierter HTML-Content für Statistiken
    """
    stats_items = [
        f'<span class="stat-item">Avg Input: {history_stats.get("avg_user_input_length", 0)} tokens</span>',
        f'<span class="stat-item">Avg Response: {history_stats.get("avg_response_length", 0)} tokens</span>',
    ]

    if chart_stats:
        stats_items.extend(
            [
                f'<span class="stat-item"><span class="stat-emoji">🎨</span>Charts: {chart_stats.get("count", 0)}</span>',
                f'<span class="stat-item"><span class="stat-emoji">💿</span>{chart_stats.get("total_size_mb", "0.0")} MB</span>',
            ]
        )

    return f'<div class="footer-stats">{"".join(stats_items)}</div>'


def render_footer(
    history_stats: dict,
    chart_stats: dict | None = None,
    custom_content: str | None = None,
) -> None:
    """
    Rendert einen sticky Footer mit Live-Statistiken und schwarzem Hintergrund.

    Args:
        history_stats: Dictionary mit Historie-Statistiken (total_interactions, session_id, etc.)
        chart_stats: Dictionary mit Chart-Statistiken (count, total_size_mb) - optional
        custom_content: Optional custom HTML content
    """

    # CSS generieren
    css = _generate_footer_css()

    # Content erstellen
    if custom_content is None:
        main_content = '<div class="footer-main-content">Powered by OpenAI (GPT-4o, GPT4o-mini) | ChromaDB Vector Store</div>'
        stats_content = _build_stats_content(history_stats, chart_stats)
        footer_content = f"{main_content}{stats_content}"
    else:
        footer_content = custom_content

    # Footer HTML zusammenbauen
    footer_html = f"""
    {css}
    <div class='custom-footer'>
        {footer_content}
    </div>
    """

    st.markdown(footer_html, unsafe_allow_html=True)


def render_simple_footer(message: str = "Customer Feedback Analysis System") -> None:
    """
    Einfacher Footer ohne Live-Statistiken.

    Args:
        message: Anzuzeigende Nachricht im Footer
    """
    # Leere Stats für einfachen Footer
    simple_stats = {
        "total_interactions": 0,
        "session_id": "",
        "agents_used": {},
        "avg_response_length": 0,
    }

    # Custom Content
    custom_content = f"""
    <div class="footer-main-content" style="opacity: 0.9; font-weight: 500;">
        {message}
    </div>
    """

    render_footer(simple_stats, None, custom_content)
