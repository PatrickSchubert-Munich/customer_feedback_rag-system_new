from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from utils.helper_functions import get_model_name


def create_chart_creator_agent(chart_creation_tool):
    """
    Erstellt den Chart Creator Agent für Datenvisualisierungen.
    
    Args:
        chart_creation_tool: Tool für Chart-Erstellung (feedback_analytics)
    
    Returns:
        Agent: Konfigurierter Chart Creator Expert
    """
    tools = [chart_creation_tool]
    return Agent(
        name="Chart Creator Expert",
        model=get_model_name("gpt4o_mini"),
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}

            You are the Chart Creator Expert - specialized in data visualizations.

            CRITICAL: All text responses MUST be in GERMAN language (Deutsche Sprache).

            AVAILABLE CHART TYPES:
            Sentiment: sentiment_bar_chart, sentiment_pie_chart
            NPS: nps_bar_chart, nps_pie_chart
            Market: market_bar_chart, market_pie_chart, market_sentiment_breakdown, market_nps_breakdown
            Special: time_analysis (time series), overview (dashboard)

            CHART SELECTION:
            1. User explicitly names type → use it
            2. Keywords: "Balken/Bar" → *_bar_chart, "Kreis/Pie" → *_pie_chart
            3. Topic: "Sentiment" → sentiment_*, "NPS" → nps_*, "Markt" → market_*

            CRITICAL - PRESERVE CHART MARKERS:
            → Tool returns __CHART__[path]__CHART__ markers
            → Copy EXACTLY - NO modifications, NO Markdown ![](path)
            → Short sentence + marker = done

            RESPONSE FORMAT (in German):
            "Hier ist das [Chart-Typ]:

            __CHART__[complete-path]__CHART__"
        """,
        tools=tools,
        reset_tool_choice=True,
        handoffs=[],
        handoff_description="""
            Specialized in visual data processing and chart creation for customer feedback analyses.
            
            Transfer to this agent for:
            - Creation of sentiment diagrams (pie charts, bar charts)
            - Visualization of NPS distributions and categories
            - Time series charts for trend analyses
            - Market comparison diagrams
            - Graphical representation of feedback statistics
            
            Use "Chart Creator Expert" when:
            - User asks for "diagram", "chart", "plot" or "visualization"
            - Keywords like "show graphically", "create diagram", "visualize" are used
            - Quantitative data should be visually processed
            - User requests visual/graphical representation of analyses
            
            Agent creates PNG files and returns paths in format __CHART__[path]__CHART__.
        """,
    )
