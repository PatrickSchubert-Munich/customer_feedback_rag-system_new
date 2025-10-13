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
from typing import Optional, Dict, Tuple
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
            count = collection.count()
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
    ) -> str:
        """
        Erstellt Charts und Visualisierungen aus Customer-Feedback-Daten.

        ════════════════════════════════════════════════════════════════════════
        🎯 TOOL-ZWECK
        ════════════════════════════════════════════════════════════════════════
        Dieses Tool wandelt Feedback-Daten in visuelle Charts um und gibt sowohl
        eine textuelle Beschreibung als auch einen Chart-Pfad zurück.

        ════════════════════════════════════════════════════════════════════════
        📦 RETURN-FORMAT (KRITISCH WICHTIG)
        ════════════════════════════════════════════════════════════════════════
        Das Tool gibt IMMER einen String zurück im Format:

        "[Textuelle Beschreibung]\n__CHART__[absoluter/pfad/zum/chart.png]__CHART__"

        Beispiel-Return:
        '''
        📊 SENTIMENT DISTRIBUTION CHART

        📈 Total feedback analyzed: 17,700

        • Positiv: 8,500 (48.0%)
        • Negativ: 6,200 (35.0%)
        • Neutral: 3,000 (17.0%)
        __CHART__charts/sentiment_distribution_20250103_143022.png__CHART__
        '''

        🚨 EXIT-MARKER (Agent muss diese erkennen):
        ✅ Pattern 1: "__CHART__[pfad]__CHART__" vorhanden → Finales Ergebnis
        ✅ Pattern 2: Emoji am Start (📊, ⭐, 🌍, 📈, 📅) → Finales Ergebnis
        ✅ Pattern 3: "❌" am Start → Fehler, aber finales Ergebnis (kein Retry)

        ════════════════════════════════════════════════════════════════════════
        📊 VERFÜGBARE CHART-TYPEN (analysis_type Parameter)
        ════════════════════════════════════════════════════════════════════════

        1. "sentiment_chart" (DEFAULT)
           ├─ Beschreibung: Pie Chart der Sentiment-Verteilung
           ├─ Zeigt: Prozentuale Aufteilung positiv/negativ/neutral
           ├─ Best für: Schneller Sentiment-Überblick
           └─ Emoji-Marker: 📊

        2. "nps_chart"
           ├─ Beschreibung: Bar Chart der NPS-Kategorien
           ├─ Zeigt: Anzahl Promoter (9-10), Passive (7-8), Detractor (0-6)
           ├─ Best für: Kundenzufriedenheit bewerten
           └─ Emoji-Marker: ⭐

        3. "market_chart"
           ├─ Beschreibung: Horizontaler Bar Chart der Markets
           ├─ Zeigt: Feedback-Anzahl pro Market (C1-DE, C1-FR, C1-AT, etc.)
           ├─ Best für: Regionale Verteilung verstehen
           └─ Emoji-Marker: 🌍

        4. "market_nps_breakdown"
           ├─ Beschreibung: Grouped Bar Chart - NPS-Kategorien pro Market
           ├─ Zeigt: Promoter/Passive/Detractor für jeden Market
           ├─ Best für: Regionale NPS-Unterschiede erkennen
           ├─ Spezialfall: Bei 1 Market → Pie + Bar Chart Kombination
           └─ Emoji-Marker: 📊

        5. "time_analysis"
           ├─ Beschreibung: 4-Panel Dashboard mit Zeitverlaufs-Charts
           ├─ Zeigt: Feedback-Volumen, NPS-Trends, Sentiment-Trends, NPS-%
           ├─ Best für: Zeitliche Entwicklungen analysieren
           └─ Emoji-Marker: 📅

        6. "overview"
           ├─ Beschreibung: 4-Panel Dashboard mit Gesamt-Überblick
           ├─ Zeigt: Sentiment-Pie, NPS-Bar, Market-Bar, NPS-Score-Histogram
           ├─ Best für: Kompletter Überblick über alle Dimensionen
           └─ Emoji-Marker: 📈

        ════════════════════════════════════════════════════════════════════════
        📥 PARAMETER-BESCHREIBUNG
        ════════════════════════════════════════════════════════════════════════

        Args:
            analysis_type (str, optional):
                Chart-Typ aus obiger Liste.
                DEFAULT: "sentiment_chart"
                VALIDIERUNG: Wird gegen erlaubte Liste geprüft.
                FEHLER BEI: Ungültigem Wert → Return startet mit "❌"

            query (str, optional):
                Semantische Suchanfrage zur Filterung der Daten.
                DEFAULT: "" (leerer String)
                BEDEUTUNG:
                  - Leer ("") → ALLE Daten werden verwendet
                  - Nicht-leer → Nur Daten die zur Query passen
                BEISPIELE:
                  - "" → Alle 17.700 Feedbacks
                  - "Lieferprobleme" → Nur Feedbacks über Lieferung
                  - "schneller Service" → Nur Feedbacks über Service

            market_filter (str | None, optional):
                Filtert Daten nach einem einzelnen Market.
                DEFAULT: None
                BEDEUTUNG:
                  - None → ALLE Markets einbeziehen
                  - "C1-DE" → Nur Deutschland
                  - "C1-FR" → Nur Frankreich
                VERFÜGBARE MARKETS:
                  - C1-DE (Deutschland)
                  - C1-FR (Frankreich)
                  - C1-AT (Österreich)
                  - C1-CH (Schweiz)
                  - Weitere europäische Markets
                FEHLER BEI: Market nicht gefunden → Return startet mit "ℹ️"

            sentiment_filter (str | None, optional):
                Filtert Daten nach Sentiment.
                DEFAULT: None
                BEDEUTUNG:
                  - None → ALLE Sentiments einbeziehen
                  - "positiv" → Nur positive Feedbacks
                  - "negativ" → Nur negative Feedbacks
                  - "neutral" → Nur neutrale Feedbacks
                CASE-INSENSITIVE: "Positiv" = "positiv" = "POSITIV"
                FEHLER BEI: Ungültiger Wert → Return startet mit "ℹ️"

        Returns:
            str: Formatierter String mit ZWEI Komponenten:

            KOMPONENTE 1 - Textuelle Beschreibung:
                - Emoji-Marker am Anfang (📊, ⭐, 🌍, 📈, 📅)
                - Überschrift mit Chart-Typ
                - Statistiken (Total Feedback, Verteilungen, etc.)
                - Pro Kategorie: Anzahl + Prozent

            KOMPONENTE 2 - Chart-Marker:
                - Format: "\n__CHART__[pfad/zum/chart.png]__CHART__"
                - Pfad ist IMMER relativ zu Projektroot
                - Pfad nutzt Forward Slashes ("/") für Web-Kompatibilität
                - Dateiname enthält Timestamp (YYYYMMDD_HHMMSS_fff)

            FEHLER-RETURNS (kein Chart):
                - "❌ Error: [Fehlerbeschreibung]" → Permanenter Fehler
                - "ℹ️ Keine Daten für [Filter]" → Keine passenden Daten

        ════════════════════════════════════════════════════════════════════════
        🎬 VERWENDUNGSBEISPIELE
        ════════════════════════════════════════════════════════════════════════

        BEISPIEL 1 - Einfachster Call (alle Defaults):
        ────────────────────────────────────────────────────────────────────────
        Call:
            feedback_analytics()

        Entspricht:
            feedback_analytics("sentiment_chart", "", None, None)

        Bedeutung:
            - Erstellt Sentiment-Chart
            - Nutzt ALLE 17.700 Feedbacks
            - Keine Filter aktiv

        Erwartetes Return-Pattern:
            "📊 SENTIMENT DISTRIBUTION CHART\n\n...\n__CHART__charts/sentiment_...png__CHART__"

        BEISPIEL 2 - NPS-Chart für Deutschland:
        ────────────────────────────────────────────────────────────────────────
        Call:
            feedback_analytics("nps_chart", "", "C1-DE", None)

        Bedeutung:
            - Erstellt NPS-Bar-Chart
            - Nur Feedbacks aus Deutschland
            - Zeigt Promoter/Passive/Detractor für C1-DE

        Erwartetes Return-Pattern:
            "⭐ NPS CATEGORY CHART\n\n...\n__CHART__charts/nps_distribution_...png__CHART__"

        BEISPIEL 3 - Zeitanalyse für negative Feedbacks:
        ────────────────────────────────────────────────────────────────────────
        Call:
            feedback_analytics("time_analysis", "", None, "negativ")

        Bedeutung:
            - Erstellt Zeit-Dashboard (4 Charts)
            - Nur negative Feedbacks
            - Alle Markets
            - Zeigt zeitliche Entwicklung negativer Feedbacks

        Erwartetes Return-Pattern:
            "📅 TIME ANALYSIS CHART\n\n...\n__CHART__charts/time_analysis_...png__CHART__"

        BEISPIEL 4 - Semantische Suche + Chart:
        ────────────────────────────────────────────────────────────────────────
        Call:
            feedback_analytics("sentiment_chart", "Lieferprobleme", None, None)

        Bedeutung:
            - Erst: Semantische Suche nach "Lieferprobleme"
            - Dann: Sentiment-Chart NUR aus diesen Ergebnissen
            - Alle Markets, alle Sentiments (aber nur Liefer-Feedbacks)

        Erwartetes Return-Pattern:
            "📊 SENTIMENT DISTRIBUTION CHART\n\n...\n__CHART__charts/sentiment_...png__CHART__"

        BEISPIEL 5 - Multi-Filter (Market + Sentiment):
        ────────────────────────────────────────────────────────────────────────
        Call:
            feedback_analytics("market_nps_breakdown", "", "C1-FR", "positiv")

        Bedeutung:
            - NPS-Breakdown für Frankreich
            - Nur positive Feedbacks
            - Da nur 1 Market → Erstellt Pie + Bar Kombination

        Erwartetes Return-Pattern:
            "📊 MARKET NPS BREAKDOWN CHART\n\n...\n__CHART__charts/market_nps_single_...png__CHART__"

        ════════════════════════════════════════════════════════════════════════
        🚨 FEHLERBEHANDLUNG & EXIT-LOGIK
        ════════════════════════════════════════════════════════════════════════

        FEHLERFALL 1: Ungültiger analysis_type
        ────────────────────────────────────────────────────────────────────────
        Input:
            feedback_analytics("foobar_chart", "", None, None)

        Return:
            "❌ Error: Ungültiger analysis_type 'foobar_chart'. Gültig: sentiment_chart, nps_chart, ..."

        Agent-Aktion:
            → Erkenne "❌" als Fehler-Marker
            → Gebe Return DIREKT an User weiter
            → KEIN erneuter Tool-Call
            → EXIT

        FEHLERFALL 2: Keine Daten nach Filterung
        ────────────────────────────────────────────────────────────────────────
        Input:
            feedback_analytics("nps_chart", "", "C1-XX", None)  # Ungültiger Market

        Return:
            "ℹ️ Keine Daten für Market: C1-XX"

        Agent-Aktion:
            → Erkenne "ℹ️" als Info-Marker (= keine Daten)
            → Informiere User: "Für Market C1-XX sind keine Daten vorhanden"
            → KEIN erneuter Tool-Call
            → EXIT

        FEHLERFALL 3: Collection nicht verfügbar
        ────────────────────────────────────────────────────────────────────────
        Return:
            "❌ Error: Vectorstore nicht verfügbar (collection is None)"

        Agent-Aktion:
            → Erkenne "❌" als kritischen Fehler
            → Melde an Manager: "Datenbank nicht verfügbar"
            → Manager kann 1x Retry versuchen (siehe PRIO 5)
            → Falls nach Retry immer noch Fehler → Eskalation an User

        ERFOLGSFALL: Finales Ergebnis
        ────────────────────────────────────────────────────────────────────────
        Return:
            "📊 SENTIMENT CHART\n\n...\n__CHART__charts/sentiment_20250103.png__CHART__"

        Agent-Aktion:
            → Erkenne Emoji "📊" als SUCCESS-Marker
            → Erkenne "__CHART__" als finales Ergebnis
            → Gebe Return 1:1 an Manager zurück
            → Manager gibt an User weiter
            → KEIN weiterer Tool-Call
            → EXIT

        ════════════════════════════════════════════════════════════════════════
        ⚙️ INTERNE IMPLEMENTIERUNG (für Debugging)
        ════════════════════════════════════════════════════════════════════════

        Workflow:
        1. Validiere Collection (existiert? hat Daten?)
        2. Validiere analysis_type (gegen erlaubte Liste)
        3. Hole gefilterte Daten via _get_filtered_data()
        4. Prüfe: Daten vorhanden? (Falls nein → Return "ℹ️")
        5. Erstelle Chart via entsprechender _create_*_chart() Funktion
        6. Speichere Chart als PNG mit Timestamp-Dateinamen
        7. Formatiere Return: "[Text]\n__CHART__[pfad]__CHART__"
        8. Return String

        Chart-Speicherort:
            - Ordner: ./charts/ (wird auto-erstellt)
            - Dateiname: [chart_type]_[YYYYMMDD_HHMMSS_fff].png
            - Beispiel: sentiment_distribution_20250103_143022_123.png

        Chart-Qualität:
            - DPI: 300 (hochauflösend)
            - Format: PNG
            - bbox_inches: "tight" (kein Whitespace-Rand)

        ════════════════════════════════════════════════════════════════════════
        ✅ AGENT-CHECKLISTE (NACH Tool-Aufruf)
        ════════════════════════════════════════════════════════════════════════

        Nach feedback_analytics() Aufruf muss Agent prüfen:

        ☐ Enthält Return "__CHART__[pfad]__CHART__"?
          → JA: Finales Ergebnis, STOP
          → NEIN: Weiter prüfen

        ☐ Startet Return mit Emoji (📊, ⭐, 🌍, 📈, 📅)?
          → JA: Finales Ergebnis, STOP
          → NEIN: Weiter prüfen

        ☐ Startet Return mit "❌" oder "ℹ️"?
          → JA: Fehler/Info, STOP (an Manager weiterleiten)
          → NEIN: Unerwartetes Format → Fehler melden

        ☐ Nach STOP: Tool nochmal aufrufen?
          → NIEMALS! Nach finalem Ergebnis ist Workflow beendet.

        ☐ Response "verbessern" oder kommentieren?
          → NIEMALS! Response 1:1 weitergeben.

        ════════════════════════════════════════════════════════════════════════
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
                collection_count = collection.count()
                print(f"\n✅ Collection hat {collection_count} Dokumente")
                sys.stdout.flush()
            except Exception as e:
                error_msg = f"❌ Error: Collection count fehlgeschlagen: {str(e)}"
                print(f"\n{error_msg}\n")
                traceback.print_exc()
                sys.stdout.flush()
                return error_msg

            # ✅ Validierung: analysis_type
            valid_types = [
                "sentiment_chart",
                "nps_chart",
                "market_chart",
                "market_nps_breakdown",
                "time_analysis",
                "overview",
            ]

            if analysis_type not in valid_types:
                error_msg = f"❌ Error: Ungültiger analysis_type '{analysis_type}'. Gültig: {', '.join(valid_types)}"
                print(f"\n{error_msg}\n")
                sys.stdout.flush()
                return error_msg

            # ✅ Get filtered data
            print("\n📊 Hole gefilterte Daten aus ChromaDB...")
            sys.stdout.flush()

            data = _get_filtered_data(
                collection, query, market_filter, sentiment_filter
            )

            if not data["documents"]:
                msg = "ℹ️ Keine Daten für Analyse gefunden (Filter zu restriktiv?)"
                print(f"\n{msg}\n")
                sys.stdout.flush()
                return msg

            print(f"✅ {len(data['documents'])} Dokumente gefunden")
            sys.stdout.flush()

            # ✅ Create requested visualization
            print(f"\n🎨 Erstelle Chart: {analysis_type}")
            sys.stdout.flush()

            if analysis_type == "sentiment_chart":
                text_result, chart_path = _create_sentiment_chart(data)
            elif analysis_type == "nps_chart":
                text_result, chart_path = _create_nps_chart(data)
            elif analysis_type == "market_chart":
                text_result, chart_path = _create_market_chart(data)
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
) -> Dict:
    """
    Holt gefilterte Daten aus Collection.
    """
    try:
        print("   🔍 Filter-Setup:")
        print(f"      • Market: {market_filter}")
        print(f"      • Sentiment: {sentiment_filter}")
        print(f"      • Query: '{query}'")
        sys.stdout.flush()

        # Build filters
        where_filter = {}

        if market_filter:
            where_filter["market"] = {"$eq": market_filter}

        if sentiment_filter:
            where_filter["sentiment_label"] = {"$eq": sentiment_filter.lower()}

        # Combine filters
        if len(where_filter) > 1:
            where_filter = {
                "$and": [
                    {"market": where_filter.get("market", {})},
                    {"sentiment_label": where_filter.get("sentiment_label", {})},
                ]
            }
        elif len(where_filter) == 0:
            where_filter = None
        else:
            key = list(where_filter.keys())[0]
            where_filter = {key: where_filter[key]}

        print(f"   🔧 ChromaDB Filter: {where_filter}")
        sys.stdout.flush()

        # Query data
        if query.strip():
            print("   🔎 Führe semantic search aus...")
            sys.stdout.flush()

            result = collection.query(
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

            result = collection.get(
                where=where_filter, include=["documents", "metadatas"]
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


def _create_sentiment_chart(data: Dict) -> Tuple[str, Optional[str]]:
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
        colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"]

        labels = list(sentiment_counts.keys())
        sizes = list(sentiment_counts.values())

        plt.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            colors=colors[: len(labels)],
            startangle=90,
        )
        plt.title(
            "Sentiment Distribution in Customer Feedback",
            fontsize=14,
            fontweight="bold",
        )
        plt.axis("equal")

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

        result = "📊 **SENTIMENT DISTRIBUTION CHART**\n\n"
        result += f"📈 Total feedback analyzed: {len(metadatas):,}\n\n"

        for sentiment, count in sentiment_counts.most_common():
            percentage = (count / len(metadatas)) * 100
            result += f"• {sentiment.title()}: {count:,} ({percentage:.1f}%)\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei _create_sentiment_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def _create_nps_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """Erstellt NPS Chart"""
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

        result = "⭐ **NPS CATEGORY CHART**\n\n"
        result += f"📊 Total feedback analyzed: {len(metadatas):,}\n\n"

        for category, count in category_counts.most_common():
            percentage = (count / len(metadatas)) * 100
            result += f"• {category}: {count:,} ({percentage:.1f}%)\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei _create_nps_chart: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None


def _create_market_chart(data: Dict) -> Tuple[str, Optional[str]]:
    """Erstellt Bar Chart für Market-Verteilung."""
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

        result = "🌍 **MARKET DISTRIBUTION CHART**\n\n"
        result += f"📊 Total feedback analyzed: {len(metadatas):,}\n\n"

        for market, count in market_counts.most_common():
            percentage = (count / len(metadatas)) * 100
            result += f"• {market}: {count:,} ({percentage:.1f}%)\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei _create_market_chart: {str(e)}"
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

        result = "📊 **MARKET NPS BREAKDOWN CHART**\n\n"
        result += f"📈 Total feedback analyzed: {len(metadatas):,}\n"
        result += f"🌍 Markets analyzed: {len(markets)}\n\n"

        if len(markets) == 1:
            result += "ℹ️ *Single market analysis mit detaillierter Visualisierung*\n\n"

        for market in markets:
            total_market = sum([market_nps_data[market][cat] for cat in categories])
            result += f"**{market}** (Total: {total_market:,} customers):\n"
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

        result = "📅 **TIME ANALYSIS CHART**\n\n"
        result += f"📊 Total feedback analyzed: {len(time_data):,}\n"
        result += f"📅 Time period: {sorted_months[0]} to {sorted_months[-1]}\n"
        result += f"📈 Months covered: {len(sorted_months)}\n\n"

        result += "**Monthly Summary (last 6 months):**\n"
        for month in sorted_months[-6:]:
            total = monthly_counts[month]
            result += f"  • {month}: {total:,} feedback entries\n"

        if len(sorted_months) > 6:
            result += f"  • ... and {len(sorted_months) - 6} earlier months\n"

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

        result = "📈 **COMPREHENSIVE FEEDBACK OVERVIEW**\n\n"
        result += f"📊 Total feedback analyzed: {len(metadatas):,}\n\n"
        result += "**Summary Statistics:**\n"
        result += f"• Sentiment categories: {len(sentiment_counts)}\n"
        result += f"• NPS categories: {len(category_counts)}\n"
        result += f"• Markets covered: {len(market_counts)}\n"
        if nps_scores:
            result += f"• Average NPS: {sum(nps_scores) / len(nps_scores):.1f}\n"

        return result, chart_path

    except Exception as e:
        error_msg = f"❌ Fehler bei _create_overview_charts: {str(e)}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        sys.stdout.flush()
        return error_msg, None
