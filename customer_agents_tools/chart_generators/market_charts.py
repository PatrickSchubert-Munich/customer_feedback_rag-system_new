"""
Market Chart Generators

Creates bar, pie, and breakdown charts for market distribution analysis.
"""

import sys
import traceback
from typing import Dict, Tuple, Optional
from collections import Counter
import numpy as np

from ._shared import get_chart_path, plt


def create_market_bar_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """
    Creates bar chart for market volume distribution.

    Args:
        data (Dict): Collection query result with keys:
            - metadatas (list[dict]): Metadata containing 'market' field

    Returns:
        Tuple[str, Optional[str]]:
            - str: Status message or description
            - Optional[str]: Chart path if successful, None on error

    Notes:
        - Shows feedback count per market (e.g. "C1-DE", "CE-IT")
        - Sorted by volume (descending)
        - Shows counts and percentages
        - Returns error if <2 markets (chart not useful)
    """
    try:
        print("   🎨 Erstelle Market Bar Chart...")
        sys.stdout.flush()

        metadatas = data["metadatas"]
        if not metadatas:
            return "❌ Keine Daten für Market-Chart", None

        markets = [m.get("market", "Unknown") for m in metadatas]
        market_counts = Counter(markets)

        print(f"   📊 Market-Verteilung: {dict(market_counts)}")
        sys.stdout.flush()

        plt.figure(figsize=(10, 6))

        labels = list(market_counts.keys())
        counts = list(market_counts.values())

        bars = plt.barh(labels, counts, color="#3742fa")
        plt.title("Feedback Distribution by Market", fontsize=14, fontweight="bold")
        plt.xlabel("Number of Feedback Entries")
        plt.ylabel("Market")

        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(
                width + 1,
                bar.get_y() + bar.get_height() / 2.0,
                f"{int(width):,}",
                ha="left",
                va="center",
            )

        plt.tight_layout()

        chart_path = get_chart_path("market_distribution")

        print("   💾 Speichere Chart...")
        sys.stdout.flush()

        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"   ✅ Chart gespeichert: {chart_path}")
        sys.stdout.flush()

        # Optimierte User-Ausgabe: Klar und fokussiert
        result = "🌍 **Markt-Verteilung (Balkenchart)**\n\n"

        for market, count in market_counts.most_common():
            percentage = (count / len(metadatas)) * 100
            result += f"• **{market}**: {count:,} ({percentage:.1f}%)\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei create_market_bar_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def create_market_pie_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """
    Creates pie chart for market share distribution.

    Args:
        data (Dict): Collection query result with keys:
            - metadatas (list[dict]): Metadata containing 'market' field

    Returns:
        Tuple[str, Optional[str]]:
            - str: Status message or description
            - Optional[str]: Chart path if successful, None on error

    Notes:
        - Shows feedback percentage per market (e.g. "C1-DE", "CE-IT")
        - Shows percentages on slices
        - Returns error if <2 markets (chart not useful)
    """
    try:
        print("   🎨 Erstelle Market Pie Chart...")
        sys.stdout.flush()

        metadatas = data["metadatas"]
        if not metadatas:
            return "❌ Keine Daten für Market-Chart", None

        markets = [m.get("market", "Unknown") for m in metadatas]
        market_counts = Counter(markets)

        print(f"   📊 Market-Verteilung: {dict(market_counts)}")
        sys.stdout.flush()

        plt.figure(figsize=(8, 6))
        
        labels = list(market_counts.keys())
        sizes = list(market_counts.values())
        colors = ["#3742fa", "#ff6348", "#2ed573", "#ffa502", "#747d8c", "#5f27cd"]  # Feste Farbpalette

        plt.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
        )
        plt.title("Feedback Distribution by Market", fontsize=14, fontweight="bold")
        plt.axis("equal")

        chart_path = get_chart_path("market_pie_distribution")
        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"   ✅ Chart gespeichert: {chart_path}")
        sys.stdout.flush()

        # Optimierte User-Ausgabe
        result = "🌍 **Markt-Verteilung (Kreisdiagramm)**\n\n"

        for market, count in market_counts.most_common():
            percentage = (count / len(metadatas)) * 100
            result += f"• **{market}**: {count:,} ({percentage:.1f}%)\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei create_market_pie_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def create_market_sentiment_breakdown(data: Dict) -> Tuple[str, Optional[str]]:
    """
    Creates grouped bar chart showing sentiment distribution per market.

    Args:
        data (Dict): Collection query result with keys:
            - metadatas (list[dict]): Metadata containing 'market' and 'sentiment_label' fields

    Returns:
        Tuple[str, Optional[str]]:
            - str: Status message or description
            - Optional[str]: Chart path if successful, None on error

    Notes:
        - Shows sentiment breakdown (positiv/neutral/negativ) for each market
        - Colors: Green (positiv), Yellow (neutral), Red (negativ)
        - Markets sorted alphabetically
        - Returns error if <2 markets (chart not useful)
    """
    try:
        print("   🎨 Erstelle Market Sentiment Breakdown...")
        sys.stdout.flush()

        metadatas = data["metadatas"]
        if not metadatas:
            return "❌ Keine Daten für Market-Sentiment-Chart", None

        # Gruppiere nach Market und Sentiment
        market_sentiment_data = {}
        for metadata in metadatas:
            market = metadata.get("market", "Unknown")
            sentiment = metadata.get("sentiment_label", "Unknown")
            
            if market not in market_sentiment_data:
                market_sentiment_data[market] = {"positiv": 0, "neutral": 0, "negativ": 0}
            
            if sentiment in market_sentiment_data[market]:
                market_sentiment_data[market][sentiment] += 1

        markets = list(market_sentiment_data.keys())
        sentiments = ["positiv", "neutral", "negativ"]
        
        print(f"   📊 Markets gefunden: {markets}")
        sys.stdout.flush()

        # Erstelle Grouped Bar Chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(markets))
        width = 0.25
        colors = ["#2ed573", "#feca57", "#ff6b6b"]  # Grün/Gelb/Rot

        for i, sentiment in enumerate(sentiments):
            counts = [market_sentiment_data[market][sentiment] for market in markets]
            bars = ax.bar(x + i * width, counts, width, label=sentiment.title(), color=colors[i])
            
            # Werte auf Balken
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2.0,
                        height + height * 0.01,
                        f"{int(height):,}",
                        ha="center",
                        va="bottom",
                        fontsize=9,
                    )

        ax.set_xlabel("Markets", fontweight="bold")
        ax.set_ylabel("Number of Feedbacks", fontweight="bold")
        ax.set_title("Sentiment Distribution by Market", fontsize=14, fontweight="bold")
        ax.set_xticks(x + width)
        ax.set_xticklabels(markets, rotation=45, ha="right")
        ax.legend()
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()

        chart_path = get_chart_path("market_sentiment_breakdown")
        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"   ✅ Chart gespeichert: {chart_path}")
        sys.stdout.flush()

        # Optimierte User-Ausgabe
        result = "🌍📊 **Sentiment-Verteilung pro Markt**\n\n"
        
        for market in markets:
            total = sum(market_sentiment_data[market].values())
            result += f"**{market}:**\n"
            for sentiment in sentiments:
                count = market_sentiment_data[market][sentiment]
                percentage = (count / total * 100) if total > 0 else 0
                result += f"  • {sentiment.title()}: {count:,} ({percentage:.1f}%)\n"
            result += "\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei create_market_sentiment_breakdown: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def create_market_nps_breakdown(data: Dict) -> Tuple[str, Optional[str]]:
    """
    Creates grouped bar chart showing NPS category distribution per market.

    Args:
        data (Dict): Collection query result with keys:
            - metadatas (list[dict]): Metadata containing 'market' and 'nps_category' fields

    Returns:
        Tuple[str, Optional[str]]:
            - str: Status message or description
            - Optional[str]: Chart path if successful, None on error

    Notes:
        - Shows NPS breakdown (Detractor/Passive/Promoter) for each market
        - Colors: Red (Detractor), Yellow (Passive), Green (Promoter)
        - Markets sorted alphabetically
        - Returns error if <2 markets (chart not useful)
    """
    try:
        print("   🎨 Erstelle Market NPS Breakdown...")
        sys.stdout.flush()

        metadatas = data["metadatas"]
        if not metadatas:
            return "❌ Keine Daten für Market-NPS-Breakdown", None

        market_nps_data = {}

        for metadata in metadatas:
            market = metadata.get("market", "Unknown")
            nps_category = metadata.get("nps_category", "Unknown")

            if market not in market_nps_data:
                market_nps_data[market] = {
                    "Detractor": 0,
                    "Passive": 0,
                    "Promoter": 0,
                    "Unknown": 0,
                }

            if nps_category in market_nps_data[market]:
                market_nps_data[market][nps_category] += 1
            else:
                market_nps_data[market]["Unknown"] += 1

        markets = list(market_nps_data.keys())
        categories = ["Detractor", "Passive", "Promoter"]

        print(f"   📊 {len(markets)} Markets, {len(categories)} Kategorien")
        sys.stdout.flush()

        if len(markets) == 1:
            # Single market: Pie + Bar chart
            market = markets[0]
            market_data = market_nps_data[market]

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

            sizes = [market_data.get(cat, 0) for cat in categories]
            colors = ["#ff6b6b", "#feca57", "#2ed573"]  # Rot/Gelb/Grün

            wedges, texts, autotexts = ax1.pie(
                sizes,
                labels=categories,
                autopct="%1.1f%%",
                colors=colors,
                startangle=90,
            )
            ax1.set_title(
                f"NPS Distribution for {market}", fontsize=14, fontweight="bold"
            )

            bars = ax2.bar(categories, sizes, color=colors, alpha=0.8)
            ax2.set_title(
                f"Absolute Numbers for {market}", fontsize=14, fontweight="bold"
            )
            ax2.set_ylabel("Number of Customers", fontweight="bold")
            ax2.grid(axis="y", alpha=0.3)

            for bar in bars:
                height = bar.get_height()
                ax2.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + height * 0.01,
                    f"{int(height):,}",
                    ha="center",
                    va="bottom",
                    fontsize=11,
                    fontweight="bold",
                )

            chart_filename = "market_nps_single_breakdown"

        else:
            # Multiple markets: Grouped bar chart
            data_matrix = []
            for category in categories:
                data_matrix.append(
                    [market_nps_data[market].get(category, 0) for market in markets]
                )

            x = np.arange(len(markets))
            width = 0.25
            colors = ["#ff6b6b", "#feca57", "#2ed573"]

            fig, ax = plt.subplots(figsize=(14, 7))

            for i, (category, data_row) in enumerate(zip(categories, data_matrix)):
                bars = ax.bar(
                    x + i * width, data_row, width, label=category, color=colors[i]
                )

                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(
                            bar.get_x() + bar.get_width() / 2.0,
                            height + height * 0.01,
                            f"{int(height):,}",
                            ha="center",
                            va="bottom",
                            fontsize=9,
                        )

            ax.set_xlabel("Markets", fontweight="bold")
            ax.set_ylabel("Number of Customers", fontweight="bold")
            ax.set_title("NPS Category Distribution by Market", fontsize=14, fontweight="bold")
            ax.set_xticks(x + width)
            ax.set_xticklabels(markets, rotation=45, ha="right")
            ax.legend()
            ax.grid(axis="y", alpha=0.3)

            chart_filename = "market_nps_breakdown"

        plt.tight_layout()

        chart_path = get_chart_path(chart_filename)
        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"   ✅ Chart gespeichert: {chart_path}")
        sys.stdout.flush()

        # User-Ausgabe
        result = "🌍⭐ **NPS-Verteilung pro Markt**\n\n"
        
        for market in markets:
            total = sum(market_nps_data[market].values())
            result += f"**{market}:**\n"
            for category in categories:
                count = market_nps_data[market][category]
                percentage = (count / total * 100) if total > 0 else 0
                result += f"  • {category}: {count:,} ({percentage:.1f}%)\n"
            result += "\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei create_market_nps_breakdown: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None
