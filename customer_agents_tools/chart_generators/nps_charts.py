"""
NPS Chart Generators

Creates bar and pie charts for Net Promoter Score (NPS) category distribution analysis.
"""

import sys
import traceback
from typing import Dict, Tuple, Optional
from collections import Counter

from ._shared import get_chart_path, plt


def create_nps_bar_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """
    Creates bar chart for NPS category distribution.

    Args:
        data (Dict): Collection query result with keys:
            - metadatas (list[dict]): Metadata containing 'nps_category' field

    Returns:
        Tuple[str, Optional[str]]:
            - str: Status message or description
            - Optional[str]: Chart path if successful, None on error

    Notes:
        - NPS categories: "Detractor" (0-6), "Passive" (7-8), "Promoter" (9-10)
        - Colors: Red (Detractor), Yellow (Passive), Green (Promoter)
        - Shows counts and percentages
        - Returns error if no data or metadata missing
    """
    try:
        print("   🎨 Erstelle NPS Bar Chart...")
        sys.stdout.flush()

        metadatas = data["metadatas"]
        if not metadatas:
            return "❌ Keine Daten für NPS-Chart", None

        categories = [m.get("nps_category", "Unknown") for m in metadatas]
        category_counts = Counter(categories)

        plt.figure(figsize=(10, 6))
        labels = list(category_counts.keys())
        counts = list(category_counts.values())
        colors = ["#ff6b6b", "#feca57", "#2ed573"]  # Rot/Gelb/Grün

        bars = plt.bar(labels, counts, color=colors[: len(labels)])
        plt.title("NPS Category Distribution", fontsize=14, fontweight="bold")
        plt.xlabel("NPS Category")
        plt.ylabel("Number of Customers")

        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 1,
                f"{int(height):,}",
                ha="center",
                va="bottom",
            )

        plt.tight_layout()

        chart_path = get_chart_path("nps_distribution")
        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"   ✅ Chart gespeichert: {chart_path}")
        sys.stdout.flush()

        # Optimierte User-Ausgabe: Fokus auf Ergebnisse, nicht technische Details
        result = "⭐ **NPS-Kategorien (Balkenchart)**\n\n"

        for category, count in category_counts.most_common():
            percentage = (count / len(metadatas)) * 100
            result += f"• **{category}**: {count:,} ({percentage:.1f}%)\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei create_nps_bar_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def create_nps_pie_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """
    Creates pie chart for NPS category distribution.

    Args:
        data (Dict): Collection query result with keys:
            - metadatas (list[dict]): Metadata containing 'nps_category' field

    Returns:
        Tuple[str, Optional[str]]:
            - str: Status message or description
            - Optional[str]: Chart path if successful, None on error

    Notes:
        - NPS categories: "Detractor" (0-6), "Passive" (7-8), "Promoter" (9-10)
        - Colors: Red (Detractor), Yellow (Passive), Green (Promoter)
        - Shows percentages on slices
        - Returns error if no data or metadata missing
    """
    try:
        print("   🎨 Erstelle NPS Pie Chart...")
        sys.stdout.flush()

        metadatas = data["metadatas"]
        if not metadatas:
            return "❌ Keine Daten für NPS-Chart", None

        categories = [m.get("nps_category", "Unknown") for m in metadatas]
        category_counts = Counter(categories)

        plt.figure(figsize=(8, 6))
        
        # NPS Kategorien in konsistenter Reihenfolge
        nps_order = ["Promoter", "Passive", "Detractor"]
        labels = [cat for cat in nps_order if cat in category_counts]
        sizes = [category_counts[cat] for cat in labels]
        colors = ["#2ed573", "#feca57", "#ff6b6b"]  # Grün/Gelb/Rot

        plt.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            colors=colors[:len(labels)],
            startangle=90,
        )
        plt.title("NPS Category Distribution", fontsize=14, fontweight="bold")
        plt.axis("equal")

        chart_path = get_chart_path("nps_pie_distribution")
        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"   ✅ Chart gespeichert: {chart_path}")
        sys.stdout.flush()

        # Optimierte User-Ausgabe
        result = "⭐ **NPS-Kategorien (Kreisdiagramm)**\n\n"

        for category, count in category_counts.most_common():
            percentage = (count / len(metadatas)) * 100
            result += f"• **{category}**: {count:,} ({percentage:.1f}%)\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei create_nps_pie_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None
