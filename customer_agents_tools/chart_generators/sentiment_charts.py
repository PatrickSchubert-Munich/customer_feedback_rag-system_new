"""
Sentiment Chart Generators

Creates bar and pie charts for sentiment distribution analysis.
"""

import os
import sys
import traceback
from typing import Dict, Tuple, Optional
from collections import Counter

from ._shared import get_chart_path, plt


def create_sentiment_bar_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """
    Creates bar chart for sentiment distribution.

    Args:
        data (Dict): Collection query result with keys:
            - metadatas (list[dict]): Metadata containing 'sentiment_label' field

    Returns:
        Tuple[str, Optional[str]]: 
            - str: Status message or description
            - Optional[str]: Chart path if successful, None on error

    Notes:
        - Sentiment values: "positiv", "neutral", "negativ"
        - Colors: Green (positiv), Yellow (neutral), Red (negativ)
        - Shows counts and percentages
        - Returns error if no data or metadata missing
    """
    try:
        print("   🎨 Erstelle Sentiment Bar Chart...")
        sys.stdout.flush()

        metadatas = data["metadatas"]
        if not metadatas:
            return "❌ Keine Daten für Sentiment-Chart", None

        sentiments = [m.get("sentiment_label", "Unknown") for m in metadatas]
        sentiment_counts = Counter(sentiments)

        print(f"   📊 Sentiment-Verteilung: {dict(sentiment_counts)}")
        sys.stdout.flush()

        plt.figure(figsize=(10, 6))
        
        # Sortiere für konsistente Anzeige: Positiv, Neutral, Negativ
        sentiment_order = ["positiv", "neutral", "negativ"]
        labels = [s for s in sentiment_order if s in sentiment_counts]
        counts = [sentiment_counts[s] for s in labels]
        
        # Farben: Grün für Positiv, Gelb für Neutral, Rot für Negativ
        colors = ["#2ed573", "#feca57", "#ff6b6b"]  # Grün/Gelb/Rot
        bar_colors = [colors[sentiment_order.index(s)] for s in labels]

        bars = plt.bar(labels, counts, color=bar_colors, edgecolor='black', linewidth=1.2)
        
        # Werte auf den Balken anzeigen
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + height * 0.01,
                f"{int(height):,}",
                ha="center",
                va="bottom",
                fontsize=11,
                fontweight="bold"
            )
        
        plt.title(
            "Sentiment Distribution in Customer Feedback",
            fontsize=14,
            fontweight="bold",
        )
        plt.xlabel("Sentiment", fontweight="bold")
        plt.ylabel("Number of Feedbacks", fontweight="bold")
        plt.grid(axis='y', alpha=0.3)

        chart_path = get_chart_path("sentiment_distribution")

        print("   💾 Speichere Chart...")
        sys.stdout.flush()

        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"   ✅ Chart gespeichert: {chart_path}")
        print(f"   ✅ File existiert: {os.path.exists(chart_path)}")
        if os.path.exists(chart_path):
            print(f"   ✅ File-Größe: {os.path.getsize(chart_path)} bytes")
        sys.stdout.flush()

        # Optimierte User-Ausgabe: Klar, prägnant, ohne technische Details
        result = "**Sentiment-Verteilung (Balkenchart)**\n\n"

        for sentiment, count in sentiment_counts.most_common():
            percentage = (count / len(metadatas)) * 100
            result += f"• **{sentiment.title()}**: {count:,} ({percentage:.1f}%)\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei create_sentiment_bar_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def create_sentiment_pie_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """
    Creates pie chart for sentiment distribution.

    Args:
        data (Dict): Collection query result with keys:
            - metadatas (list[dict]): Metadata containing 'sentiment_label' field

    Returns:
        Tuple[str, Optional[str]]:
            - str: Status message or description
            - Optional[str]: Chart path if successful, None on error

    Notes:
        - Sentiment values: "positiv", "neutral", "negativ"
        - Colors: Green (positiv), Yellow (neutral), Red (negativ)
        - Shows percentages on slices
        - Returns error if no data or metadata missing
    """
    try:
        print("   🎨 Erstelle Sentiment Pie Chart...")
        sys.stdout.flush()

        metadatas = data["metadatas"]
        if not metadatas:
            return "❌ Keine Daten für Sentiment-Chart", None

        sentiments = [m.get("sentiment_label", "Unknown") for m in metadatas]
        sentiment_counts = Counter(sentiments)

        print(f"   📊 Sentiment-Verteilung: {dict(sentiment_counts)}")
        sys.stdout.flush()

        plt.figure(figsize=(8, 6))
        colors = ["#2ed573", "#feca57", "#ff6b6b"]  # Grün/Gelb/Rot

        # Sortiere für konsistente Anzeige: Positiv, Neutral, Negativ
        sentiment_order = ["positiv", "neutral", "negativ"]
        labels = [s.title() for s in sentiment_order if s in sentiment_counts]
        sizes = [sentiment_counts[s] for s in sentiment_order if s in sentiment_counts]

        plt.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            colors=colors[:len(labels)],
            startangle=90,
        )
        plt.title(
            "Sentiment Distribution in Customer Feedback",
            fontsize=14,
            fontweight="bold",
        )
        plt.axis("equal")

        chart_path = get_chart_path("sentiment_pie_distribution")

        print("   💾 Speichere Chart...")
        sys.stdout.flush()

        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"   ✅ Chart gespeichert: {chart_path}")
        print(f"   ✅ File existiert: {os.path.exists(chart_path)}")
        if os.path.exists(chart_path):
            print(f"   ✅ File-Größe: {os.path.getsize(chart_path)} bytes")
        sys.stdout.flush()

        # Optimierte User-Ausgabe: Klar, prägnant, ohne technische Details
        result = "**Sentiment-Verteilung (Kreisdiagramm)**\n\n"

        for sentiment, count in sentiment_counts.most_common():
            percentage = (count / len(metadatas)) * 100
            result += f"• **{sentiment.title()}**: {count:,} ({percentage:.1f}%)\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei create_sentiment_pie_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None
