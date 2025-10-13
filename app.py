import asyncio
from dotenv import load_dotenv
from agents import Runner

from customer_agents_tools.robust_search_tool_factory import RobustSearchToolFactory
from customer_agents.feedback_analysis_agent import create_feedback_analysis_agent
from customer_agents.customer_manager_agent import (
    create_customer_manager_agent,
)
from customer_agents_tools.get_metadata_tool import create_metadata_tool
from customer_agents.metadata_analysis_agent import create_metadata_analysis_agent
from customer_agents.sentiment_analysis_agent import create_sentiment_analysis_agent
from customer_agents.output_summarizer_agent import create_output_summarizer_agent
from helper_functions import (
    get_azure_openai_client,
    load_csv,
    load_vectorstore,
    get_test_questions,
)
from utils.simple_history import SimpleConversationHistory

load_dotenv()

# Pfad zur CSV-Datei mit Kundenfeedback
FILE_PATH_CSV = "./data/feedback_data.csv"

# vectorstore type: "chroma" (aktuell einzige Option)
VECTORSTORE_TYPE = "chroma"

# Test question sets - flags to control which tests to run - VOLLSTÄNDIGER TEST
TEST_META = True  # Meta-Fragen (metadata_tool) - 10 Fragen
TEST_FEEDBACK = True  # Feedback-Analysen (search_customer_feedback) - 10 Fragen
TEST_VALIDATION = False  # Markt-Validierung (Fehlerprüfung)
TEST_SENTIMENT = False  # Sentiment-Analysen (sentiment_analysis_agent)
TEST_PARAMETERS = False  # User-Parameter Extraktion
TEST_COMPLEX = True  # Komplexe Multi-Kriterien Queries
TEST_EDGE = True  # Edge Cases (optional)

# Number of questions per category (default: 2) - Simple History
QUESTIONS_PER_CATEGORY = 6  # Vollständiger Test: 6 Meta + 6 Feedback = 12 Fragen


def print_native_response(result):
    """Formatiere die native SDK Response benutzerfreundlich"""
    print("\n🚀 " + "=" * 58 + " 🚀")
    print("    NATIVE SDK CUSTOMER FEEDBACK ANALYSIS")
    print("🚀 " + "=" * 58 + " 🚀\n")

    final_output = result.final_output

    # Prüfe ob es eine UserFriendlySummary ist (vom Output Summarizer)
    if hasattr(final_output, "executive_summary"):
        print("✅ STRUCTURED OUTPUT: UserFriendlySummary erkannt")
        print_formatted_summary(final_output)
    elif hasattr(final_output, "feedbacks"):
        print("✅ STRUCTURED OUTPUT: FeedbackAnalysisResult erkannt")
        print(f"📊 Found {len(final_output.feedbacks)} feedbacks")
        print(f"📝 Summary: {final_output.summary}")
    else:
        print("📄 DIRECT OUTPUT:")
        print(
            str(final_output)[:500] + "..."
            if len(str(final_output)) > 500
            else str(final_output)
        )


def print_formatted_summary(summary):
    """Formatiert UserFriendlySummary wie in der ursprünglichen app.py"""
    print("📊 EXECUTIVE SUMMARY")
    print("─" * 60)
    print(f"{summary.executive_summary}\n")

    if hasattr(summary, "key_insights") and summary.key_insights:
        print("🔍 KEY INSIGHTS")
        print("─" * 60)
        for i, insight in enumerate(summary.key_insights, 1):
            print(f"{i}. {insight.title}")
            print(f"   📝 {insight.description}")
            print(f"   🎯 Impact: {insight.impact}")
            print(f"   ⚡ Priority: {insight.priority}\n")

    if hasattr(summary, "statistics") and summary.statistics:
        stats = summary.statistics
        print("📈 STATISTICS")
        print("─" * 60)
        print(f"Total Feedbacks: {stats.total_feedbacks}")
        if stats.avg_nps is not None:
            print(f"Average NPS: {stats.avg_nps:.2f}")
        if stats.promoter_percentage is not None:
            print(f"Promoter: {stats.promoter_percentage:.1f}%")
            print(f"Passive: {stats.passive_percentage:.1f}%")
            print(f"Detractor: {stats.detractor_percentage:.1f}%")
        if stats.top_issues:
            print(f"Top Issues: {', '.join(stats.top_issues[:3])}")
        print()

    if (
        hasattr(summary, "actionable_recommendations")
        and summary.actionable_recommendations
    ):
        print("🚀 ACTIONABLE RECOMMENDATIONS")
        print("─" * 60)
        for i, rec in enumerate(summary.actionable_recommendations, 1):
            print(f"{i}. {rec.action}")
            print(f"   🏢 Department: {rec.department}")
            print(f"   ⏱️  Timeline: {rec.timeline}")
            print(f"   📊 Expected Impact: {rec.expected_impact}\n")


