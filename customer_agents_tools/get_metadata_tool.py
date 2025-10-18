import pandas as pd


def create_metadata_tool(collection):
    """
    Creates metadata snapshot builder for Customer Manager.
    
    Since no Metadata Analysis Agent exists anymore, functions are
    implemented directly (without @function_tool decorator) and only used
    for snapshot building at app startup.
    
    Args:
        collection: ChromaDB Collection with metadata
    
    Returns:
        callable: build_metadata_snapshot function for snapshot creation
    """
    def get_all_metadata() -> list:
        """All metadata loaded from collection."""
        data = collection.get(include=["metadatas"])
        meta_data = data["metadatas"]
        return meta_data

    def convert_metadata_to_dataframe(metadatas: list) -> pd.DataFrame:
        """
        Converts list of metadata dictionaries into pandas DataFrame.

        Args:
            metadatas (list): List of metadata dictionaries from collection.

        Returns:
            pd.DataFrame: DataFrame with metadata columns (market, region, country,
                nps, sentiment_label, topic, date_str, etc.).
        """
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
    # Direct implementation without @function_tool - only for snapshot building
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_unique_markets() -> str:
        """
        Returns all available markets, regions and countries in dataset.

        Returns:
            str: Structured listing of:
                - Markets: Complete market IDs (e.g. "C1-DE, C1-FR, CE-IT, ...")
                - Regions: Business region codes (e.g. "C1, C3, C5, CE, IT, ...")
                - Countries: ISO 3166-1 Alpha-2 country codes (e.g. "AT, DE, FR, IT, ...")
                or "Keine Marktdaten verfügbar." when data is missing

        Examples:
            >>> get_unique_markets()
            "Märkte (5): C1-DE, C1-FR, CE-IT, C3-AT, IT-IT\\n\
            Regionen (4): C1, C3, CE, IT\\n\
            Länder ISO-Code (4): AT, DE, FR, IT"
        
        Notes:
            - Markets are split at "-" into Region (left) and Country (right)
            - Regions are business-specific codes (not geographic)
            - Countries follow ISO 3166-1 Alpha-2 standard (2-letter codes)
        """
        lines = []
        
        # Märkte
        if "market" in df_metadata.columns:
            unique_markets = sorted(df_metadata["market"].dropna().unique())
            market_count = len(unique_markets)
            lines.append(f"Märkte ({market_count}): {', '.join(unique_markets)}")
        
        # Regionen
        if "region" in df_metadata.columns:
            unique_regions = sorted(df_metadata["region"].dropna().unique())
            # Filtere UNKNOWN heraus
            unique_regions = [r for r in unique_regions if r != "UNKNOWN"]
            region_count = len(unique_regions)
            lines.append(f"Regionen ({region_count}): {', '.join(unique_regions)}")
        
        # Länder (ISO-Format)
        if "country" in df_metadata.columns:
            unique_countries = sorted(df_metadata["country"].dropna().unique())
            # Filtere UNKNOWN heraus
            unique_countries = [c for c in unique_countries if c != "UNKNOWN"]
            country_count = len(unique_countries)
            lines.append(f"Länder ISO-Code ({country_count}): {', '.join(unique_countries)}")
        
        if not lines:
            return "Keine Marktdaten verfügbar."
        
        return "\n".join(lines)

    def get_nps_statistics() -> str:
        """
        Returns comprehensive NPS statistics of the dataset.

        Returns:
            str: Multi-line string with NPS analysis:
                - Number of entries
                - Average (Mean)
                - Median
                - Range (Min-Max)
                - Category distribution (Detractor/Passive/Promoter with percentages)
                When data is missing: "Keine NPS-Daten verfügbar."

        Examples:
            >>> get_nps_statistics()
            "NPS-Statistiken (1500 Einträge):\\n• Durchschnitt: 7.85\\n• Median: 8.0\\n..."

        Notes:
            - NPS categories: Detractor (0-6), Passive (7-8), Promoter (9-10)
            - Percentages refer to total NPS entries
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
        Returns sentiment analysis statistics of the dataset.

        Returns:
            str: Multi-line string with:
                - Sentiment label distribution (positiv/negativ/neutral with percentages)
                - Sentiment scores (average, range)
                When data is missing: "Keine Sentiment-Daten verfügbar."

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

    def get_topic_statistics() -> str:
        """
        Returns topic classification statistics of the dataset.

        Returns:
            str: Multi-line string with:
                - Topic distribution (with percentages)
                - Average confidence scores per topic
                When data is missing: "Keine Topic-Daten verfügbar."

        Examples:
            >>> get_topic_statistics()
            "Topic-Verteilung (1500 Einträge):\\n• Service: 450 (30.0%, Ø Confidence: 0.85)\\n..."
        """
        lines = []

        # Topic Labels
        if "topic" in df_metadata.columns:
            topic_counts = df_metadata["topic"].value_counts()
            total_topics = len(df_metadata["topic"].dropna())
            lines.append(f"Topic-Verteilung ({total_topics} Einträge):")
            
            for topic, count in topic_counts.items():
                percentage = (count / total_topics) * 100
                
                # Durchschnittliche Confidence für dieses Topic berechnen
                if "topic_confidence" in df_metadata.columns:
                    avg_confidence = df_metadata[df_metadata["topic"] == topic]["topic_confidence"].mean()
                    lines.append(f"• {topic}: {count} ({percentage:.1f}%, Ø Confidence: {avg_confidence:.2f})")
                else:
                    lines.append(f"• {topic}: {count} ({percentage:.1f}%)")

        return "\n".join(lines) if lines else "Keine Topic-Daten verfügbar."

    def get_date_range() -> str:
        """
        Returns the time range of the dataset with gap detection.

        Returns:
            str: Time range with start/end date, number of days, entries and gap info.
                 Format: "Zeitraum: 2024-01-01 bis 2024-12-31 (365 Tage Spanne, 1500 Einträge)"
                 With gaps: "Zeitraum: 2024-01-01 bis 2024-12-31 (365 Tage Spanne, 1500 Einträge)
                            ⚠️ Achtung: Nicht alle Tage haben Daten! (150 Tage mit Einträgen)"
                 When data is missing: "Keine Datumsdaten verfügbar."

        Examples:
            >>> get_date_range()
            "Zeitraum: 2024-01-01 bis 2024-12-31 (365 Tage Spanne, 1500 Einträge)"
            
            >>> get_date_range()  # With gaps
            "Zeitraum: 2024-01-01 bis 2024-12-31 (365 Tage Spanne, 1500 Einträge)
            ⚠️ Achtung: Nicht alle Tage haben Daten! Nur 150 von 365 Tagen haben Einträge."
        """
        if "date_str" not in df_metadata.columns:
            return "Keine Datumsdaten verfügbar."

        dates = df_metadata["date_str"].dropna()
        if dates.empty:
            return "Keine gültigen Datumsdaten verfügbar."

        # Min/Max Datum
        date_min_str = dates.min()
        date_max_str = dates.max()
        
        # Parse und formatiere schön (ohne Zeitzone/Zeit wenn nicht nötig)
        try:
            date_min_dt = pd.to_datetime(date_min_str)
            date_max_dt = pd.to_datetime(date_max_str)
            
            # Formatiere als YYYY-MM-DD (ohne Zeit)
            date_min = date_min_dt.strftime('%Y-%m-%d')
            date_max = date_max_dt.strftime('%Y-%m-%d')
            
            # Zeitspanne (Min bis Max)
            total_days_span = (date_max_dt - date_min_dt).days + 1  # +1 weil inklusiv
        except Exception:
            # Fallback: Nutze Original-Strings und berechne Spanne auf 1 Tag
            date_min = str(date_min_str)
            date_max = str(date_max_str)
            total_days_span = 1
        
        # Tatsächliche Tage mit Daten (unique dates)
        unique_dates = pd.to_datetime(dates).dt.date.nunique()
        
        # Basis-Info
        result = f"Zeitraum: {date_min} bis {date_max} ({total_days_span} Tage Spanne, {len(dates)} Einträge)"
        
        # Lücken-Warnung wenn nicht alle Tage Daten haben
        coverage_percent = (unique_dates / total_days_span) * 100
        if coverage_percent < 90:  # Weniger als 90% Coverage
            result += f"\n⚠️ Achtung: Nicht alle Tage haben Daten! Nur {unique_dates} von {total_days_span} Tagen haben Einträge ({coverage_percent:.0f}% Abdeckung)."
        
        return result

    def get_verbatim_statistics() -> str:
        """
        Returns statistics about feedback text lengths (token count).

        Returns:
            str: Multi-line string with:
                - Average token count
                - Median, Min, Max
                - Length distribution (short/medium/long with percentages)
                When data is missing: "Keine Token-Count-Daten verfügbar."

        Examples:
            >>> get_verbatim_statistics()
            "Verbatim-Statistiken (1500 Texte):\\n• Durchschnittliche Länge: 45.3 Token\\n..."

        Notes:
            - Short: ≤20 tokens, Medium: 21-100 tokens, Long: >100 tokens
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
        Returns compact overview of all dataset metrics.

        Returns:
            str: Multi-line overview with:
                - Total number of entries
                - Number/list of markets
                - Average NPS
                - Most common sentiment
                - Time range
                Compressed representation for quick overview.

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

        # Zeitraum (nutze gleiche Formatierung wie get_date_range())
        if "date_str" in df_metadata.columns:
            dates = df_metadata["date_str"].dropna()
            if not dates.empty:
                try:
                    date_min_dt = pd.to_datetime(dates.min())
                    date_max_dt = pd.to_datetime(dates.max())
                    date_min = date_min_dt.strftime('%Y-%m-%d')
                    date_max = date_max_dt.strftime('%Y-%m-%d')
                    lines.append(f"📅 Zeitraum: {date_min} bis {date_max}")
                except Exception:
                    lines.append(f"📅 Zeitraum: {dates.min()} bis {dates.max()}")

        lines.append("")
        lines.append("💡 Verwende die spezifischen Tools für detaillierte Analysen.")

        return "\n".join(lines)

    def resolve_market_name(market_input: str) -> str:
        """
        Maps user inputs to valid dataset market names.
        
        Args:
            market_input (str): User input for market.
                Supports: Abbreviations (DE, AT, CH, US), country names (Deutschland, Austria),
                exact market IDs (C1-DE)

        Returns:
            str: Valid market name from dataset or error message with available markets.
                - Exact match: Market name (e.g. "C1-DE")
                - Partial match: First match or warning on ambiguity
                - Error: "❌ Unbekannter Markt: ... Verfügbare Märkte: ..."

        Examples:
            >>> resolve_market_name("DE")
            "C1-DE"
            
            >>> resolve_market_name("Deutschland")
            "C1-DE"
            
            >>> resolve_market_name("XYZ")
            "❌ Unbekannter Markt: 'XYZ'. Verfügbare Märkte: C1-DE, C2-AT, ..."

        Notes:
            - Mapping: deutschland→DE, österreich→AT, schweiz→CH, usa→US, etc.
            - Case-insensitive matching
            - On ambiguity: Uses first match with warning
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
    # SNAPSHOT BUILDER (once at app startup)
    # ═══════════════════════════════════════════════════════════════════════
    
    def build_metadata_snapshot() -> dict:
        """
        Builds a static metadata snapshot for Customer Manager instructions.
        
        This snapshot is created ONCE at app startup and embedded directly into
        Customer Manager instructions. This eliminates runtime tool calls and
        allows the manager to answer metadata questions directly.
        
        Returns:
            dict: Snapshot with all metadata values as formatted strings
                Keys: unique_markets, nps_statistics, sentiment_statistics,
                      topic_statistics, date_range, verbatim_statistics, 
                      dataset_overview, total_entries
        """
        return {
            "unique_markets": get_unique_markets(),
            "nps_statistics": get_nps_statistics(),
            "sentiment_statistics": get_sentiment_statistics(),
            "topic_statistics": get_topic_statistics(),
            "date_range": get_date_range(),
            "verbatim_statistics": get_verbatim_statistics(),
            "dataset_overview": get_dataset_overview(),
            "total_entries": str(len(df_metadata)),
        }

    # Return: Only build_snapshot function (no more tools for agents)
    return build_metadata_snapshot
