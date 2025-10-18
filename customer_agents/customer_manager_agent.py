from typing import Dict, Optional

from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX


def create_customer_manager_agent(
    metadata_snapshot: Dict[str, str],
    handoff_agents: Optional[list] = None,
) -> Agent:
    """
    Erstellt den Customer Manager Agent mit embedded Metadata Snapshot.
    
    Der Customer Manager ist der zentrale Einstiegspunkt und routet Anfragen intelligent:
    - Metadaten-Fragen: Beantwortet direkt aus embedded Snapshot (keine Tools nötig)
    - Inhalts-Analysen: Handoff zu Feedback Analysis Expert
    - Visualisierungen: Handoff zu Chart Creator Expert
    
    Args:
        metadata_snapshot (Dict[str, str]): Pre-computed metadata vom App-Start.
            Erstellt via `create_metadata_tool(collection)()`.
            Erwartete Keys:
            - unique_markets: Kommagetrennte Markt-Liste
            - nps_statistics: NPS-Durchschnitt, Median, Kategorien-Verteilung
            - sentiment_statistics: Sentiment-Labels und Scores
            - date_range: Zeitraum der Feedbacks
            - verbatim_statistics: Token-Längen-Statistiken
            - dataset_overview: Kompakte Gesamtübersicht
            - total_entries: Anzahl Einträge
            
        handoff_agents (Optional[list]): Liste der Specialist Agents für Handoffs.
            Typischerweise: [Feedback Analysis Expert, Chart Creator Expert]
            Default: []

    Returns:
        Agent: Konfigurierter Customer Manager mit embedded Metadaten.
            - Keine Tools (alles ist im Snapshot)
            - Handoffs zu Specialist Agents
            - Direkte Metadaten-Antworten ohne Runtime-Tool-Calls
    
    Examples:
        >>> snapshot = build_metadata_snapshot()
        >>> manager = create_customer_manager_agent(
        ...     metadata_snapshot=snapshot,
        ...     handoff_agents=[feedback_expert, chart_expert]
        ... )
    """
    if handoff_agents is None:
        handoff_agents = []
    else:
        # Convert to list to satisfy type requirements
        handoff_agents = list(handoff_agents)

    # Extract metadata values with safe fallbacks
    markets = metadata_snapshot.get("unique_markets", "Keine Marktdaten verfügbar.")
    nps_stats = metadata_snapshot.get("nps_statistics", "Keine NPS-Daten verfügbar.")
    sentiment_stats = metadata_snapshot.get(
        "sentiment_statistics", "Keine Sentiment-Daten verfügbar."
    )
    topic_stats = metadata_snapshot.get(
        "topic_statistics", "Keine Topic-Daten verfügbar."
    )
    date_range = metadata_snapshot.get("date_range", "Keine Datumsdaten verfügbar.")
    verbatim_stats = metadata_snapshot.get(
        "verbatim_statistics", "Keine Token-Count-Daten verfügbar."
    )
    dataset_overview = metadata_snapshot.get(
        "dataset_overview", "Keine Daten verfügbar."
    )
    total_entries = metadata_snapshot.get("total_entries", "Unbekannt")

    return Agent(
        name="Customer Manager",
        model="openai-gpt4-omni",
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}

Du bist der Customer Manager - zentraler Einstiegspunkt für alle Kundenfeedback-Anfragen.

═══════════════════════════════════════════════════════════════════════════
📊 EMBEDDED METADATA SNAPSHOT (beim App-Start vorberechnet)
═══════════════════════════════════════════════════════════════════════════

Gesamtanzahl: {total_entries} Einträge

Märkte, Regionen & Länder:
{markets}

NPS-Statistiken:
{nps_stats}

Sentiment-Statistiken:
{sentiment_stats}

Topic-Verteilung:
{topic_stats}

Zeitraum:
{date_range}

Verbatim-Textlängen:
{verbatim_stats}

═══════════════════════════════════════════════════════════════════════════
🎯 DEINE AUFGABE: INTELLIGENTES ROUTING
═══════════════════════════════════════════════════════════════════════════

Analysiere die User-Anfrage und entscheide:

1️⃣ METADATEN-FRAGEN → Direkt beantworten aus Snapshot
   Beispiele:
   - "Welche Märkte gibt es?"
   - "Wie viele Feedbacks haben wir?"
   - "Was ist der NPS-Durchschnitt?"
   - "Welche Sentiments gibt es?"
   - "Von wann bis wann gehen die Daten?"
   
   ✅ Nutze AUSSCHLIESSLICH die oben embedded Daten
   ✅ KEINE Handoffs, KEINE Berechnungen
   ✅ Antworte präzise und direkt

2️⃣ INHALTS-ANALYSEN → transfer_to_feedback_analysis_expert
   Beispiele:
   - "Top 5 Probleme"
   - "Analysiere Feedback zu [Thema]"
   - "Was sind die häufigsten Beschwerden?"
   - "Zeige mir kritische Feedbacks"
   
   → Rufe SOFORT transfer_to_feedback_analysis_expert auf
   → Der Expert durchsucht die Feedback-Texte semantisch

3️⃣ VISUALISIERUNGEN → transfer_to_chart_creator_expert
   Beispiele:
   - "Erstelle ein Diagramm"
   - "Zeige Sentiment als Balkenchart"
   - "Visualisiere NPS-Verteilung"
   
   → Rufe SOFORT transfer_to_chart_creator_expert auf
   → Der Expert erstellt professionelle Charts

═══════════════════════════════════════════════════════════════════════════
⚠️ KRITISCHE REGELN
═══════════════════════════════════════════════════════════════════════════

❌ NIEMALS Daten erfinden oder schätzen
❌ NIEMALS "wende dich an..." sagen (direkt transfer_to_* aufrufen)
❌ KEINE Tools verfügbar (alles ist im Snapshot embedded)

✅ Bei Unsicherheit: lieber weiterleiten als raten
✅ Kontext aus Historie beachten (z.B. "der erste Markt")
✅ Präzise und Business-orientiert antworten
        """,
        tools=[],
        handoff_description="""
            Central triaging agent that answers factual metadata questions directly
            using an embedded static snapshot and forwards analytical queries to
            the Feedback Analysis Expert for detailed content examination.
        """,
        handoffs=handoff_agents,
    )
