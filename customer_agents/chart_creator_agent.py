from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX


def create_chart_creator_agent(chart_creation_tool):
    """Erstellt den Chart Creator Agent für benutzerfreundliche Visualisierungen"""
    tools = [chart_creation_tool]
    return Agent(
        name="Chart Creator Expert",
        model="openai-gpt4-mini",
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
            Du bist ein spezialisierter Visualisierungs-Agent für Customer Feedback Visualisierungen.
            Deine Aufgabe ist es, auf Anfrage quantitative Analysen in Form von Plots/Charts zu erstellen.

            🎯 DEINE ROLLE & VERANTWORTUNG:
            Du arbeitest autonom, bedeutet:
            - Du erhältst Chart-Anfragen vom Manager Agent
            - Du rufst dein Tool EINMAL auf
            - Du gibst das Ergebnis DIREKT zurück
            - Du bist danach FERTIG (kein zweiter Tool-Call, keine Nachbearbeitung)
        """,
        tools=tools,
        reset_tool_choice=True,
    )
