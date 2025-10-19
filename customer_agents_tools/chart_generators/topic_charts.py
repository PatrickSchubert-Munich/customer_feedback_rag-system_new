"""
Topic Chart Generators

Creates bar and pie charts for topic distribution analysis.
"""

import os
import sys
import traceback
from typing import Dict, Tuple, Optional
from collections import Counter

from ._shared import get_chart_path, plt


def create_topic_bar_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """
    Creates bar chart for topic distribution.

    Args:
        data (Dict): Collection query result with keys:
            - metadatas (list[dict]): Metadata containing 'topic' field

    Returns:
        Tuple[str, Optional[str]]:
            - str: Status message or description
            - Optional[str]: Chart path if successful, None on error

    Notes:
        - Shows feedback count per topic
        - Sorted by volume (descending)
        - Shows counts and percentages
        - Returns error if <2 topics (chart not useful)
    """
    try:
        print("   🎨 Erstelle Topic Bar Chart...")
        sys.stdout.flush()

        metadatas = data["metadatas"]
        if not metadatas:
            return "❌ Keine Daten für Topic-Chart", None

        topics = [m.get("topic", "Unknown") for m in metadatas]
        topic_counts = Counter(topics)

        if len(topic_counts) < 2:
            return "ℹ️ Nur ein Thema vorhanden - Chart nicht sinnvoll", None

        print(f"   📊 Topic-Verteilung: {dict(topic_counts)}")
        sys.stdout.flush()

        plt.figure(figsize=(12, 8))

        # Sort by count for better visualization
        sorted_topics = topic_counts.most_common()
        labels = [t[0] for t in sorted_topics]
        counts = [t[1] for t in sorted_topics]

        bars = plt.barh(labels, counts, color="#3742fa")
        plt.title("Feedback Distribution by Topic", fontsize=14, fontweight="bold")
        plt.xlabel("Number of Feedback Entries")
        plt.ylabel("Topic")

        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(
                width + 0.5,
                bar.get_y() + bar.get_height() / 2.0,
                f"{int(width):,}",
                ha="left",
                va="center",
            )

        plt.tight_layout()

        chart_path = get_chart_path("topic_distribution")

        print("   💾 Speichere Chart...")
        sys.stdout.flush()

        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"   ✅ Chart gespeichert: {chart_path}")
        sys.stdout.flush()

        # User-Ausgabe
        result = "📋 **Themen-Verteilung (Balkenchart)**\n\n"

        for topic, count in sorted_topics:
            percentage = (count / len(metadatas)) * 100
            result += f"• **{topic}**: {count:,} ({percentage:.1f}%)\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei create_topic_bar_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def create_topic_pie_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """
    Creates pie chart for topic distribution.

    Args:
        data (Dict): Collection query result with keys:
            - metadatas (list[dict]): Metadata containing 'topic' field

    Returns:
        Tuple[str, Optional[str]]:
            - str: Status message or description
            - Optional[str]: Chart path if successful, None on error

    Notes:
        - Shows percentage distribution of topics
        - Returns error if <2 topics (chart not useful)
    """
    try:
        print("   🎨 Erstelle Topic Pie Chart...")
        sys.stdout.flush()

        metadatas = data["metadatas"]
        if not metadatas:
            return "❌ Keine Daten für Topic-Chart", None

        topics = [m.get("topic", "Unknown") for m in metadatas]
        topic_counts = Counter(topics)

        if len(topic_counts) < 2:
            return "ℹ️ Nur ein Thema vorhanden - Chart nicht sinnvoll", None

        print(f"   📊 Topic-Verteilung: {dict(topic_counts)}")
        sys.stdout.flush()

        plt.figure(figsize=(10, 8))

        labels = list(topic_counts.keys())
        sizes = list(topic_counts.values())

        colors = ["#3742fa", "#ff6348", "#2ed573", "#ffa502", "#747d8c", "#5f27cd", "#ff4757", "#1e90ff"]

        plt.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
        )
        plt.title("Feedback Distribution by Topic", fontsize=14, fontweight="bold")
        plt.axis("equal")

        chart_path = get_chart_path("topic_pie_distribution")
        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"   ✅ Chart gespeichert: {chart_path}")
        sys.stdout.flush()

        # User-Ausgabe
        result = "📋 **Themen-Verteilung (Kreisdiagramm)**\n\n"

        for topic, count in topic_counts.most_common():
            percentage = (count / len(metadatas)) * 100
            result += f"• **{topic}**: {count:,} ({percentage:.1f}%)\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei create_topic_pie_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None
