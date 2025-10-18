"""
📐 Layout Styles - Main Application Layout & Spacing

Main layout styles for containers, padding, margins, and general spacing rules.
"""

import streamlit as st


def apply_main_layout_styles() -> None:
    """
    Applies main layout styles to the Streamlit app.

    Returns:
        None

    Features:
        - Reduced top padding for more viewport space
        - Optimized spacing for header areas
        - Footer-friendly bottom padding
        - Consistent margin rules
        - Responsive side padding
        
    Notes:
        - Sets transparent app header background
        - Adjusts block-container padding (top: 1rem, bottom: 0, sides: 5rem)
        - Removes default margins from h1 and h3 elements
        - Reduces hr (divider) spacing to 1rem
        - Should be called early in app initialization
    """
    st.markdown(
        """
    <style>
            /* Remove top margin */
            .stAppHeader {
                background-color: rgba(255, 255, 255, 0.0);  /* Transparent bg */
                visibility: visible;  /* Ensure the header is visible */
            }

            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                padding-left: 5rem;
                padding-right: 5rem;
            }
    
            /* Reduce spacing in header section */
            .main h1 {
                margin-top: 0 !important;
                padding-top: 0 !important;
            }
            
            .main h3 {
                margin-top: 0.5rem !important;
            }
            
            /* Adjust divider spacing */
            hr {
                margin: 1rem 0 !important;
            }
    </style>
    """,
        unsafe_allow_html=True,
    )