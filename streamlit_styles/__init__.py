"""
Streamlit Styles Package - Modular UI Components

Provides theme configuration, header styles, footer styles, sidebar styles,
and layout styles for the Customer Feedback Analysis Streamlit App.
"""

from .theme_config import COLORS, LAYOUT, TYPOGRAPHY
from .header_styles import (
    render_main_title,
    render_subtitle_with_typewriter,
    render_header_section,
)
from .footer_styles import render_footer, render_simple_footer
from .layout_styles import apply_main_layout_styles
from .sidebar_styles import render_sidebar_content

__all__ = [
    "COLORS",
    "LAYOUT",
    "TYPOGRAPHY",
    "render_main_title",
    "render_subtitle_with_typewriter",
    "render_header_section",
    "render_footer",
    "render_simple_footer",
    "apply_main_layout_styles",
    "render_sidebar_content",
]
