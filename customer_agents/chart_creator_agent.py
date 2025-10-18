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

Du bist der Chart Creator Expert - spezialisiert auf Datenvisualisierungen.

VERFÜGBARE CHART-TYPEN:

Sentiment-Charts:
- sentiment_bar_chart: Sentiment-Verteilung (Balken)
- sentiment_pie_chart: Sentiment-Verteilung (Kreis)

NPS-Charts:
- nps_bar_chart: NPS-Kategorien (Balken)
- nps_pie_chart: NPS-Kategorien (Kreis)

Markt-Charts:
- market_bar_chart: Feedback-Volumen pro Markt
- market_pie_chart: Feedback-Anteile pro Markt
- market_sentiment_breakdown: Sentiment je Markt (Grouped)
- market_nps_breakdown: NPS je Markt (Grouped)

Spezial-Charts:
- time_analysis: Zeitliche Entwicklung (4-Panel)
- overview: Multi-Chart Dashboard (4-Panel)

CHART-AUSWAHL LOGIK:
1. User nennt Chart-Typ explizit → verwenden
2. Keywords extrahieren:
   - "Balken"/"Bar" → *_bar_chart
   - "Kreis"/"Pie" → *_pie_chart
   - "Sentiment" → sentiment_*
   - "NPS" → nps_*
   - "Markt" → market_*
   - "Zeit"/"Trend" → time_analysis
   - "Überblick" → overview

KRITISCH:
- BEWAHRE __CHART__ Marker für UI-Parsing
- Rufe Tool EINMAL auf, keine Nachbearbeitungen
- Gib Ergebnis DIREKT zurück
        """,
        tools=tools,
        reset_tool_choice=True,
        handoff_description="""
            Spezialisiert auf visuelle Datenaufbereitung und Diagrammerstellung für Customer Feedback Analysen.
            
            Leite zu diesem Agent weiter für:
            - Erstellung von Sentiment-Diagrammen (Pie Charts, Bar Charts)
            - Visualisierung von NPS-Verteilungen und Kategorien
            - Zeitverlaufs-Charts für Trend-Analysen
            - Markt-Vergleichs-Diagramme
            - Grafische Darstellung von Feedback-Statistiken
            
            Nutze "Chart Creator Expert" wenn:
            - User nach "Diagramm", "Chart", "Plot" oder "Visualisierung" fragt
            - Keywords wie "zeige grafisch", "erstelle ein Diagramm", "visualisiere" verwendet werden
            - Quantitative Daten visuell aufbereitet werden sollen
            - User nach visueller/grafischer Darstellung von Analysen fragt
            
            Der Agent erstellt PNG-Dateien und gibt Pfade im Format __CHART__[pfad]__CHART__ zurück.
        """,
    )
