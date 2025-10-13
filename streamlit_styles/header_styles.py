"""
🏷️ Header Styles - Title, Subtitle, Typewriter Effect

Komponenten für die Haupt-UI-Header der Streamlit App.
"""

import streamlit as st
import time
from .theme_config import COLORS, TYPOGRAPHY


def render_main_title() -> None:
    """
    Rendert den Haupttitel der Anwendung mit Brand-Styling.

    Features:
    - Text Shadow für bessere Lesbarkeit
    - Accent Color für "Analysis"
    - Custom Font für spielerischen Touch
    """
    title_html = f"""
    <h1 style="
        text-shadow: {TYPOGRAPHY["text_shadow_light"]};
        margin-bottom: 0;
    ">
        🎧 Customer Feedback 
        <span style="
            font-family: {TYPOGRAPHY["accent_font"]};
            color: {COLORS["primary_accent"]};
        ">Analysis</span> 
        Chat
    </h1>
    """

    st.markdown(title_html, unsafe_allow_html=True)


def render_subtitle_with_typewriter(
    text: str = "Ask me anything about your customer feedback data!",
    speed: float = 0.05,
    session_key: str = "typewriter_complete",
) -> None:
    """
    Rendert einen Untertitel mit Typewriter-Effekt (einmalig pro Session).

    Args:
        text: Text für den Typewriter-Effekt
        speed: Geschwindigkeit des Tippens (Sekunden pro Zeichen)
        session_key: Session State Key für Completion-Tracking
    """
    # Prüfe ob Typewriter-Effekt bereits abgeschlossen
    if session_key not in st.session_state:
        st.session_state[session_key] = False

    subtitle_style = f"""
    color: {COLORS["text_secondary"]};
    text-shadow: {TYPOGRAPHY["text_shadow_light"]};
    margin-top: 0;
    """

    if not st.session_state[session_key]:
        # Typewriter-Effekt
        placeholder = st.empty()

        for i in range(len(text) + 1):
            typing_text = f"""
            <h3 style="{subtitle_style}">
                {text[:i]}|
            </h3>
            """
            placeholder.markdown(typing_text, unsafe_allow_html=True)
            time.sleep(speed)

        # Entferne Cursor am Ende
        final_text = f"""
        <h3 style="{subtitle_style}">
            {text}
        </h3>
        """
        placeholder.markdown(final_text, unsafe_allow_html=True)

        # Markiere als abgeschlossen
        st.session_state[session_key] = True

    else:
        # Zeige finalen Text ohne Animation
        final_text = f"""
        <h3 style="{subtitle_style}">
            {text}
        </h3>
        """
        st.markdown(final_text, unsafe_allow_html=True)


def render_header_section() -> None:
    """
    Komplette Header-Sektion mit Title + Subtitle.
    Convenience-Funktion für einfache Nutzung.
    """
    render_main_title()
    render_subtitle_with_typewriter()