# main function to run the multi-agent system
async def main():
    """Main function to run the customer feedback system"""

    print("🚀 STARTING - CUSTOMER FEEDBACK SYSTEM - ")
    print("=" * 80)

    # Initialize OpenAI client FIRST (required for VectorStore)
    get_azure_openai_client()

    # Load data and tools
    customer_data = load_csv(path=FILE_PATH_CSV, write_local=False)

    # Log loaded data count
    collection = load_vectorstore(
        data=customer_data, type=VECTORSTORE_TYPE, create_new_store=False
    )

    # VALIDIERUNG: VectorStore muss Daten enthalten
    if collection is None:
        return
    if collection.count() == 0:
        return

    # Use enhanced search tool with better error handling
    search_customer_feedback = RobustSearchToolFactory.create_enhanced_search_tool(
        collection
    )

    # Create metadata tools (unified approach)
    metadata_tools = create_metadata_tool(collection)  # Returns dict of tools

    # Create agent hierarchy with native handoffs
    output_summarizer = create_output_summarizer_agent()

    # Create specialized Metadata Analysis Agent (no handoffs - only serves Customer Manager)
    metadata_analysis_agent = create_metadata_analysis_agent(
        metadata_tools=metadata_tools,
    )

    # Create Feedback Analysis Agent (focused on search and content analysis)
    feedback_analysis_agent = create_feedback_analysis_agent(
        search_tool=search_customer_feedback,
        handoff_agents=[output_summarizer],
    )

    # Create Sentiment Analysis Agent
    sentiment_analysis_agent = create_sentiment_analysis_agent(
        search_tool=search_customer_feedback, handoff_agents=[output_summarizer]
    )

    # Customer Manager with all specialized agents
    customer_manager = create_customer_manager_agent(
        handoff_agents=[
            metadata_analysis_agent,  # NEW: Dedicated metadata expert
            feedback_analysis_agent,
            sentiment_analysis_agent,
        ]
    )

    # Test queries
    test_queries = get_test_questions(
        test_meta=TEST_META,
        test_feedback=TEST_FEEDBACK,
        test_validation=TEST_VALIDATION,
        test_sentiment=TEST_SENTIMENT,
        test_parameters=TEST_PARAMETERS,
        test_complex=TEST_COMPLEX,
        test_edge=TEST_EDGE,
        questions_per_category=QUESTIONS_PER_CATEGORY,
    )

    # Initialize Session-based conversation with intelligent history and tracing
    from agents import SQLiteSession, trace, RunConfig

    session = SQLiteSession(
        "customer_feedback_session", "conversation_history.db"
    )  # File-based Session (persistent)

    # Enhanced tracing configuration for better handoff visibility
    _ = RunConfig(
        tracing_disabled=False,  # Ensure tracing is enabled
        trace_include_sensitive_data=False,  # Keep customer data private
    )

    # Backup: Initialize Simple History for stats tracking
    conversation = SimpleConversationHistory()

    for i, user_query in enumerate(test_queries, 1):
        print(f"\n\n🔍 TEST QUERY {i}: {user_query}")
        print("-" * 70)

        try:
            # Session-aware execution with automatic history management and enhanced tracing
            print("🚀 Processing with Agent System (with session history + tracing)...")

            # Wrap in custom trace for better visibility
            with trace(
                "Customer Feedback Multi-Agent Analysis",
                group_id=f"session_{session.session_id}",
            ):
                result = await Runner.run(customer_manager, user_query, session=session)
            print_native_response(result)

            # Simple history tracking - just one line!
            response_text = (
                str(result.final_output)
                if hasattr(result, "final_output")
                else str(result)
            )
            conversation.add_interaction(
                user_input=user_query,
                agent_response=response_text,
                agent_name="Customer Manager",
            )

            # Show simple stats
            stats = conversation.get_summary_stats()
            print(
                f"💬 Conversation: {stats['total_interactions']} interactions | Session: {stats['session_id']}"
            )

        except Exception as e:
            print(f"❌ ERROR: {e}")
            print(f"Error Type: {type(e).__name__}")

            # Even errors can be tracked simply
            conversation.add_interaction(
                user_input=user_query,
                agent_response=f"Error: {str(e)}",
                agent_name="System",
            )

    print("\n\n🎯 === EXECUTION COMPLETED === ")
    print("=" * 70)

    # Simple final statistics
    final_stats = conversation.get_summary_stats()
    print("\n📊 CONVERSATION SUMMARY:")
    print(f"   Session ID: {final_stats['session_id']}")
    print(f"   Total Interactions: {final_stats['total_interactions']}")
    print(f"   Agents Used: {final_stats['agents_used']}")
    print(f"   Avg Input Length: {final_stats['avg_user_input_length']} chars")
    print(f"   Avg Response Length: {final_stats['avg_response_length']} chars")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
