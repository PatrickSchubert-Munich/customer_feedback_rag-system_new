"""
Chart Generators Package

Modular chart generation functions organized by chart category.
Each module handles a specific type of visualization.
"""

# Sentiment Charts
from .sentiment_charts import (
    create_sentiment_bar_chart,
    create_sentiment_pie_chart
)

# NPS Charts
from .nps_charts import (
    create_nps_bar_chart,
    create_nps_pie_chart
)

# Market Charts
from .market_charts import (
    create_market_bar_chart,
    create_market_pie_chart,
    create_market_sentiment_breakdown,
    create_market_nps_breakdown
)

# Topic Charts
from .topic_charts import (
    create_topic_bar_chart,
    create_topic_pie_chart
)

# Dealership Charts
from .dealership_charts import (
    analyze_dealerships,
    create_dealership_bar_chart
)

# Time Analysis
from .time_analysis_chart import create_time_analysis

# Overview Dashboard
from .overview_chart import create_overview_charts

__all__ = [
    # Sentiment
    "create_sentiment_bar_chart",
    "create_sentiment_pie_chart",
    # NPS
    "create_nps_bar_chart",
    "create_nps_pie_chart",
    # Market
    "create_market_bar_chart",
    "create_market_pie_chart",
    "create_market_sentiment_breakdown",
    "create_market_nps_breakdown",
    # Topic
    "create_topic_bar_chart",
    "create_topic_pie_chart",
    # Dealership
    "analyze_dealerships",
    "create_dealership_bar_chart",
    # Special
    "create_time_analysis",
    "create_overview_charts",
]
