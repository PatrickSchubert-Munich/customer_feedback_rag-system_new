"""
Overview Chart Generator

Creates comprehensive overview dashboard with multiple summary charts.
"""
import sys
import traceback
from typing import Dict, Tuple, Optional
from collections import Counter

from ._shared import get_chart_path, plt


def create_overview_charts(data: Dict) -> Tuple[str, Optional[str]]:
    """
    Creates overview dashboard with 4 charts (comprehensive summary).

    Args:
        data (Dict): Collection query result with keys:
            - metadatas (list[dict]): Metadata containing 'sentiment_label', 'nps_category',
              'market', and 'topic' fields

    Returns:
        Tuple[str, Optional[str]]:
            - str: Status message or description
            - Optional[str]: Chart path if successful, None on error

    Notes:
        - Creates 2x2 grid: Sentiment pie, NPS pie, Market distribution, Topic distribution
        - Comprehensive overview for executive summaries
        - Returns error if no data available
    """
    try:
        print("   🎨 Erstelle Overview Dashboard...")
        sys.stdout.flush()

        metadatas = data["metadatas"]
        if not metadatas:
            return "❌ Keine Daten für Overview", None

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        # Chart 1: Sentiment Distribution (Pie)
        sentiments = [m.get("sentiment_label", "Unknown") for m in metadatas]
        sentiment_counts = Counter(sentiments)
        ax1.pie(
            sentiment_counts.values(),
            labels=sentiment_counts.keys(),
            autopct="%1.1f%%",
            startangle=90,
        )
        ax1.set_title("Sentiment Distribution")

        # Chart 2: NPS Categories (Bar)
        categories = [m.get("nps_category", "Unknown") for m in metadatas]
        category_counts = Counter(categories)
        ax2.bar(
            category_counts.keys(),
            category_counts.values(),
            color=["#ff6b6b", "#feca57", "#48dbfb"],
        )
        ax2.set_title("NPS Categories")
        ax2.set_ylabel("Count")

        # Chart 3: Markets (Horizontal Bar)
        markets = [m.get("market", "Unknown") for m in metadatas]
        market_counts = Counter(markets)
        ax3.barh(
            list(market_counts.keys()), list(market_counts.values()), color="#3742fa"
        )
        ax3.set_title("Markets")
        ax3.set_xlabel("Count")

        # Chart 4: NPS Score Distribution (Histogram)
        nps_scores = []
        for m in metadatas:
            nps = m.get("nps")
            if nps is not None:
                try:
                    nps_scores.append(int(nps))
                except (ValueError, TypeError):
                    pass

        if nps_scores:
            ax4.hist(nps_scores, bins=11, range=(0, 10), color="#ff9ff3", alpha=0.7)
            ax4.set_title("NPS Score Distribution")
            ax4.set_xlabel("NPS Score")
            ax4.set_ylabel("Count")
        else:
            ax4.text(
                0.5,
                0.5,
                "No NPS data",
                ha="center",
                va="center",
                transform=ax4.transAxes,
            )
            ax4.set_title("NPS Score Distribution")

        plt.tight_layout()

        chart_path = get_chart_path("feedback_overview")

        print("   💾 Speichere Chart...")
        sys.stdout.flush()

        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"   ✅ Chart gespeichert: {chart_path}")
        sys.stdout.flush()

        # Optimierte User-Ausgabe: Kompakter Überblick mit Key-Insights
        result = "📊 **Feedback-Überblick**\n\n"
        
        # Zeige die wichtigsten Insights
        top_sentiment = sentiment_counts.most_common(1)[0]
        top_nps = category_counts.most_common(1)[0]
        
        result += f"• **Sentiment**: {top_sentiment[0].title()} dominiert ({(top_sentiment[1]/len(metadatas)*100):.1f}%)\n"
        result += f"• **NPS**: {top_nps[0]} führend ({(top_nps[1]/len(metadatas)*100):.1f}%)\n"
        
        if nps_scores:
            avg_nps = sum(nps_scores) / len(nps_scores)
            result += f"• **Durchschnittlicher NPS-Score**: {avg_nps:.1f}/10\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei create_overview_charts: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None
