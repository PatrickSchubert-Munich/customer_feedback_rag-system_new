import os
import sys
import traceback
from typing import Optional, Dict, Any
from datetime import datetime
from langchain_chroma import Chroma
from agents import function_tool

# Import modular chart generators
from .chart_generators import (
    create_sentiment_bar_chart,
    create_sentiment_pie_chart,
    create_nps_bar_chart,
    create_nps_pie_chart,
    create_market_bar_chart,
    create_market_pie_chart,
    create_market_sentiment_breakdown,
    create_market_nps_breakdown,
    create_topic_bar_chart,
    create_topic_pie_chart,
    create_dealership_bar_chart,
    create_time_analysis,
    create_overview_charts,
)


def create_chart_creation_tool(collection: Chroma):
    """
    Factory for feedback_analytics tool with injected collection.

    Args:
        collection: ChromaDB Collection (reference!)

    Returns:
        function_tool: Configured Analytics Tool
    """

    # ✅ DEBUG: Validiere Collection beim Tool-Erstellen
    print("\n🔧 Creating Analytics Tool...")
    print(f"   • Collection: {collection}")
    print(f"   • Collection Type: {type(collection)}")
    if collection:
        try:
            count = collection.count()  # type: ignore[attr-defined]
            print(f"   • Collection Count: {count}")
        except Exception as e:
            print(f"   ⚠️ Collection Count Error: {e}")
    print()
    sys.stdout.flush()

    @function_tool
    def feedback_analytics(
        analysis_type: str = "sentiment_chart",
        query: str = "",
        market_filter: Optional[str] = None,
        region_filter: Optional[str] = None,
        country_filter: Optional[str] = None,
        sentiment_filter: Optional[str] = None,
        nps_filter: Optional[str] = None,
        topic_filter: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> str:
        """
        Creates visualizations from customer feedback data.

        Args:
            analysis_type (str): Chart type. Options:
                Sentiment: "sentiment_bar_chart", "sentiment_pie_chart"
                NPS: "nps_bar_chart", "nps_pie_chart"
                Market: "market_bar_chart", "market_pie_chart", 
                       "market_sentiment_breakdown", "market_nps_breakdown"
                Topic: "topic_bar_chart", "topic_pie_chart"
                Dealership: "dealership_bar_chart", "dealership_pie_chart"
                    NOTE: Extracts dealership names from verbatim text (not metadata)
                Special: 
                  - "time_analysis": Comprehensive timeline (4 charts: volume, sentiment, NPS trends)
                    Best for: "letzte X Monate", "Entwicklung", "Trend über Zeit"
                  - "overview": Dashboard with multiple metrics
                Default: "sentiment_chart"
            
            query (str, optional): Semantic filter query (e.g. "Lieferprobleme").
                Empty = all data. Default: ""
            
            market_filter (str, optional): Market filter (e.g. "C1-DE"). 
                None = all markets. Default: None
            
            region_filter (str, optional): Region filter (e.g. "C1", "CE"). 
                None = all regions. Default: None
            
            country_filter (str, optional): Country filter (ISO code e.g. "DE", "IT"). 
                None = all countries. Default: None
            
            sentiment_filter (str, optional): Sentiment filter 
                ("positiv"/"negativ"/"neutral" - German values!). Default: None
            
            nps_filter (str, optional): NPS category 
                ("Promoter"/"Passive"/"Detractor"). Default: None
            
            topic_filter (str, optional): Topic filter 
                (e.g. "Service", "Lieferproblem", "Produktqualität" - German values!). 
                Default: None
            
            date_from (str, optional): Start date "YYYY-MM-DD". Default: None
            date_to (str, optional): End date "YYYY-MM-DD". Default: None

        Returns:
            str: Text description + chart path in format:
                "[Description]\\n__CHART__[path.png]__CHART__"
                On errors: "❌ Error: ..." or "ℹ️ Keine Daten..."

        Examples:
            >>> feedback_analytics("sentiment_pie_chart", market_filter="C1-DE")
            "Sentiment-Verteilung für C1-DE\\n__CHART__charts/sentiment_...png__CHART__"
            
            >>> feedback_analytics("nps_bar_chart", query="Service")
            "NPS-Kategorien für 'Service'\\n__CHART__charts/nps_...png__CHART__"

        Notes:
            - IMPORTANT: Filter values are in GERMAN (data compatibility)
              sentiment_filter: "positiv", "negativ", "neutral"
              topic_filter: "Lieferproblem", "Service", "Terminvergabe", etc.
            - __CHART__ marker is critical for UI parsing
            - Auto-fallback for invalid analysis_type (query-based)
            - Smart validation prevents meaningless charts (e.g. Market chart with 1 market)
        """
        try:
            # ✅ DEBUG: Log Tool-Aufruf
            print(f"\n{'=' * 60}")
            print("🎨 ANALYTICS TOOL AUFGERUFEN")
            print(f"{'=' * 60}")
            print(f"   • analysis_type: {analysis_type}")
            print(f"   • query: '{query}'")
            print(f"   • market_filter: {market_filter}")
            print(f"   • sentiment_filter: {sentiment_filter}")
            print(f"   • nps_filter: {nps_filter}")
            print(f"   • date_from: {date_from}")
            print(f"   • date_to: {date_to}")
            print(f"   • collection: {collection}")
            print(f"{'=' * 60}")
            sys.stdout.flush()

            # ✅ Validierung: Collection Check
            if not collection:
                error_msg = "❌ Error: Vectorstore nicht verfügbar (collection is None)"
                print(f"\n{error_msg}\n")
                sys.stdout.flush()
                return error_msg

            # ✅ Validierung: Collection Count
            try:
                collection_count = collection.count()  # type: ignore[attr-defined]
                print(f"\n✅ Collection hat {collection_count} Dokumente")
                sys.stdout.flush()
            except Exception as e:
                error_msg = f"❌ Error: Collection count fehlgeschlagen: {str(e)}"
                print(f"\n{error_msg}\n")
                traceback.print_exc()
                sys.stdout.flush()
                return error_msg

            # ✅ INFO: Warnung bei komplett leeren Parametern
            if (not query.strip() and 
                not market_filter and not region_filter and not country_filter and
                not sentiment_filter and not nps_filter and not topic_filter and
                not date_from and not date_to):
                print("\n📊 INFO: Keine spezifischen Filter gesetzt - erstelle Chart über ALLE Daten")
                print("   💡 Tipp: Für fokussiertere Analysen können Filter verwendet werden:")
                print("      • market_filter, region_filter, country_filter (geografisch)")
                print("      • sentiment_filter, nps_filter, topic_filter (analytisch)")
                print("      • date_from, date_to (zeitlich)")
                print("      • query (semantische Filterung)\n")
                sys.stdout.flush()

            # ✅ Validierung: analysis_type mit FALLBACK
            valid_types = [
                "sentiment_bar_chart",
                "sentiment_pie_chart",
                "nps_bar_chart",
                "nps_pie_chart",
                "market_bar_chart",
                "market_pie_chart",
                "topic_bar_chart",
                "topic_pie_chart",
                "dealership_bar_chart",
                "market_sentiment_breakdown",
                "market_nps_breakdown",
                "time_analysis",
                "overview",
            ]

            if analysis_type not in valid_types:
                print(f"⚠️ Ungültiger analysis_type: '{analysis_type}' - versuche Fallback...")
                sys.stdout.flush()
                
                # 🧠 FALLBACK: Versuche aus query zu erraten
                query_lower = query.lower()
                
                if "sentiment" in query_lower or "stimmung" in query_lower:
                    if "balken" in query_lower or "bar" in query_lower:
                        analysis_type = "sentiment_bar_chart"
                        print(f"✅ Fallback: Query enthält 'Sentiment' + 'Balken' → sentiment_bar_chart")
                    else:
                        analysis_type = "sentiment_pie_chart"
                        print(f"✅ Fallback: Query enthält 'Sentiment' → sentiment_pie_chart")
                    sys.stdout.flush()
                    
                elif "nps" in query_lower or "promoter" in query_lower or "detractor" in query_lower:
                    if "balken" in query_lower or "bar" in query_lower:
                        analysis_type = "nps_bar_chart"
                        print(f"✅ Fallback: Query enthält 'NPS' + 'Balken' → nps_bar_chart")
                    else:
                        analysis_type = "nps_pie_chart"
                        print(f"✅ Fallback: Query enthält 'NPS' → nps_pie_chart")
                    sys.stdout.flush()
                    
                elif "markt" in query_lower or "market" in query_lower or "region" in query_lower:
                    # Prüfe, ob Sentiment oder NPS im Context
                    if "sentiment" in query_lower:
                        analysis_type = "market_sentiment_breakdown"
                        print(f"✅ Fallback: Query enthält 'Markt' + 'Sentiment' → market_sentiment_breakdown")
                    elif "nps" in query_lower:
                        analysis_type = "market_nps_breakdown"
                        print(f"✅ Fallback: Query enthält 'Markt' + 'NPS' → market_nps_breakdown")
                    elif "balken" in query_lower or "bar" in query_lower:
                        analysis_type = "market_bar_chart"
                        print(f"✅ Fallback: Query enthält 'Markt' + 'Balken' → market_bar_chart")
                    else:
                        analysis_type = "market_pie_chart"  # Default für Markt-Volumen
                        print(f"✅ Fallback: Query enthält 'Markt' → market_pie_chart")
                    sys.stdout.flush()
                    
                elif ("zeit" in query_lower or "time" in query_lower or "trend" in query_lower or
                      "entwicklung" in query_lower or "verlauf" in query_lower or 
                      "monat" in query_lower or "woche" in query_lower or
                      "zeitreihe" in query_lower or "temporal" in query_lower):
                    analysis_type = "time_analysis"
                    print(f"✅ Fallback: Query enthält zeitbezogene Keywords → time_analysis")
                    sys.stdout.flush()
                    
                elif "überblick" in query_lower or "overview" in query_lower or "dashboard" in query_lower:
                    analysis_type = "overview"
                    print(f"✅ Fallback: Query enthält 'Überblick' → overview")
                    sys.stdout.flush()
                    
                else:
                    # Kein Fallback möglich
                    error_msg = f"❌ Error: Ungültiger analysis_type '{analysis_type}' und kein Fallback möglich. Gültig: {', '.join(valid_types)}"
                    print(f"\n{error_msg}\n")
                    sys.stdout.flush()
                    return error_msg

            # ✅ Get filtered data
            print("\n📊 Hole gefilterte Daten aus ChromaDB...")
            sys.stdout.flush()

            data = _get_filtered_data(
                collection, query, market_filter, region_filter, country_filter,
                sentiment_filter, nps_filter, topic_filter, date_from, date_to
            )

            if not data["documents"]:
                msg = "ℹ️ Keine Daten für Analyse gefunden (Filter zu restriktiv?)"
                print(f"\n{msg}\n")
                sys.stdout.flush()
                return msg

            print(f"✅ {len(data['documents'])} Dokumente gefunden")
            sys.stdout.flush()
            
            # ════════════════════════════════════════════════════════════════
            # 🧠 SMART CHART-TYPE VALIDATION (Data-Aware Logic)
            # ════════════════════════════════════════════════════════════════
            # ZWECK: Verhindert sinnlose Charts BEVOR sie erstellt werden
            # Beispiel: 1 Markt → market_chart zeigt nur 1 Balken → sinnlos!
            # ════════════════════════════════════════════════════════════════
            
            # Zähle unique markets in den Daten
            unique_markets = set()
            for metadata in data.get("metadatas", []):
                if metadata and "market" in metadata:
                    unique_markets.add(metadata["market"])
            
            market_count = len(unique_markets)
            print(f"\n🔍 SMART VALIDATION: {market_count} eindeutige Märkte gefunden")
            sys.stdout.flush()
            
            # REGEL 1: Market-Charts mit nur 1 Markt machen keinen Sinn
            query_lower = query.lower()
            if analysis_type in ["market_bar_chart", "market_pie_chart", "market_sentiment_breakdown", "market_nps_breakdown"] and market_count == 1:
                print(f"⚠️ OVERRIDE: {analysis_type} mit nur 1 Markt → Switching to sentiment chart")
                sys.stdout.flush()
                
                # Prüfe, ob User explizit "Balken" will
                if "balken" in query_lower or "bar" in query_lower:
                    analysis_type = "sentiment_bar_chart"  # Bar Chart
                else:
                    analysis_type = "sentiment_pie_chart"  # Pie Chart (default)
                
                print(f"✅ Chart-Typ geändert zu: {analysis_type}")
                sys.stdout.flush()
            
            # REGEL 2: Wenn Query "Sentiment" UND "Markt" enthält → market_sentiment_breakdown
            if "sentiment" in query_lower and "markt" in query_lower and market_count > 1:
                if analysis_type in ["market_bar_chart", "market_pie_chart"]:
                    print("⚠️ OVERRIDE: Query enthält 'Sentiment' + 'Markt' → market_sentiment_breakdown")
                    analysis_type = "market_sentiment_breakdown"
                    print(f"✅ Chart-Typ geändert zu: {analysis_type}")
                    sys.stdout.flush()
                print(f"✅ Chart-Typ geändert zu: {analysis_type}")
                sys.stdout.flush()
            
            print(f"✅ Finaler Chart-Typ: {analysis_type}")
            sys.stdout.flush()

            # ✅ Create requested visualization using modular chart generators
            print(f"\n🎨 Erstelle Chart: {analysis_type}")
            sys.stdout.flush()

            if analysis_type == "sentiment_bar_chart":
                text_result, chart_path = create_sentiment_bar_chart(data)
            elif analysis_type == "sentiment_pie_chart":
                text_result, chart_path = create_sentiment_pie_chart(data)
            elif analysis_type == "nps_bar_chart":
                text_result, chart_path = create_nps_bar_chart(data)
            elif analysis_type == "nps_pie_chart":
                text_result, chart_path = create_nps_pie_chart(data)
            elif analysis_type == "market_bar_chart":
                text_result, chart_path = create_market_bar_chart(data)
            elif analysis_type == "market_pie_chart":
                text_result, chart_path = create_market_pie_chart(data)
            elif analysis_type == "topic_bar_chart":
                text_result, chart_path = create_topic_bar_chart(data)
            elif analysis_type == "topic_pie_chart":
                text_result, chart_path = create_topic_pie_chart(data)
            elif analysis_type == "dealership_bar_chart":
                text_result, chart_path = create_dealership_bar_chart(data)
            elif analysis_type == "market_sentiment_breakdown":
                text_result, chart_path = create_market_sentiment_breakdown(data)
            elif analysis_type == "market_nps_breakdown":
                text_result, chart_path = create_market_nps_breakdown(data)
            elif analysis_type == "time_analysis":
                text_result, chart_path = create_time_analysis(data)
            elif analysis_type == "overview":
                text_result, chart_path = create_overview_charts(data)
            else:
                return f"❌ Unbekannter Chart-Typ: {analysis_type}"

            # ✅ Chart-Marker für Streamlit-Parser hinzufügen
            if chart_path and os.path.exists(chart_path):
                final_result = f"{text_result}\n__CHART__{chart_path}__CHART__"
                return final_result
            else:
                return text_result

        except Exception as e:
            error_msg = f"❌ KRITISCHER FEHLER bei Analytics: {str(e)}"
            print(f"\n{'=' * 60}")
            print(error_msg)
            print(f"{'=' * 60}")
            traceback.print_exc()
            print(f"{'=' * 60}\n")
            sys.stdout.flush()
            return error_msg

    return feedback_analytics


# ═════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS (Unverändert, da reine Implementierung)
# ═════════════════════════════════════════════════════════════════════════════


def _get_chart_path(chart_name: str) -> str:
    """
    Creates unique chart path with timestamp.

    Args:
        chart_name (str): Base name for chart file (e.g. "sentiment_bar", "nps_pie").

    Returns:
        str: Absolute path to chart file in charts/ directory.
            Format: "charts/{chart_name}_{timestamp}.png"
            Example: "charts/sentiment_bar_20231015_143022_12.png"

    Notes:
        - Uses ABSOLUTE path for secure Streamlit display
        - Timestamp format: YYYYMMDD_HHMMSS_MS (17 chars)
        - Auto-creates charts/ directory if not exists
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:17]
    chart_filename = f"{chart_name}_{timestamp}.png"

    chart_dir = "charts"
    os.makedirs(chart_dir, exist_ok=True)

    # ✅ Nutze os.path.join für OS-unabhängigen Pfad
    chart_path = os.path.join(chart_dir, chart_filename)
    
    # ✅ KRITISCH: Konvertiere zu ABSOLUTEM Pfad für Streamlit
    chart_path = os.path.abspath(chart_path)

    # ✅ KRITISCH: Konvertiere zu Forward Slashes für Streamlit/Web
    chart_path = chart_path.replace("\\", "/")

    print(f"   📁 Chart wird gespeichert als: {chart_path}")
    sys.stdout.flush()

    return chart_path


def _get_filtered_data(
    collection: Chroma,
    query: str,
    market_filter: Optional[str],
    region_filter: Optional[str],
    country_filter: Optional[str],
    sentiment_filter: Optional[str],
    nps_filter: Optional[str],
    topic_filter: Optional[str],
    date_from: Optional[str],
    date_to: Optional[str],
) -> Dict:
    """
    Fetches filtered data from collection with extended filters.
    
    Args:
        collection (Chroma): ChromaDB collection instance.
        query (str): Semantic search query (empty = all data).
        market_filter (str | None): Market filter (e.g. "C1-DE").
        region_filter (str | None): Region filter (e.g. "C1", "CE").
        country_filter (str | None): Country filter (ISO code, e.g. "DE").
        sentiment_filter (str | None): Sentiment ("positiv"/"negativ"/"neutral").
        nps_filter (str | None): NPS category ("Promoter"/"Passive"/"Detractor").
        topic_filter (str | None): Topic (e.g. "Service", "Lieferproblem").
        date_from (str | None): Start date "YYYY-MM-DD".
        date_to (str | None): End date "YYYY-MM-DD".

    Returns:
        Dict: Collection query result with keys:
            - ids (list[str]): Document IDs
            - metadatas (list[dict]): Metadata for each document
            - documents (list[str]): Verbatim texts
            - distances (list[float] | None): Similarity scores (if query used)

    Notes:
        - Supports filtering by: Market, Region, Country, Sentiment, NPS, Topic, Date
        - Empty query: Returns all documents matching filters
        - Semantic query: Returns top 1000 most relevant results
        - Date filters use $gte (>=) and $lte (<=) operators
    """
    try:
        print("   🔍 Filter-Setup:")
        print(f"      • Market: {market_filter}")
        print(f"      • Region: {region_filter}")
        print(f"      • Country: {country_filter}")
        print(f"      • Sentiment: {sentiment_filter}")
        print(f"      • NPS: {nps_filter}")
        print(f"      • Topic: {topic_filter}")
        print(f"      • Date From: {date_from}")
        print(f"      • Date To: {date_to}")
        print(f"      • Query: '{query}'")
        sys.stdout.flush()

        # Build filters
        where_filter = {}

        if market_filter:
            where_filter["market"] = {"$eq": market_filter}

        if region_filter:
            where_filter["region"] = {"$eq": region_filter}

        if country_filter:
            where_filter["country"] = {"$eq": country_filter}

        if sentiment_filter:
            where_filter["sentiment_label"] = {"$eq": sentiment_filter.lower()}
        
        if nps_filter:
            where_filter["nps_category"] = {"$eq": nps_filter}
        
        if topic_filter:
            where_filter["topic"] = {"$eq": topic_filter}
        
        # Date range filtering - build separate conditions for ChromaDB
        date_conditions = []
        if date_from or date_to:
            from datetime import datetime
            
            if date_from:
                try:
                    date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
                    timestamp_from = int(date_from_obj.timestamp())
                    date_conditions.append({"date": {"$gte": timestamp_from}})
                    print(f"      ⏰ Date From: {date_from} → {timestamp_from}")
                except ValueError as e:
                    print(f"      ⚠️ Invalid date_from format: {date_from} (expected YYYY-MM-DD)")
            
            if date_to:
                try:
                    date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
                    # Set to end of day (23:59:59)
                    timestamp_to = int(date_to_obj.timestamp()) + 86399
                    date_conditions.append({"date": {"$lte": timestamp_to}})
                    print(f"      ⏰ Date To: {date_to} → {timestamp_to}")
                except ValueError as e:
                    print(f"      ⚠️ Invalid date_to format: {date_to} (expected YYYY-MM-DD)")

        # Combine filters with $and operator
        # ChromaDB requires separate conditions for multiple operators on same field
        filter_list = []
        for key, value in where_filter.items():
            filter_list.append({key: value})
        
        # Add date conditions separately (each operator needs own dict)
        filter_list.extend(date_conditions)
        
        if len(filter_list) > 1:
            where_filter = {"$and": filter_list}
        elif len(filter_list) == 1:
            where_filter = filter_list[0]
        else:
            where_filter = None

        print(f"   🔧 ChromaDB Filter: {where_filter}")
        sys.stdout.flush()

        # Query data
        if query.strip():
            print("   🔎 Führe semantic search aus...")
            sys.stdout.flush()

            # Type hint: Chroma hat query() zur Laufzeit, auch wenn Pylance es nicht sieht
            result: Any = collection.query(  # type: ignore[attr-defined]
                query_texts=[query.strip()],
                n_results=10000,
                where=where_filter,
                include=["documents", "metadatas"],
            )

            if result and "documents" in result and result["documents"][0]:
                documents = result["documents"][0]
                metadatas = result["metadatas"][0] if result["metadatas"] else []
            else:
                documents, metadatas = [], []
        else:
            print("   📚 Führe get() aus (keine query)...")
            sys.stdout.flush()

            # Warnung wenn keine Filter gesetzt sind
            if where_filter is None:
                print("   ℹ️ INFO: Keine Filter gesetzt - hole alle verfügbaren Daten")
                sys.stdout.flush()
            
            result: Any = collection.get(
                where=where_filter,  # type: ignore[arg-type]
                include=["documents", "metadatas"]
            )
            documents = result.get("documents", [])
            metadatas = result.get("metadatas", [])

        print(f"   ✅ {len(documents)} Dokumente gefunden")
        sys.stdout.flush()

        return {"documents": documents, "metadatas": metadatas}

    except Exception as e:
        print(f"   ❌ Fehler bei _get_filtered_data: {str(e)}")
        traceback.print_exc()
        sys.stdout.flush()
        return {"documents": [], "metadatas": []}
