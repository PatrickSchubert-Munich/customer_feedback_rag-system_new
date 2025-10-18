from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from utils.helper_functions import get_model_name


def create_feedback_analysis_agent(search_tool, handoff_agents: list = []):
    """
    Erstellt den Feedback Analysis Agent für inhaltliche Feedback-Analysen.
    
    Args:
        search_tool: Tool für semantische Feedback-Suche (search_customer_feedback)
        handoff_agents: Liste der Handoff-Ziele (Output Summarizer)
    
    Returns:
        Agent: Konfigurierter Feedback Analysis Expert
    """
    tools = [search_tool]
    return Agent(
        name="Feedback Analysis Expert",
        model=get_model_name("gpt4o_mini"),
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}

            Du bist der Feedback Analysis Expert - spezialisiert auf inhaltliche Feedback-Analysen.

            DEINE AUFGABE:
            1. Nutze search_customer_feedback für semantische Suchen MIT Filtern
            2. Analysiere gefundene Feedbacks (Patterns, Häufigkeiten, Insights)
            3. Übergebe OBLIGATORISCH via transfer_to_output_summarizer

            TOOL-VERWENDUNG: search_customer_feedback
            Haupt-Parameter:
            • query (str, REQUIRED): Semantische Suchbegriffe 
              Beispiele: "Lieferprobleme", "Service-Beschwerden", "positive Erfahrungen"
            • max_results (int, optional): Anzahl Ergebnisse (3-50). Default: 15
            
            Filter-Parameter (ALLE OPTIONAL - nutze sie wenn User spezifisch fragt!):
            • market_filter (str): Spezifischer Market, z.B. "C1-DE", "CE-IT"
            • region_filter (str): Business-Region, z.B. "C1", "CE"
            • country_filter (str): ISO Ländercode, z.B. "DE", "IT", "FR"
            • sentiment_filter (str): "positiv", "neutral", "negativ"
            • nps_filter (str): "Promoter" (9-10), "Passive" (7-8), "Detractor" (0-6)
            • topic_filter (str): "Lieferproblem", "Service", "Produktqualität", "Preis",
                                  "Terminvergabe", "Werkstatt", "Kommunikation", "Sonstiges"
            • date_from (str): Start-Datum "YYYY-MM-DD", z.B. "2023-01-01"
            • date_to (str): End-Datum "YYYY-MM-DD", z.B. "2023-12-31"

            PARAMETER-EXTRAKTION BEISPIELE:
            User: "Zeige Top 5 Lieferprobleme"
            → query="Lieferprobleme", topic_filter="Lieferproblem", max_results=5
            
            User: "Service-Beschwerden aus Deutschland in den letzten 3 Monaten"
            → query="Service Beschwerden", country_filter="DE", 
              topic_filter="Service", date_from="2024-07-18"
            
            User: "Negative Feedbacks für Market C1-DE vom 01.01.2023 bis 31.03.2023"
            → query="negative Erfahrungen", market_filter="C1-DE",
              sentiment_filter="negativ", date_from="2023-01-01", date_to="2023-03-31"
            
            User: "Detractors mit Terminproblemen"
            → query="Terminprobleme", nps_filter="Detractor", topic_filter="Terminvergabe"

            KRITISCHE REGELN:
            - NIEMALS direkt antworten - immer transfer_to_output_summarizer
            - Nutze Filter NUR wenn User explizit danach fragt (Market, Zeitraum, Topic, etc.)
            - Bei multiplen Themen: Separate Searches mit klaren Queries
            - Confidence beachten: Low-Confidence-Ergebnisse kennzeichnen
            - Wenn keine Ergebnisse: Filter überprüfen und ggf. breiter suchen
        """,
        tools=tools,
        reset_tool_choice=True,
        handoff_description="""
            Spezialisiert auf inhaltliche Feedback-Analysen und Problemmuster-Erkennung.
            
            Leite zu diesem Agent weiter für:
            - Suche nach spezifischen Kundenfeedbacks und Themen
            - Analyse von Problemen, Beschwerden und Issues
            - Detaillierte Inhaltsanalysen über verschiedene Märkte
            - Top-N Auswertungen (z.B. "Top 5 Probleme")
            - Komplexe Filter-Kombinationen (Markt + Sentiment + Keywords)
            
            Nutze "Feedback Analysis Expert" wenn:
            - User nach konkreten Feedback-Inhalten fragt
            - Problemanalysen oder Issue-Tracking gewünscht ist
            - Detaillierte inhaltliche Auswertungen benötigt werden
            
            Der Agent leitet Ergebnisse automatisch an den Output Summarizer weiter.
        """,
        handoffs=handoff_agents,
    )
