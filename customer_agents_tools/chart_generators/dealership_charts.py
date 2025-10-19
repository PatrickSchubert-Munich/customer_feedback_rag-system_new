"""
Dealership Chart Generators

Creates charts for dealership mention analysis and provides dealership extraction functionality.
"""

import sys
import re
import traceback
from typing import Dict, Tuple, Optional, Any
from collections import Counter

from ._shared import get_chart_path, plt


def analyze_dealerships(
    collection,
    sentiment_filter: str | None = None,
    nps_filter: str | None = None,
    market_filter: str | None = None,
    topic_filter: str | None = None,
    min_mentions: int = 1
) -> Dict[str, Any]:
    """
    Analyzes dealership mentions in customer feedback.
    
    IMPORTANT: Dealership names are NOT stored as structured metadata!
    This tool searches through verbatim text to find dealership mentions.
    
    Args:
        collection: ChromaDB collection with customer feedback
        sentiment_filter: Filter by sentiment ('positiv', 'neutral', 'negativ')
        nps_filter: Filter by NPS category ('Promoter', 'Passive', 'Detractor')
        market_filter: Filter by market (e.g., 'C1-DE', 'C3-CN')
        topic_filter: Filter by topic (e.g., 'Service & Beratung', 'Werkstattservice')
        min_mentions: Minimum number of mentions to include (default: 1)
        
    Returns:
        Dict with:
            - dealership_counts: Dict mapping dealership names to mention counts
            - total_feedbacks_analyzed: Total number of feedback documents analyzed
            - filtered_by: Applied filters
            - top_dealerships: Top 10 dealerships by mention count
            
    Example Response:
        {
            "dealership_counts": {
                "Autohaus Goldgrube": 15,
                "Werkstatt Blitzblank": 12,
                "AutoCenter Regenbogen": 10
            },
            "total_feedbacks_analyzed": 523,
            "filtered_by": {
                "sentiment": "negativ",
                "market": "C1-DE"
            },
            "top_dealerships": [
                {"name": "Autohaus Goldgrube", "count": 15},
                {"name": "Werkstatt Blitzblank", "count": 12}
            ]
        }
    """
    # Common dealership patterns in verbatim text (from synthetic_data_generator.py)
    DEALERSHIP_PATTERNS = [
        # Fun mode dealerships
        r"Autohaus Sonnenschein", r"Werkstatt Blitzblank", r"AutoCenter Regenbogen",
        r"Motorwelt Sternschnuppe", r"Autohaus Glücksklee", r"Service-Center Traumwagen",
        r"Autopark Wunderland", r"Werkstatt Meisterhaft", r"AutoPalast König",
        r"Fahrzeugwelt Paradies", r"Autohaus Goldgrube", r"Service-Oase Wüstenfuchs",
        r"Motorhof Edelstein", r"Autohaus Zeitreise", r"Werkstatt Turbozauber",
        r"AutoArena Champion", r"Servicewelt Premiumglanz", r"Autohaus Meilenstein",
        r"Werkstatt Schraubenkönig", r"Motorreich Vollgas", r"Autohaus Freudensprung",
        r"Service-Station Rakete", r"Autowelt Horizont", r"Werkstatt Präzision Plus",
        r"Autohaus Vertrauenssache",
        
        # Standard mode dealerships
        r"Autohaus Müller", r"Werkstatt Schmidt", r"AutoCenter Weber",
        r"Motorwelt Fischer", r"Autohaus Wagner", r"Service-Center Becker",
        r"Autopark Schulz", r"Werkstatt Hoffmann", r"AutoPalast König"
    ]
    
    # Build metadata filter
    where_filter = {}
    if sentiment_filter:
        where_filter["sentiment_label"] = sentiment_filter
    if nps_filter:
        where_filter["nps_category"] = nps_filter
    if market_filter:
        where_filter["Market"] = market_filter
    if topic_filter:
        where_filter["topic"] = topic_filter
    
    # Query collection
    try:
        if where_filter:
            results = collection.get(
                where=where_filter,
                include=["documents", "metadatas"]
            )
        else:
            results = collection.get(
                include=["documents", "metadatas"]
            )
    except Exception as e:
        return {
            "error": f"Failed to query collection: {str(e)}",
            "dealership_counts": {},
            "total_feedbacks_analyzed": 0
        }
    
    documents = results.get("documents", [])
    total_analyzed = len(documents)
    
    # Extract dealership names from verbatim text
    dealership_mentions = []
    
    for doc in documents:
        if not doc:
            continue
            
        # Search for each dealership pattern
        for pattern in DEALERSHIP_PATTERNS:
            matches = re.findall(pattern, doc, re.IGNORECASE)
            dealership_mentions.extend(matches)
    
    # Count mentions
    dealership_counter = Counter(dealership_mentions)
    
    # Filter by minimum mentions
    dealership_counts = {
        name: count 
        for name, count in dealership_counter.items() 
        if count >= min_mentions
    }
    
    # Get top 10 dealerships
    top_dealerships = [
        {"name": name, "count": count}
        for name, count in dealership_counter.most_common(10)
        if count >= min_mentions
    ]
    
    # Build filter summary
    applied_filters = {}
    if sentiment_filter:
        applied_filters["sentiment"] = sentiment_filter
    if nps_filter:
        applied_filters["nps_category"] = nps_filter
    if market_filter:
        applied_filters["market"] = market_filter
    if topic_filter:
        applied_filters["topic"] = topic_filter
    
    return {
        "dealership_counts": dealership_counts,
        "total_feedbacks_analyzed": total_analyzed,
        "filtered_by": applied_filters if applied_filters else "No filters applied",
        "top_dealerships": top_dealerships,
        "unique_dealerships_found": len(dealership_counts)
    }


