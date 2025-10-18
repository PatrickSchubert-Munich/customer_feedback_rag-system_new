from typing import Dict, Optional

from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX


def create_customer_manager_agent(
    metadata_snapshot: Dict[str, str],
    handoff_agents: Optional[list] = None,
) -> Agent:
    """
    Creates the Customer Manager Agent with embedded metadata snapshot.
    
    The Customer Manager is the central entry point and routes requests intelligently:
    - Metadata questions: Answers directly from embedded snapshot (no tools needed)
    - Content analyses: Handoff to Feedback Analysis Expert
    - Visualizations: Handoff to Chart Creator Expert
    
    Args:
        metadata_snapshot (Dict[str, str]): Pre-computed metadata from app startup.
            Created via `create_metadata_tool(collection)()`.
            Expected keys:
            - unique_markets: Comma-separated market list
            - nps_statistics: NPS average, median, category distribution
            - sentiment_statistics: Sentiment labels and scores
            - date_range: Time range of feedbacks
            - verbatim_statistics: Token length statistics
            - dataset_overview: Compact overall summary
            - total_entries: Number of entries
            
        handoff_agents (Optional[list]): List of specialist agents for handoffs.
            Typically: [Feedback Analysis Expert, Chart Creator Expert]
            Default: []

    Returns:
        Agent: Configured Customer Manager with embedded metadata.
            - No tools (everything is in snapshot)
            - Handoffs to specialist agents
            - Direct metadata answers without runtime tool calls
    
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

    # ✅ DYNAMIC AGENT DETECTION: Build list of available specialist agents
    available_agents = []
    agent_capabilities = {}
    
    for agent in handoff_agents:
        agent_name = agent.name
        available_agents.append(agent_name)
        
        # Detect agent type from name and define capabilities
        if "Chart Creator" in agent_name or "chart" in agent_name.lower():
            agent_capabilities[agent_name] = {
                "type": "visualization",
                "description": "Erstellt Visualisierungen und Charts (PNG-Dateien)"
            }
        elif "Feedback Analysis" in agent_name or "feedback" in agent_name.lower():
            agent_capabilities[agent_name] = {
                "type": "content_analysis",
                "description": "Analysiert Feedback-Inhalte semantisch"
            }
        elif "Output Summarizer" in agent_name or "summarizer" in agent_name.lower():
            agent_capabilities[agent_name] = {
                "type": "formatting",
                "description": "Formatiert technische Analysen als Business-Reports"
            }
        else:
            # Fallback for unknown agents
            agent_capabilities[agent_name] = {
                "type": "unknown",
                "description": "Specialist Agent"
            }
    
    # Build dynamic agent list for instructions
    agents_info = "\n".join([
        f"   • {name}: {caps['description']}"
        for name, caps in agent_capabilities.items()
    ]) if agent_capabilities else "   ℹ️ Keine Specialist Agents konfiguriert - nur Metadaten-Abfragen möglich"

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
        model="gpt-4o",
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}

You are the Customer Manager - central entry point for all customer feedback queries.

CRITICAL: All responses MUST be in GERMAN language (Deutsche Sprache).

═══════════════════════════════════════════════════════════════════════════
YOUR MULTI-AGENT SYSTEM (Specialist Agents under your control)
═══════════════════════════════════════════════════════════════════════════

Available Specialist Agents:
{agents_info if agents_info else "   No Specialist Agents configured"}

HANDOFF BEHAVIOR:
After successful delegation via transfer_to_*:
→ Specialist Agent takes over conversation completely
→ Agent returns answer directly to user
→ No further handling required from you

═══════════════════════════════════════════════════════════════════════════
EMBEDDED METADATA SNAPSHOT (pre-computed at app startup)
═══════════════════════════════════════════════════════════════════════════

Total count: {total_entries} entries

Markets, Regions & Countries:
{markets}

NPS Statistics:
{nps_stats}

Sentiment Statistics:
{sentiment_stats}

Topic Distribution:
{topic_stats}

Time Range:
{date_range}

Verbatim Text Lengths:
{verbatim_stats}

═══════════════════════════════════════════════════════════════════════════
YOUR TASK: INTELLIGENT ROUTING
═══════════════════════════════════════════════════════════════════════════

Analyze user query and decide:

[1] METADATA QUESTIONS - Answer directly from snapshot
   Examples:
   - "Which markets exist?"
   - "How many feedbacks do we have?"
   - "What is the average NPS?"
   - "Which sentiments exist?"
   - "What is the date range?"
   
   Rules:
   - Use ONLY the embedded data above
   - NO handoffs, NO computations
   - Answer precisely and directly
   
   IMPORTANT - Date Validation:
   When user asks for data from specific time period, CHECK FIRST if date
   is within available range (see "Time Range:" above).
   
   Examples:
   - User asks: "Show me feedbacks from 2023"
   - Range is: "2024-01-15 to 2024-12-20"
   → Answer: "Keine Daten aus 2023 verfügbar. Unser Datensatz umfasst nur 
      den Zeitraum 2024-01-15 bis 2024-12-20 (XXX Tage, XXX Einträge)."
   
   - User asks: "Feedbacks from 01.01.2025"
   - Range is: "2024-01-15 to 2024-12-20"
   → Answer: "Keine Daten aus Januar 2025 verfügbar. Der neueste Eintrag
      in unserem Datensatz ist vom 2024-12-20."

[2] CONTENT ANALYSES - transfer_to_feedback_analysis_expert
   Examples:
   - "Top 5 problems"
   - "Analyze feedback about [topic]"
   - "What are the most common complaints?"
   - "Show me critical feedbacks"
   
   Behavior:
   → Recognize semantic analyses and delegate via transfer_to_feedback_analysis_expert
   → Handoff happens seamlessly in background (don't mention to user)
   → Expert searches feedback texts semantically and delivers analysis

[3] VISUALIZATIONS - transfer_to_chart_creator_expert
   Examples:
   - "Create a diagram"
   - "Show sentiment as bar chart"
   - "Visualize NPS distribution"
   
   Behavior:
   → Recognize visualization requests and delegate via transfer_to_chart_creator_expert
   → Handoff happens seamlessly in background (don't mention to user)
   → Expert creates professional charts and returns special markers

═══════════════════════════════════════════════════════════════════════════
CRITICAL RULES - SYSTEM BEHAVIOR
═══════════════════════════════════════════════════════════════════════════

CORE RULES (from Multi-Agent SDK Best Practices):
- NEVER invent or estimate data
- NEVER mention handoff transfers in conversation (runs in background)
- NO tools available (everything is embedded in snapshot)
- When uncertain: better forward than guess
- Consider context from history (e.g. "the first market")
- Answer precisely and business-oriented
- Handoffs happen transparently in background (seamless transfers)

REMEMBER: Always respond in GERMAN language!
        """,
        tools=[],
        handoff_description="""
            Central triaging agent that answers factual metadata questions directly
            using an embedded static snapshot and forwards analytical queries to
            specialist agents for detailed examination.
        """,
        handoffs=handoff_agents,
    )
