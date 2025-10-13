import pandas as pd
from agents import function_tool


def create_metadata_tool(collection):
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

    @function_tool
    def get_unique_markets() -> str:
        """Liefert eine kommagetrennte Liste aller eindeutigen Märkte im Datensatz.

        Returns:
            str: Kommagetrennte Liste der Märkte
        """
        if "market" in df_metadata.columns:
            unique_markets = sorted(df_metadata["market"].dropna().unique())
            return ", ".join(unique_markets)
        return "Keine Marktdaten verfügbar."

    @function_tool
    def get_nps_statistics() -> str:
        """Liefert umfassende NPS-Statistiken des Datensatzes.

        Returns:
            str: NPS-Statistiken mit Durchschnitt, Verteilung und Kategorien
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

    @function_tool
    def get_sentiment_statistics() -> str:
        """Liefert Sentiment-Analysestatistiken des Datensatzes.

        Returns:
            str: Sentiment-Verteilung und Durchschnittswerte
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

    @function_tool
    def get_date_range() -> str:
        """Liefert den Zeitraum des Datensatzes.

        Returns:
            str: Start- und Enddatum des Feedback-Zeitraums
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

    @function_tool
    def get_verbatim_statistics() -> str:
        """Liefert Statistiken über die Verbatim-Texte (Token-Anzahl).

        Returns:
            str: Token-Statistiken der Feedback-Texte
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

    @function_tool
    def get_dataset_overview() -> str:
        """Liefert eine kompakte Übersicht des gesamten Datensatzes.

        Returns:
            str: Zusammenfassung aller wichtigen Datensatz-Kennzahlen
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

    # Return dictionary of all available tools
    return {
        "get_unique_markets": get_unique_markets,
        "get_nps_statistics": get_nps_statistics,
        "get_sentiment_statistics": get_sentiment_statistics,
        "get_date_range": get_date_range,
        "get_verbatim_statistics": get_verbatim_statistics,
        "get_dataset_overview": get_dataset_overview,
    }
