import pandas as pd


def create_metadata_tool(collection):
    """
    Erstellt Metadata-Snapshot-Builder für Customer Manager.
    
    Da kein Metadata Analysis Agent mehr existiert, werden die Funktionen
    direkt (ohne @function_tool Decorator) implementiert und nur für den
    Snapshot-Build beim App-Start verwendet.
    
    Args:
        collection: ChromaDB Collection mit Metadaten
    
    Returns:
        callable: build_metadata_snapshot Funktion zur Snapshot-Erstellung
    """
    def get_all_metadata() -> list:
        """Alle Metadaten werden aus der Collection geladen."""
        data = collection.get(include=["metadatas"])
        meta_data = data["metadatas"]
        return meta_data

    def convert_metadata_to_dataframe(metadatas: list) -> pd.DataFrame:
        """Konvertiert die Liste der Metadaten-Dictionaries in ein pandas DataFrame."""
        return pd.DataFrame(metadatas)

    # Lade ALLE Metadaten aus der Collection
    metadatas_list = get_all_metadata()

    # Konvertiere die Metadaten-Liste in ein pandas DataFrame
    df_metadata = convert_metadata_to_dataframe(metadatas_list)

    # Stelle sicher, dass numerische Spalten korrekte Datentypen haben
    if not df_metadata.empty:
        # NPS sollte numerisch sein
        if "nps" in df_metadata.columns:
            df_metadata["nps"] = pd.to_numeric(df_metadata["nps"], errors="coerce")

        # Sentiment Score sollte float sein
        if "sentiment_score" in df_metadata.columns:
            df_metadata["sentiment_score"] = pd.to_numeric(
                df_metadata["sentiment_score"], errors="coerce"
            )

        # Token Count sollte int sein
        if "verbatim_token_count" in df_metadata.columns:
            df_metadata["verbatim_token_count"] = pd.to_numeric(
                df_metadata["verbatim_token_count"], errors="coerce"
            )

    # ═══════════════════════════════════════════════════════════════════════
    # METADATA EXTRACTION FUNCTIONS
    # Direkte Implementierung ohne @function_tool - nur für Snapshot-Build
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_unique_markets() -> str:
        """
        Liefert alle verfügbaren Märkte im Datensatz.

        Returns:
            str: Kommagetrennte Liste der Märkte (z.B. "C1-DE, C2-AT, C3-CH")
                 oder "Keine Marktdaten verfügbar." bei fehlenden Daten

        Examples:
            >>> get_unique_markets()
            "C1-DE, C2-AT, C2-US, C3-CH"
        """
        if "market" in df_metadata.columns:
            unique_markets = sorted(df_metadata["market"].dropna().unique())
            return ", ".join(unique_markets)
        return "Keine Marktdaten verfügbar."

    def get_nps_statistics() -> str:
        """
        Liefert umfassende NPS-Statistiken des Datensatzes.

        Returns:
            str: Multi-Line String mit NPS-Analyse:
                - Anzahl Einträge
                - Durchschnitt (Mean)
                - Median
                - Range (Min-Max)
                - Kategorien-Verteilung (Detractor/Passive/Promoter mit Prozenten)
                Bei fehlenden Daten: "Keine NPS-Daten verfügbar."

        Examples:
            >>> get_nps_statistics()
            "NPS-Statistiken (1500 Einträge):\\n• Durchschnitt: 7.85\\n• Median: 8.0\\n..."

        Notes:
            - NPS-Kategorien: Detractor (0-6), Passive (7-8), Promoter (9-10)
            - Prozente beziehen sich auf Gesamt-NPS-Einträge
        """
        if "nps" not in df_metadata.columns or df_metadata["nps"].isna().all():
            return "Keine NPS-Daten verfügbar."

        nps_stats = df_metadata["nps"].describe()
        lines = []
        lines.append(f"NPS-Statistiken ({int(nps_stats['count'])} Einträge):")
        lines.append(f"• Durchschnitt: {nps_stats['mean']:.2f}")
        lines.append(f"• Median: {nps_stats['50%']:.1f}")
        lines.append(f"• Range: {nps_stats['min']:.0f} - {nps_stats['max']:.0f}")

        # NPS-Kategorien berechnen
        nps_categories = (
            df_metadata["nps"]
            .apply(
                lambda x: "Detractor" if x <= 6 else "Passive" if x <= 8 else "Promoter"
            )
            .value_counts()
        )

        total = len(df_metadata["nps"].dropna())
        lines.append("• Kategorien:")
        for category, count in nps_categories.items():
            percentage = (count / total) * 100
            lines.append(f"  - {category}: {count} ({percentage:.1f}%)")

        return "\n".join(lines)

    def get_sentiment_statistics() -> str:
        """
        Liefert Sentiment-Analysestatistiken des Datensatzes.

        Returns:
            str: Multi-Line String mit:
                - Sentiment-Labels-Verteilung (positiv/negativ/neutral mit Prozenten)
                - Sentiment-Scores (Durchschnitt, Range)
                Bei fehlenden Daten: "Keine Sentiment-Daten verfügbar."

        Examples:
            >>> get_sentiment_statistics()
            "Sentiment-Verteilung (1500 Einträge):\\n• positiv: 800 (53.3%)\\n..."
        """
        lines = []

        # Sentiment Labels
        if "sentiment_label" in df_metadata.columns:
            sentiment_counts = df_metadata["sentiment_label"].value_counts()
            total_sent = len(df_metadata["sentiment_label"].dropna())
            lines.append(f"Sentiment-Verteilung ({total_sent} Einträge):")
            for label, count in sentiment_counts.items():
                percentage = (count / total_sent) * 100
                lines.append(f"• {label}: {count} ({percentage:.1f}%)")

        # Sentiment Scores
        if "sentiment_score" in df_metadata.columns:
            sentiment_stats = df_metadata["sentiment_score"].describe()
            lines.append("\nSentiment-Scores:")
            lines.append(f"• Durchschnitt: {sentiment_stats['mean']:.3f}")
            lines.append(
                f"• Range: {sentiment_stats['min']:.3f} bis {sentiment_stats['max']:.3f}"
            )

        return "\n".join(lines) if lines else "Keine Sentiment-Daten verfügbar."

    def get_date_range() -> str:
        """
        Liefert den Zeitraum des Datensatzes.

        Returns:
            str: Zeitraum mit Start/End-Datum, Anzahl Tage und Einträge.
                 Format: "Zeitraum: 2024-01-01 bis 2024-12-31 (365 Tage, 1500 Einträge)"
                 Bei fehlenden Daten: "Keine Datumsdaten verfügbar."

        Examples:
            >>> get_date_range()
            "Zeitraum: 2024-01-01 bis 2024-12-31 (365 Tage, 1500 Einträge)"
        """
        if "date_str" not in df_metadata.columns:
            return "Keine Datumsdaten verfügbar."

        dates = df_metadata["date_str"].dropna()
        if dates.empty:
            return "Keine gültigen Datumsdaten verfügbar."

        date_min = dates.min()
        date_max = dates.max()
        total_days = (pd.to_datetime(date_max) - pd.to_datetime(date_min)).days

        return f"Zeitraum: {date_min} bis {date_max} ({total_days} Tage, {len(dates)} Einträge)"

    def get_verbatim_statistics() -> str:
        """
        Liefert Statistiken über Feedback-Text-Längen (Token-Anzahl).

        Returns:
            str: Multi-Line String mit:
                - Durchschnittliche Token-Anzahl
                - Median, Min, Max
                - Längenverteilung (kurz/mittel/lang mit Prozenten)
                Bei fehlenden Daten: "Keine Token-Count-Daten verfügbar."

        Examples:
            >>> get_verbatim_statistics()
            "Verbatim-Statistiken (1500 Texte):\\n• Durchschnittliche Länge: 45.3 Token\\n..."

        Notes:
            - Kurz: ≤20 Token, Mittel: 21-100 Token, Lang: >100 Token
        """
        if "verbatim_token_count" not in df_metadata.columns:
            return "Keine Token-Count-Daten verfügbar."

        token_stats = df_metadata["verbatim_token_count"].describe()
        lines = []
        lines.append(f"Verbatim-Statistiken ({int(token_stats['count'])} Texte):")
        lines.append(f"• Durchschnittliche Länge: {token_stats['mean']:.1f} Token")
        lines.append(f"• Median: {token_stats['50%']:.0f} Token")
        lines.append(f"• Kürzester Text: {token_stats['min']:.0f} Token")
        lines.append(f"• Längster Text: {token_stats['max']:.0f} Token")

        # Kategorisierung nach Textlänge
        short_texts = (df_metadata["verbatim_token_count"] <= 20).sum()
        medium_texts = (
            (df_metadata["verbatim_token_count"] > 20)
            & (df_metadata["verbatim_token_count"] <= 100)
        ).sum()
        long_texts = (df_metadata["verbatim_token_count"] > 100).sum()

        total = len(df_metadata["verbatim_token_count"].dropna())
        lines.append("• Längenverteilung:")
        lines.append(
            f"  - Kurze Texte (≤20 Token): {short_texts} ({(short_texts / total) * 100:.1f}%)"
        )
        lines.append(
            f"  - Mittlere Texte (21-100 Token): {medium_texts} ({(medium_texts / total) * 100:.1f}%)"
        )
        lines.append(
            f"  - Lange Texte (>100 Token): {long_texts} ({(long_texts / total) * 100:.1f}%)"
        )

        return "\n".join(lines)

    def get_dataset_overview() -> str:
        """
        Liefert kompakte Übersicht aller Datensatz-Kennzahlen.

        Returns:
            str: Multi-Line Übersicht mit:
                - Gesamt-Anzahl Einträge
                - Anzahl/Liste Märkte
                - NPS-Durchschnitt
                - Häufigstes Sentiment
                - Zeitraum
                Komprimierte Darstellung für schnellen Überblick.

        Examples:
            >>> get_dataset_overview()
            "📊 DATENSATZ-ÜBERSICHT\\nGesamt: 1500 Einträge\\n🏢 Märkte: 4 (C1-DE, ...)\\n..."
        """
        lines = []
        lines.append("📊 DATENSATZ-ÜBERSICHT")
        lines.append(f"Gesamt: {len(df_metadata)} Einträge")
        lines.append("")

        # Märkte
        if "market" in df_metadata.columns:
            unique_markets = df_metadata["market"].nunique()
            lines.append(
                f"🏢 Märkte: {unique_markets} ({', '.join(sorted(df_metadata['market'].dropna().unique()))})"
            )

        # NPS-Schnellübersicht
        if "nps" in df_metadata.columns:
            nps_avg = df_metadata["nps"].mean()
            lines.append(f"⭐ NPS-Durchschnitt: {nps_avg:.2f}")

        # Sentiment-Schnellübersicht
        if "sentiment_label" in df_metadata.columns:
            top_sentiment = (
                df_metadata["sentiment_label"].mode().iloc[0]
                if not df_metadata["sentiment_label"].empty
                else "N/A"
            )
            lines.append(f"😊 Häufigstes Sentiment: {top_sentiment}")

        # Zeitraum
        if "date_str" in df_metadata.columns:
            dates = df_metadata["date_str"].dropna()
            if not dates.empty:
                lines.append(f"📅 Zeitraum: {dates.min()} bis {dates.max()}")

        lines.append("")
        lines.append("💡 Verwende die spezifischen Tools für detaillierte Analysen.")

        return "\n".join(lines)

    def resolve_market_name(market_input: str) -> str:
        """
        Mappt User-Eingaben auf valide Datensatz-Marktnamen.
        
        Args:
            market_input (str): User-Eingabe für Markt.
                Unterstützt: Kürzel (DE, AT, CH, US), Ländernamen (Deutschland, Austria),
                exakte Market-IDs (C1-DE)

        Returns:
            str: Valider Market-Name aus Datensatz oder Fehlermeldung mit verfügbaren Märkten.
                - Bei exakter Übereinstimmung: Market-Name (z.B. "C1-DE")
                - Bei Partial Match: Erster Match oder Warnung bei Mehrdeutigkeit
                - Bei Fehler: "❌ Unbekannter Markt: ... Verfügbare Märkte: ..."

        Examples:
            >>> resolve_market_name("DE")
            "C1-DE"
            
            >>> resolve_market_name("Deutschland")
            "C1-DE"
            
            >>> resolve_market_name("XYZ")
            "❌ Unbekannter Markt: 'XYZ'. Verfügbare Märkte: C1-DE, C2-AT, ..."

        Notes:
            - Mapping: deutschland→DE, österreich→AT, schweiz→CH, usa→US, etc.
            - Case-insensitive Matching
            - Bei Mehrdeutigkeit: Nutzt ersten Match mit Warnung
        """
        if "market" not in df_metadata.columns:
            return "❌ Keine Marktdaten verfügbar."
        
        # Hole alle verfügbaren Märkte
        available_markets = sorted(df_metadata["market"].dropna().unique())
        
        # Normalisiere Input
        market_lower = market_input.lower().strip()
        
        # 1. Exakte Übereinstimmung (case-insensitive)
        for market in available_markets:
            if market.lower() == market_lower:
                return market
        
        # 2. Partial Match: User sagt "DE", wir finden "C1-DE" oder "C2-DE"
        matches = [m for m in available_markets if market_lower in m.lower()]
        
        if len(matches) == 1:
            # Eindeutige Übereinstimmung
            return matches[0]
        elif len(matches) > 1:
            # Mehrere Übereinstimmungen - wähle erste
            return f"⚠️ Mehrere Märkte gefunden: {', '.join(matches)}. Nutze ersten: {matches[0]}"
        
        # 3. Länder-Namen Mapping
        country_mapping = {
            "deutschland": "DE",
            "germany": "DE",
            "österreich": "AT",
            "oesterreich": "AT",
            "austria": "AT",
            "schweiz": "CH",
            "switzerland": "CH",
            "usa": "US",
            "united states": "US",
            "frankreich": "FR",
            "france": "FR",
            "italien": "IT",
            "italy": "IT",
            "spanien": "ES",
            "spain": "ES",
        }
        
        # Versuche Länder-Namen zu mappen
        if market_lower in country_mapping:
            country_code = country_mapping[market_lower]
            # Suche nach Märkten mit diesem Länder-Code
            matches = [m for m in available_markets if country_code.lower() in m.lower()]
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                return f"⚠️ Mehrere Märkte für {market_input}: {', '.join(matches)}. Nutze ersten: {matches[0]}"
        
        # 4. Keine Übereinstimmung gefunden
        return f"❌ Unbekannter Markt: '{market_input}'. Verfügbare Märkte: {', '.join(available_markets)}"

    # ═══════════════════════════════════════════════════════════════════════
    # SNAPSHOT BUILDER (einmalig beim App-Start)
    # ═══════════════════════════════════════════════════════════════════════
    
    def build_metadata_snapshot() -> dict:
        """
        Baut einen statischen Metadata-Snapshot für Customer Manager Instructions.
        
        Dieser Snapshot wird EINMALIG beim App-Start erstellt und direkt in die
        Instructions des Customer Manager embedded. Dadurch entfallen Runtime-Tool-Calls
        und der Manager kann Metadaten-Fragen direkt beantworten.
        
        Returns:
            dict: Snapshot mit allen Metadaten-Werten als formatierte Strings
                Keys: unique_markets, nps_statistics, sentiment_statistics,
                      date_range, verbatim_statistics, dataset_overview, total_entries
        """
        return {
            "unique_markets": get_unique_markets(),
            "nps_statistics": get_nps_statistics(),
            "sentiment_statistics": get_sentiment_statistics(),
            "date_range": get_date_range(),
            "verbatim_statistics": get_verbatim_statistics(),
            "dataset_overview": get_dataset_overview(),
            "total_entries": str(len(df_metadata)),
        }

    # Rückgabe: Nur noch die build_snapshot Funktion (keine Tools mehr für Agents)
    return build_metadata_snapshot
