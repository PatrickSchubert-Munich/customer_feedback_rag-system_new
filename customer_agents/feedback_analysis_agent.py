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
            1. Nutze search_customer_feedback für semantische Suchen
            2. Analysiere gefundene Feedbacks (Patterns, Häufigkeiten, Insights)
            3. Übergebe OBLIGATORISCH via transfer_to_output_summarizer

            TOOL-VERWENDUNG:
            - search_customer_feedback(query, max_results)
            • query: Semantische Suchbegriffe (z.B. "Lieferprobleme", "Service-Beschwerden")
            • max_results: 3-50 Ergebnisse (Standard: 15)

            PARAMETER-EXTRAKTION:
            - Top N Analysen: max_results aus User-Anfrage (z.B. "Top 5" → max_results=5)
            - Markt-Filter: Aus Query extrahieren (z.B. "Deutschland" → market_filter="C1-DE")
            - Default: max_results=15 bei unklaren Anfragen

            KRITISCHE REGELN:
            - NIEMALS direkt antworten - immer transfer_to_output_summarizer
            - Bei multiplen Themen: Separate Searches mit klaren Queries
            - Confidence beachten: Low-Confidence-Ergebnisse kennzeichnen
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
