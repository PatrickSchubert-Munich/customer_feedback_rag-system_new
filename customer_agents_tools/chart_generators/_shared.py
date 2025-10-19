"""
Shared utilities for chart generators.

Contains common functions, imports, and constants used across all chart types.
"""

import os
import sys
from datetime import datetime
import matplotlib

# CRITICAL: Set non-interactive backend BEFORE importing pyplot
# This must be executed before any chart module imports matplotlib.pyplot
matplotlib.use("Agg")

# Now safe to import pyplot
import matplotlib.pyplot as plt


def get_chart_path(chart_name: str) -> str:
    """
    Creates unique chart path with timestamp.

    Args:
        chart_name (str): Base name for chart file (e.g. "sentiment_bar", "nps_pie").

    Returns:
        str: Absolute path to chart file in charts/ directory.
            Format: "charts/{chart_name}_{timestamp}.png"
            Example: "charts/sentiment_bar_20231015_143022_12.png"

    Notes:
        - Uses ABSOLUTE path for secure Streamlit display
        - Timestamp format: YYYYMMDD_HHMMSS_MS (17 chars)
        - Auto-creates charts/ directory if not exists
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:17]
    chart_filename = f"{chart_name}_{timestamp}.png"

    chart_dir = "charts"
    os.makedirs(chart_dir, exist_ok=True)

    # ✅ Use os.path.join for OS-independent path
    chart_path = os.path.join(chart_dir, chart_filename)
    
    # ✅ CRITICAL: Convert to ABSOLUTE path for Streamlit
    chart_path = os.path.abspath(chart_path)

    # ✅ CRITICAL: Convert to Forward Slashes for Streamlit/Web
    chart_path = chart_path.replace("\\", "/")

    return chart_path
