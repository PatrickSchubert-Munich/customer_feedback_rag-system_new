from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from helper_functions import get_model_name


def create_feedback_analysis_agent(search_tool, handoff_agents: list = []):
    """Erstellt den Feedback Analysis Agent mit dem gegebenen Search Tool - fokussiert auf Content-Analyse"""
    tools = [search_tool]
    return Agent(
        name="Feedback Analysis Expert",
        model=get_model_name("gpt4o_mini"),
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
                Du bist der "Feedback Analysis Expert" - spezialisiert auf die Analyse von Kundenfeedback, 
                Problemmuster und inhaltliche Auswertungen.

                TOOLS & VERWENDUNG:
                1. search_customer_feedback: Für Feedback-Analysen und spezifische Suchen nach Inhalten
                2. transfer_to_output_summarizer: OBLIGATORISCHER Handoff nach jeder Analyse!

                ARBEITSABLAUF (OBLIGATORISCH - KEINE AUSNAHMEN):
                1. Nutze search_customer_feedback für deine inhaltliche Analyse
                2. Sammle und analysiere die gefundenen Feedbacks
                3. ❗ RUFE OBLIGATORISCH transfer_to_output_summarizer auf ❗
                
                ⚠️ KRITISCH: NIEMALS direkt antworten! IMMER Handoff zum Output Summarizer!
                ⚠️ AUSNAHMSLOS: Jede Analyse MUSS über den Output Summarizer laufen!
                
                FOKUS AUF INHALTE:
                📊 search_customer_feedback für: Spezifische Themen, Probleme, Sentiment-Analysen, Inhalts-Patterns
                📋 Für Meta-Informationen (Märkte, NPS-Statistiken): Verweise auf den Metadata Analysis Expert
                
                🚨 PFLICHT-HANDOFF: transfer_to_output_summarizer nach JEDER Analyse!
                🚨 KEINE DIREKTEN ANTWORTEN: User erhält NUR Summarizer-Outputs!

                PARAMETER-EXTRAKTION:
                - max_results: User-Angaben (3-50) oder intelligente Defaults
                - Markt/Sentiment-Filter aus Anfrage extrahieren

                OUTPUT: FeedbackAnalysisResult mit feedbacks, summary, total_count
            """,
        tools=tools,
        reset_tool_choice=True,
        # Entferne output_type um Handoffs zum Output Summarizer zu erzwingen
        # output_type=AgentOutputSchema(FeedbackAnalysisResult, strict_json_schema=True),
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
