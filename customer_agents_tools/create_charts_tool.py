"""
Analytics Tools - Factory Pattern für Collection Injection
Alle Visualisierungs-Tools für den Analytics Agent
Mit Streamlit-Integration
Mit umfassendem Debugging und Error-Handling

WICHTIGE ÄNDERUNGEN (PRIO 1 Optimierung):
- Vollständige Docstrings mit Args, Returns, Examples
- Exit-Marker explizit definiert (__CHART__, Emojis, Fehler)
- Fehlerbehandlung dokumentiert
- Default-Verhalten beschrieben
"""

import os
import sys
import traceback
from typing import Optional, Dict, Tuple, Any
from collections import Counter, defaultdict
from datetime import datetime
from langchain_chroma import Chroma
from agents import function_tool
import matplotlib
import matplotlib.pyplot as plt

# Non-interactive backend für Server
matplotlib.use("Agg")


def create_chart_creation_tool(collection: Chroma):
    """
    Factory für feedback_analytics Tool mit injizierter Collection.

    Args:
        collection: ChromaDB Collection (Referenz!)

    Returns:
        function_tool: Konfiguriertes Analytics Tool
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
        sentiment_filter: Optional[str] = None,
        nps_filter: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> str:
        """
        Erstellt Visualisierungen aus Customer-Feedback-Daten.

        Args:
            analysis_type: Chart-Typ. Optionen:
                - "sentiment_bar_chart": Sentiment-Verteilung als BALKENCHART
                - "sentiment_pie_chart": Sentiment-Verteilung als KREISDIAGRAMM
                - "nps_bar_chart": NPS-Kategorien als BALKENCHART
                - "nps_pie_chart": NPS-Kategorien als KREISDIAGRAMM
                - "market_bar_chart": Feedback-Volumen pro Markt (Balkenchart)
                - "market_pie_chart": Feedback-Anteile pro Markt (Kreisdiagramm)
                - "market_sentiment_breakdown": Sentiment-Verteilung pro Markt (Grouped Bar)
                - "market_nps_breakdown": NPS-Kategorien pro Markt (Grouped Bar)
                - "time_analysis": Zeitliche Entwicklung (4-Panel Dashboard)
                - "overview": Gesamt-Überblick (4-Panel Dashboard)
            
            query: Semantische Suche zur Filterung (z.B. "Lieferprobleme"). 
                   Leer = alle Daten.
            
            market_filter: Filtere nach Markt (z.B. "C1-DE"). None = alle Märkte.
            
            sentiment_filter: Filtere nach Sentiment ("positiv"/"negativ"/"neutral"). 
                             None = alle Sentiments.
            
            nps_filter: Filtere nach NPS-Kategorie ("Promoter"/"Passive"/"Detractor").
                       None = alle Kategorien.
            
            date_from: Start-Datum im Format "YYYY-MM-DD" (z.B. "2024-01-01").
                      None = kein Start-Filter.
            
            date_to: End-Datum im Format "YYYY-MM-DD" (z.B. "2024-12-31").
                    None = kein End-Filter.

        Returns:
            String mit Text-Beschreibung + Chart-Pfad im Format:
            "[Beschreibung]\n__CHART__[pfad.png]__CHART__"
            
            Bei Fehlern: "❌ Error: ..." oder "ℹ️ Keine Daten..."
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

            # ✅ Validierung: analysis_type mit FALLBACK
            valid_types = [
                "sentiment_bar_chart",
                "sentiment_pie_chart",
                "nps_bar_chart",
                "nps_pie_chart",
                "market_bar_chart",
                "market_pie_chart",
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
                    
                elif "zeit" in query_lower or "time" in query_lower or "trend" in query_lower:
                    analysis_type = "time_analysis"
                    print(f"✅ Fallback: Query enthält 'Zeit' → time_analysis")
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
                collection, query, market_filter, sentiment_filter, nps_filter, date_from, date_to
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

            # ✅ Create requested visualization
            print(f"\n🎨 Erstelle Chart: {analysis_type}")
            sys.stdout.flush()

            if analysis_type == "sentiment_bar_chart":
                text_result, chart_path = _create_sentiment_bar_chart(data)
            elif analysis_type == "sentiment_pie_chart":
                text_result, chart_path = _create_sentiment_pie_chart(data)
            elif analysis_type == "nps_bar_chart":
                text_result, chart_path = _create_nps_bar_chart(data)
            elif analysis_type == "nps_pie_chart":
                text_result, chart_path = _create_nps_pie_chart(data)
            elif analysis_type == "market_bar_chart":
                text_result, chart_path = _create_market_bar_chart(data)
            elif analysis_type == "market_pie_chart":
                text_result, chart_path = _create_market_pie_chart(data)
            elif analysis_type == "market_sentiment_breakdown":
                text_result, chart_path = _create_market_sentiment_breakdown(data)
            elif analysis_type == "market_nps_breakdown":
                text_result, chart_path = _create_market_nps_breakdown(data)
            elif analysis_type == "time_analysis":
                text_result, chart_path = _create_time_analysis(data)
            elif analysis_type == "overview":
                text_result, chart_path = _create_overview_charts(data)
            else:
                return f"❌ Unbekannter Chart-Typ: {analysis_type}"

            # ✅ DEBUG: Log Ergebnis
            print(f"\n{'=' * 60}")
            print("✅ CHART ERSTELLT")
            print(f"{'=' * 60}")
            print(f"   • Chart-Pfad: {chart_path}")
            if chart_path:
                print(f"   • File existiert: {os.path.exists(chart_path)}")
                if os.path.exists(chart_path):
                    print(f"   • File-Größe: {os.path.getsize(chart_path)} bytes")
            print(f"{'=' * 60}\n")
            sys.stdout.flush()

            # ✅ Chart-Marker für Streamlit-Parser hinzufügen
            if chart_path and os.path.exists(chart_path):
                final_result = f"{text_result}\n__CHART__{chart_path}__CHART__"
                print("📦 Returning result with chart marker")
                sys.stdout.flush()
                return final_result
            else:
                print("⚠️ Returning result WITHOUT chart marker (no valid path)")
                sys.stdout.flush()
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
    Erstellt eindeutigen Chart-Pfad mit Timestamp.

    ✅ WICHTIG: Nutzt immer Forward Slashes für Web-Kompatibilität!
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:17]
    chart_filename = f"{chart_name}_{timestamp}.png"

    chart_dir = "charts"
    os.makedirs(chart_dir, exist_ok=True)

    # ✅ Nutze os.path.join für OS-unabhängigen Pfad
    chart_path = os.path.join(chart_dir, chart_filename)

    # ✅ KRITISCH: Konvertiere zu Forward Slashes für Streamlit/Web
    chart_path = chart_path.replace("\\", "/")

    print(f"   📁 Chart wird gespeichert als: {chart_path}")
    sys.stdout.flush()

    return chart_path


