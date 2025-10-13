"""
📐 Layout Styles - Main Application Layout & Spacing

Hauptlayout-Styles für Container, Padding, Margins und allgemeine Spacing-Regeln.
"""

import streamlit as st


def apply_main_layout_styles() -> None:
    """
    Wendet die Hauptlayout-Styles für die Streamlit-App an.

    Features:
    - Reduziertes Top-Padding für mehr Platz
    - Optimiertes Spacing für Header-Bereiche
    - Footer-freundliches Bottom-Padding
    - Konsistente Margin-Regeln
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