def create_dealership_bar_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """
    Creates horizontal bar chart showing dealership mention frequency.
    
    IMPORTANT: Extracts dealership names from verbatim text (not structured metadata).
    
    Args:
        data (Dict): Collection query result with keys:
            - documents (list[str]): Verbatim feedback texts
            
    Returns:
        Tuple[str, Optional[str]]:
            - str: Status message or description
            - Optional[str]: Chart path if successful, None on error
    """
    try:
        documents = data.get("documents", [])
        
        if not documents:
            return "ℹ️ Keine Feedbacks gefunden.", None
        
        # Dealership patterns from synthetic_data_generator.py
        dealership_patterns = [
            r"Autohaus Sonnenschein", r"Werkstatt Blitzblank", r"AutoCenter Regenbogen",
            r"Motorwelt Sternschnuppe", r"Autohaus Glücksklee", r"Service-Center Traumwagen",
            r"Autopark Wunderland", r"Werkstatt Meisterhaft", r"AutoPalast König",
            r"Fahrzeugwelt Paradies", r"Autohaus Goldgrube", r"Service-Oase Wüstenfuchs",
            r"Motorhof Edelstein", r"Autohaus Zeitreise", r"Werkstatt Turbozauber",
            r"AutoArena Champion", r"Servicewelt Premiumglanz", r"Autohaus Meilenstein",
            r"Werkstatt Schraubenkönig", r"Motorreich Vollgas", r"Autohaus Freudensprung",
            r"Service-Station Rakete", r"Autowelt Horizont", r"Werkstatt Präzision Plus",
            r"Autohaus Vertrauenssache",
            r"Autohaus Müller", r"Werkstatt Schmidt", r"AutoCenter Weber",
            r"Motorwelt Fischer", r"Autohaus Wagner", r"Service-Center Becker",
            r"Autopark Schulz", r"Werkstatt Hoffmann"
        ]
        
        # Extract dealerships from verbatim text
        dealership_mentions = []
        for doc in documents:
            if not doc:
                continue
            for pattern in dealership_patterns:
                matches = re.findall(pattern, doc, re.IGNORECASE)
                dealership_mentions.extend(matches)
        
        if not dealership_mentions:
            return "ℹ️ Keine Dealership-Erwähnungen im Verbatim-Text gefunden.", None
        
        dealership_counts = Counter(dealership_mentions)
        
        # Get top 15 dealerships
        top_dealerships = dealership_counts.most_common(15)
        
        # Create chart
        dealership_names = [name for name, _ in reversed(top_dealerships)]
        counts = [count for _, count in reversed(top_dealerships)]
        
        plt.figure(figsize=(12, max(6, len(dealership_names) * 0.4)))
        bars = plt.barh(dealership_names, counts, color="#3742fa")
        
        # Add count labels
        for bar in bars:
            width = bar.get_width()
            plt.text(
                width, bar.get_y() + bar.get_height() / 2,
                f" {int(width)}",
                va="center", fontsize=10, fontweight="bold"
            )
        
        plt.xlabel("Anzahl Erwähnungen", fontsize=12, fontweight="bold")
        plt.ylabel("Dealership", fontsize=12, fontweight="bold")
        plt.title("Dealership-Erwähnungen in Feedbacks", fontsize=14, fontweight="bold")
        plt.grid(axis="x", alpha=0.3, linestyle="--")
        plt.tight_layout()
        
        chart_path = get_chart_path("dealership_bar_distribution")
        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()
        
        print(f"   ✅ Dealership-Chart gespeichert: {chart_path}")
        sys.stdout.flush()
        
        # User output
        result = "🏢 **Dealership-Erwähnungen (Balkendiagramm)**\n\n"
        result += f"**Top {len(top_dealerships)} Dealerships:**\n\n"
        
        for name, count in dealership_counts.most_common(15):
            percentage = (count / len(dealership_mentions)) * 100
            result += f"• **{name}**: {count} Erwähnungen ({percentage:.1f}%)\n"
        
        result += f"\n📊 Gesamt: {len(dealership_mentions)} Erwähnungen in {len(documents)} Feedbacks"
        
        return result, chart_path
        
    except Exception as e:
        error_msg = f"❌ Fehler bei create_dealership_bar_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None