def _get_filtered_data(
    collection: Chroma,
    query: str,
    market_filter: Optional[str],
    sentiment_filter: Optional[str],
    nps_filter: Optional[str],
    date_from: Optional[str],
    date_to: Optional[str],
) -> Dict:
    """
    Holt gefilterte Daten aus Collection mit erweiterten Filtern.
    """
    try:
        print("   🔍 Filter-Setup:")
        print(f"      • Market: {market_filter}")
        print(f"      • Sentiment: {sentiment_filter}")
        print(f"      • NPS: {nps_filter}")
        print(f"      • Date From: {date_from}")
        print(f"      • Date To: {date_to}")
        print(f"      • Query: '{query}'")
        sys.stdout.flush()

        # Build filters
        where_filter = {}

        if market_filter:
            where_filter["market"] = {"$eq": market_filter}

        if sentiment_filter:
            where_filter["sentiment_label"] = {"$eq": sentiment_filter.lower()}
        
        if nps_filter:
            where_filter["nps_category"] = {"$eq": nps_filter}
        
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

            result: Any = collection.get(
                where=where_filter, include=["documents", "metadatas"]  # type: ignore[arg-type]
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


# ═════════════════════════════════════════════════════════════════════════════
# CHART CREATION FUNCTIONS
# (Bleiben unverändert - nur Implementierung, keine Dokumentation nötig)
# ═════════════════════════════════════════════════════════════════════════════


def _create_sentiment_bar_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """Erstellt Bar Chart für Sentiment-Verteilung."""
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
        
        # Farben: Grün für Positiv, Grau für Neutral, Rot für Negativ
        colors = ["#48dbfb", "#feca57", "#ff6b6b"]  # Blau/Gelb/Rot
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

        chart_path = _get_chart_path("sentiment_distribution")

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
        error_msg = f"❌ Fehler bei _create_sentiment_bar_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def _create_sentiment_pie_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """Erstellt Pie Chart für Sentiment-Verteilung."""
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
        colors = ["#48dbfb", "#feca57", "#ff6b6b"]  # Blau/Gelb/Rot

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

        chart_path = _get_chart_path("sentiment_pie_distribution")

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
        error_msg = f"❌ Fehler bei _create_sentiment_pie_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def _create_nps_bar_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """Erstellt NPS Bar Chart"""
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
        colors = ["#ff6b6b", "#feca57", "#48dbfb"]

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

        chart_path = _get_chart_path("nps_distribution")
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
        error_msg = f"❌ Fehler bei _create_nps_bar_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def _create_nps_pie_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """Erstellt NPS Pie Chart"""
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
        colors = ["#48dbfb", "#feca57", "#ff6b6b"]  # Blau/Gelb/Rot

        plt.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            colors=colors[:len(labels)],
            startangle=90,
        )
        plt.title("NPS Category Distribution", fontsize=14, fontweight="bold")
        plt.axis("equal")

        chart_path = _get_chart_path("nps_pie_distribution")
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
        error_msg = f"❌ Fehler bei _create_nps_pie_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def _create_market_bar_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """Erstellt Bar Chart für Market-Volumen."""
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

        chart_path = _get_chart_path("market_distribution")

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
        error_msg = f"❌ Fehler bei _create_market_bar_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def _create_market_pie_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """Erstellt Pie Chart für Market-Anteile."""
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

        chart_path = _get_chart_path("market_pie_distribution")
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
        error_msg = f"❌ Fehler bei _create_market_pie_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def _create_market_sentiment_breakdown(data: Dict) -> Tuple[str, Optional[str]]:
    """Erstellt Grouped Bar Chart - Sentiment pro Market."""
    try:
        import numpy as np

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
        colors = ["#48dbfb", "#feca57", "#ff6b6b"]  # Blau, Gelb, Rot

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

        chart_path = _get_chart_path("market_sentiment_breakdown")
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
        error_msg = f"❌ Fehler bei _create_market_sentiment_breakdown: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def _create_market_nps_breakdown(data: Dict) -> Tuple[str, Optional[str]]:
    """Erstellt Grouped Bar Chart - NPS-Kategorien pro Market."""
    try:
        import numpy as np

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
            market = markets[0]
            market_data = market_nps_data[market]

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

            sizes = [market_data.get(cat, 0) for cat in categories]
            colors = ["#ff6b6b", "#feca57", "#48dbfb"]

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
            data_matrix = []
            for category in categories:
                data_matrix.append(
                    [market_nps_data[market].get(category, 0) for market in markets]
                )

            fig_width = max(12, len(markets) * 2)
            fig, ax = plt.subplots(figsize=(fig_width, 8))

            x = np.arange(len(markets))
            width = 0.25
            colors = ["#ff6b6b", "#feca57", "#48dbfb"]

            for i, (category, values) in enumerate(zip(categories, data_matrix)):
                bars = ax.bar(
                    x + i * width,
                    values,
                    width,
                    label=category,
                    color=colors[i],
                    alpha=0.8,
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
            ax.set_title("NPS Categories by Market", fontsize=14, fontweight="bold")
            ax.set_xticks(x + width)
            ax.set_xticklabels(markets, rotation=45, ha="right")
            ax.legend()
            ax.grid(axis="y", alpha=0.3)

            chart_filename = "market_nps_breakdown"

        plt.tight_layout()

        chart_path = _get_chart_path(chart_filename)

        print("   💾 Speichere Chart...")
        sys.stdout.flush()

        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"   ✅ Chart gespeichert: {chart_path}")
        sys.stdout.flush()

        # Optimierte User-Ausgabe: Clean, fokussiert, keine redundanten Infos
        if len(markets) == 1:
            # Single Market: Zeige nur die Kategorien ohne Market-Name (redundant)
            result = "⭐ **NPS-Verteilung**\n\n"
            market = markets[0]
            total_market = sum([market_nps_data[market][cat] for cat in categories])
            
            for category in categories:
                count = market_nps_data[market].get(category, 0)
                percentage = (count / total_market * 100) if total_market > 0 else 0
                result += f"• **{category}**: {count:,} ({percentage:.1f}%)\n"
        else:
            # Multiple Markets: Zeige Breakdown pro Market
            result = "⭐ **NPS nach Märkten**\n\n"
            
            for market in markets:
                total_market = sum([market_nps_data[market][cat] for cat in categories])
                result += f"**{market}**\n"
                for category in categories:
                    count = market_nps_data[market].get(category, 0)
                    percentage = (count / total_market * 100) if total_market > 0 else 0
                    result += f"  • {category}: {count:,} ({percentage:.1f}%)\n"
                result += "\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei _create_market_nps_breakdown: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def _create_time_analysis(data: Dict) -> Tuple[str, Optional[str]]:
    """Erstellt Timeline-Analyse mit mehreren Charts."""
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

        nps_monthly = defaultdict(lambda: defaultdict(int))
        for item in time_data:
            nps_monthly[item["year_month"]][item["nps_category"]] += 1

        categories = ["Detractor", "Passive", "Promoter"]
        colors = ["#ff6b6b", "#feca57", "#48dbfb"]

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

        chart_path = _get_chart_path("time_analysis")

        print("   💾 Speichere Chart...")
        sys.stdout.flush()

        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"   ✅ Chart gespeichert: {chart_path}")
        sys.stdout.flush()

        # Optimierte User-Ausgabe: Fokus auf Zeitraum und Trends
        result = "� **Zeitverlauf-Analyse**\n\n"
        result += f"� Zeitraum: {sorted_months[0]} bis {sorted_months[-1]}\n\n"

        result += "**Letzte 6 Monate:**\n"
        for month in sorted_months[-6:]:
            total = monthly_counts[month]
            result += f"• {month}: {total:,} Feedbacks\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei _create_time_analysis: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def _create_overview_charts(data: Dict) -> Tuple[str, Optional[str]]:
    """Erstellt Overview mit 4 Charts."""
    try:
        print("   🎨 Erstelle Overview Dashboard...")
        sys.stdout.flush()

        metadatas = data["metadatas"]
        if not metadatas:
            return "❌ Keine Daten für Overview", None

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        sentiments = [m.get("sentiment_label", "Unknown") for m in metadatas]
        sentiment_counts = Counter(sentiments)
        ax1.pie(
            sentiment_counts.values(),
            labels=sentiment_counts.keys(),
            autopct="%1.1f%%",
            startangle=90,
        )
        ax1.set_title("Sentiment Distribution")

        categories = [m.get("nps_category", "Unknown") for m in metadatas]
        category_counts = Counter(categories)
        ax2.bar(
            category_counts.keys(),
            category_counts.values(),
            color=["#ff6b6b", "#feca57", "#48dbfb"],
        )
        ax2.set_title("NPS Categories")
        ax2.set_ylabel("Count")

        markets = [m.get("market", "Unknown") for m in metadatas]
        market_counts = Counter(markets)
        ax3.barh(
            list(market_counts.keys()), list(market_counts.values()), color="#3742fa"
        )
        ax3.set_title("Markets")
        ax3.set_xlabel("Count")

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

        chart_path = _get_chart_path("feedback_overview")

        print("   💾 Speichere Chart...")
        sys.stdout.flush()

        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"   ✅ Chart gespeichert: {chart_path}")
        sys.stdout.flush()

        # Optimierte User-Ausgabe: Kompakter Überblick mit Key-Insights
        result = "� **Feedback-Überblick**\n\n"
        
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
        error_msg = f"❌ Fehler bei _create_overview_charts: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None
