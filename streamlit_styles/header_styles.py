"""
🏷️ Header Styles - Title, Subtitle, Typewriter Effect

Components for the main UI header of the Streamlit app.
"""

import streamlit as st
import time
from .theme_config import COLORS, TYPOGRAPHY


def render_main_title() -> None:
    """
    Renders the main application title with brand styling.

    Returns:
        None

    Features:
        - Text shadow for better readability
        - Accent color for "Analysis" keyword
        - Custom font for playful touch
        - Responsive sizing
        
    Notes:
        - Uses TYPOGRAPHY["accent_font"] for "Analysis" word
        - Applies COLORS["primary_accent"] turquoise color
        - Includes text shadow for depth effect
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
        ">Analyse</span> 
        Chat
    </h1>
    """

    st.markdown(title_html, unsafe_allow_html=True)


def render_subtitle_with_typewriter(
    text: str = "Frage mich alles zu deinen customer feedback Daten!",
    speed: float = 0.05,
    session_key: str = "typewriter_complete",
) -> None:
    """
    Renders a subtitle with typewriter effect (once per session).

    Args:
        text (str): Text for the typewriter effect. Defaults to
                   "Ask me anything about your customer feedback data!"
        speed (float): Typing speed in seconds per character. Defaults to 0.05
        session_key (str): Session state key for completion tracking.
                          Defaults to "typewriter_complete"

    Returns:
        None
        
    Notes:
        - Typewriter effect runs only once per session
        - Uses session_state to track completion status
        - Shows blinking cursor ("|") during typing
        - Removes cursor after completion
        - Subsequent renders show final text immediately
        - Uses COLORS["text_secondary"] for subtitle color
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
    Renders complete header section with title and subtitle.
    
    Returns:
        None
        
    Notes:
        - Convenience function for easy usage
        - Combines render_main_title() and render_subtitle_with_typewriter()
        - Uses default parameters for subtitle
        - Ideal for standard header display
    """
    render_main_title()
    render_subtitle_with_typewriter()
