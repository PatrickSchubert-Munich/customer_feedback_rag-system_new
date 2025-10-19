"""
Time Analysis Chart Generator

Creates timeline analysis dashboard with multiple trend charts.
"""
import sys
import traceback
from typing import Dict, Tuple, Optional
from collections import defaultdict
from datetime import datetime

from ._shared import get_chart_path, plt


def create_time_analysis(data: Dict) -> Tuple[str, Optional[str]]:
    """
    Creates timeline analysis with multiple charts (trends over time).

    Args:
        data (Dict): Collection query result with keys:
            - metadatas (list[dict]): Metadata containing 'date_str', 'sentiment_label', 
              'nps_category', and 'nps' fields

    Returns:
        Tuple[str, Optional[str]]:
            - str: Status message or description
            - Optional[str]: Chart path if successful, None on error

    Notes:
        - Creates 4 subplots: Volume trend, Sentiment trend, NPS categories, NPS score
        - Date format: "YYYY-MM-DD" parsed from 'date_str'
        - Monthly aggregation for clearer trends
        - Returns error if no temporal data available
    """
    try:
        print("   🎨 Erstelle Time Analysis Charts...")
        sys.stdout.flush()

        metadatas = data["metadatas"]
        if not metadatas:
            return "❌ Keine Daten für Time-Analysis", None

        time_data = []

        for metadata in metadatas:
            date_timestamp = metadata.get("date", 0)
            nps_category = metadata.get("nps_category", "Unknown")
            sentiment = metadata.get("sentiment_label", "Unknown")

            if date_timestamp and isinstance(date_timestamp, (int, float)):
                try:
                    date_obj = datetime.fromtimestamp(date_timestamp)
                    time_data.append(
                        {
                            "date": date_obj,
                            "year_month": date_obj.strftime("%Y-%m"),
                            "year": date_obj.year,
                            "nps_category": nps_category,
                            "sentiment": sentiment,
                        }
                    )
                except (ValueError, OSError):
                    continue

        if not time_data:
            return "❌ Keine validen Datums-Informationen gefunden", None

        print(f"   📊 {len(time_data)} Einträge mit validen Zeitstempeln")
        sys.stdout.flush()

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # Chart 1: Volume Over Time
        monthly_counts = defaultdict(int)
        for item in time_data:
            monthly_counts[item["year_month"]] += 1

        sorted_months = sorted(monthly_counts.keys())
        counts = [monthly_counts[month] for month in sorted_months]

        ax1.plot(
            range(len(sorted_months)),
            counts,
            marker="o",
            linewidth=2,
            markersize=6,
            color="#3742fa",
        )
        ax1.set_title("Feedback Volume Over Time", fontweight="bold", fontsize=12)
        ax1.set_ylabel("Number of Feedback")
        ax1.set_xticks(range(0, len(sorted_months), max(1, len(sorted_months) // 6)))
        ax1.set_xticklabels(
            [
                sorted_months[i]
                for i in range(0, len(sorted_months), max(1, len(sorted_months) // 6))
            ],
            rotation=45,
        )
        ax1.grid(True, alpha=0.3)

        # Chart 2: NPS Categories Over Time
        nps_monthly = defaultdict(lambda: defaultdict(int))
        for item in time_data:
            nps_monthly[item["year_month"]][item["nps_category"]] += 1

        categories = ["Detractor", "Passive", "Promoter"]
        colors = ["#ff6b6b", "#feca57", "#2ed573"]  # Rot/Gelb/Grün

        for i, category in enumerate(categories):
            category_counts = [
                nps_monthly[month].get(category, 0) for month in sorted_months
            ]
            ax2.plot(
                range(len(sorted_months)),
                category_counts,
                marker="o",
                label=category,
                color=colors[i],
                linewidth=2,
                markersize=4,
            )

        ax2.set_title("NPS Categories Over Time", fontweight="bold", fontsize=12)
        ax2.set_ylabel("Number of Customers")
        ax2.set_xticks(range(0, len(sorted_months), max(1, len(sorted_months) // 6)))
        ax2.set_xticklabels(
            [
                sorted_months[i]
                for i in range(0, len(sorted_months), max(1, len(sorted_months) // 6))
            ],
            rotation=45,
        )
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Chart 3: Sentiment Over Time
        sentiment_monthly = defaultdict(lambda: defaultdict(int))
        for item in time_data:
            sentiment_monthly[item["year_month"]][item["sentiment"]] += 1

        sentiments = ["negativ", "neutral", "positiv"]
        sentiment_colors = ["#ff4757", "#747d8c", "#2ed573"]

        for i, sentiment in enumerate(sentiments):
            sentiment_counts = [
                sentiment_monthly[month].get(sentiment, 0) for month in sorted_months
            ]
            if max(sentiment_counts) > 0:
                ax3.plot(
                    range(len(sorted_months)),
                    sentiment_counts,
                    marker="o",
                    label=sentiment.title(),
                    color=sentiment_colors[i],
                    linewidth=2,
                    markersize=4,
                )

        ax3.set_title("Sentiment Over Time", fontweight="bold", fontsize=12)
        ax3.set_ylabel("Number of Feedback")
        ax3.set_xticks(range(0, len(sorted_months), max(1, len(sorted_months) // 6)))
        ax3.set_xticklabels(
            [
                sorted_months[i]
                for i in range(0, len(sorted_months), max(1, len(sorted_months) // 6))
            ],
            rotation=45,
        )
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Chart 4: NPS Distribution (%) Over Time - Stacked Bar
        monthly_percentages = defaultdict(lambda: defaultdict(float))
        for month in sorted_months:
            total = sum(nps_monthly[month].values())
            if total > 0:
                for category in categories:
                    monthly_percentages[month][category] = (
                        nps_monthly[month].get(category, 0) / total
                    ) * 100

        detractor_pct = [
            monthly_percentages[month]["Detractor"] for month in sorted_months
        ]
        passive_pct = [monthly_percentages[month]["Passive"] for month in sorted_months]
        promoter_pct = [
            monthly_percentages[month]["Promoter"] for month in sorted_months
        ]

        ax4.bar(
            range(len(sorted_months)),
            detractor_pct,
            label="Detractor",
            color=colors[0],
            alpha=0.8,
        )
        ax4.bar(
            range(len(sorted_months)),
            passive_pct,
            bottom=detractor_pct,
            label="Passive",
            color=colors[1],
            alpha=0.8,
        )

        promoter_bottom = [d + p for d, p in zip(detractor_pct, passive_pct)]
        ax4.bar(
            range(len(sorted_months)),
            promoter_pct,
            bottom=promoter_bottom,
            label="Promoter",
            color=colors[2],
            alpha=0.8,
        )

        ax4.set_title("NPS Distribution (%) Over Time", fontweight="bold", fontsize=12)
        ax4.set_ylabel("Percentage")
        ax4.set_xticks(range(0, len(sorted_months), max(1, len(sorted_months) // 6)))
        ax4.set_xticklabels(
            [
                sorted_months[i]
                for i in range(0, len(sorted_months), max(1, len(sorted_months) // 6))
            ],
            rotation=45,
        )
        ax4.legend()
        ax4.set_ylim(0, 100)

        plt.tight_layout()

        chart_path = get_chart_path("time_analysis")

        print("   💾 Speichere Chart...")
        sys.stdout.flush()

        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"   ✅ Chart gespeichert: {chart_path}")
        sys.stdout.flush()

        # Optimierte User-Ausgabe: Fokus auf Zeitraum und Trends
        result = "📅 **Zeitverlauf-Analyse**\n\n"
        result += f"📊 Zeitraum: {sorted_months[0]} bis {sorted_months[-1]}\n\n"

        result += "**Letzte 6 Monate:**\n"
        for month in sorted_months[-6:]:
            total = monthly_counts[month]
            result += f"• {month}: {total:,} Feedbacks\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei create_time_analysis: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None
