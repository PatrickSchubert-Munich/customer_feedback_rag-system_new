"""
🎨 Theme Configuration - Color Palette, Layout, Typography

Zentralisierte Design-Tokens für die Customer Feedback Analysis App.
Basiert auf GitHub's Dark Theme mit Custom Accents.
"""

# ============================================================================
# COLOR PALETTE
# ============================================================================

COLORS = {
    # Primary Brand Colors
    "primary_accent": "#4ECDC4",  # Turquoise
    "secondary_accent": "#45B7AB",
    # GitHub Dark Theme Colors
    "text_primary": "#f0f6fc",
    "text_secondary": "#8b949e",
    "text_muted": "#656d76",
    # Background Colors
    "bg_primary": "#0d1117",
    "bg_secondary": "#161b22",
    "bg_tertiary": "#21262d",
    # Border & Divider
    "border_default": "#30363d",
    "border_muted": "#21262d",
    # Status Colors
    "success": "#238636",
    "warning": "#d29922",
    "error": "#da3633",
    "info": "#1f6feb",
    # Footer
    "footer_bg": "rgba(14, 17, 23, 0.95)",
    "footer_text": "#8b949e",
}

# ============================================================================
# LAYOUT CONFIGURATION
# ============================================================================

LAYOUT = {
    # Chart Sizes (Column Ratios)
    "chart_sizes": {
        "Klein": [2, 2, 2],  # 33% Breite
        "Mittel": [1, 3, 1],  # 60% Breite (Standard)
        "Groß": [1, 5, 1],  # 71% Breite
    },
    # Spacing
    "footer_height": "80px",
    "chat_input_margin": "60px",
    # Z-Index
    "footer_z_index": 999,
}

# ============================================================================
# TYPOGRAPHY
# ============================================================================

TYPOGRAPHY = {
    # Font Families
    "accent_font": "'Comic Sans MS', cursive, sans-serif",
    "default_font": "system-ui, -apple-system, sans-serif",
    # Font Sizes
    "title_size": "2.5rem",
    "subtitle_size": "1.5rem",
    "footer_size": "12px",
    # Text Shadows
    "text_shadow_light": "0px 1px 2px rgba(0,0,0,0.1)",
    "text_shadow_medium": "0px 2px 4px rgba(0,0,0,0.15)",
}
