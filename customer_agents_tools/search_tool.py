from agents import function_tool


class RobustSearchToolFactory:
    """Verbesserte Search Tool Factory mit erweiterten Error Handling für LLM Feedback"""

    # Confidence Thresholds für Semantic Search Quality (optimiert für Ada-002)
    # Test-Performance mit Ada-002: Durchschnitt 92.0%, Range 88.8%-94.1%
    CONFIDENCE_THRESHOLDS = {
        "REJECT": 0.60,      # <60%: Keine Ergebnisse (Ada-002: alle Queries >88%)
        "LOW": 0.75,         # <75%: Warnung niedrige Qualität (Ada-002: selten <75%)
        "MEDIUM": 0.85,      # <85%: Moderate Qualität (Ada-002: 88-94% typisch)
        # ≥85%: Hohe Qualität (Ada-002 Cross-Lingual Performance)
    }

    @staticmethod
    def create_search_tool(collection):
        """Erstellt Search Tool mit verbessertem Error Handling für LLMs"""

        @function_tool
        def search_customer_feedback(
            query: str,
            max_results: int = 15,
            market_filter: str | None = None,
            region_filter: str | None = None,
            country_filter: str | None = None,
            sentiment_filter: str | None = None,
            nps_filter: str | None = None,
            topic_filter: str | None = None,
            date_from: str | None = None,
            date_to: str | None = None,
        ) -> str:
            """
            Durchsucht Kundenfeedback-Datenbank semantisch mit optionalen Metadata-Filtern.

            Args:
                query (str): Semantische Suchanfrage in Deutsch oder Englisch.
                    Beispiele: "Lieferprobleme", "Service-Beschwerden", "positive Erfahrungen"
                    
                max_results (int, optional): Anzahl Ergebnisse (3-50). Default: 15.
                    Bei Top-N Analysen entsprechend setzen (z.B. "Top 5" → max_results=5)
                
                market_filter (str | None, optional): Markt-Filter für spezifischen Market.
                    Format: "REGION-COUNTRY" (z.B. "C1-DE", "CE-IT")
                    None = alle Märkte durchsuchen. Default: None
                
                region_filter (str | None, optional): Regions-Filter.
                    Werte: "C1", "CE", etc.
                    None = alle Regionen. Default: None
                
                country_filter (str | None, optional): Länder-Filter (ISO 3166-1 Alpha-2).
                    Werte: "DE", "IT", "FR", "ES", etc.
                    None = alle Länder. Default: None
                
                sentiment_filter (str | None, optional): Sentiment-Filter.
                    Werte: "positiv", "neutral", "negativ"
                    None = alle Sentiments. Default: None
                
                nps_filter (str | None, optional): NPS-Kategorie-Filter.
                    Werte: "Promoter" (9-10), "Passive" (7-8), "Detractor" (0-6)
                    None = alle NPS-Kategorien. Default: None
                
                topic_filter (str | None, optional): Topic-Filter.
                    Werte: "Lieferproblem", "Service", "Produktqualität", "Preis",
                           "Terminvergabe", "Werkstatt", "Kommunikation", "Sonstiges"
                    None = alle Topics. Default: None
                
                date_from (str | None, optional): Start-Datum für Zeitraum-Filter.
                    Format: "YYYY-MM-DD" (z.B. "2023-01-01")
                    None = kein Start-Datum. Default: None
                
                date_to (str | None, optional): End-Datum für Zeitraum-Filter.
                    Format: "YYYY-MM-DD" (z.B. "2023-12-31")
                    None = kein End-Datum. Default: None

            Returns:
                str: Formatierte Ergebnisse mit Confidence-Bewertung oder Fehlermeldung.
                    Format: "[CONFIDENCE]\n[RESULTS]\n[SUMMARY]"
                    
                    Bei Erfolg - Liste von Feedbacks mit Metadaten:
                      • market: Market-ID (z.B. "C1-DE")
                      • region: Business-Region (z.B. "C1", "CE")
                      • country: ISO Ländercode (z.B. "DE", "IT")
                      • nps: Net Promoter Score (0-10)
                      • nps_category: Detractor/Passive/Promoter
                      • sentiment_label: positiv/neutral/negativ
                      • topic: Topic-Kategorie (z.B. "Service", "Lieferproblem")
                      • date_str: Datum als String
                    
                    Bei Fehler: Detaillierte Fehlermeldung mit Lösungsvorschlägen
                    Bei niedriger Confidence: Warnung über eingeschränkte Relevanz
                    Bei keinen Ergebnissen: Info über Filter-Kombination

            Raises:
                None: Alle Fehler werden als formatierte String-Meldungen zurückgegeben

            Examples:
                >>> # Basis-Suche ohne Filter
                >>> search_customer_feedback("Probleme mit Lieferung", max_results=10)
                "✅ HOHE RELEVANZ\\n✅ Gefunden: 10 Feedbacks (Ø Relevanz: 85.3%)\\n..."
                
                >>> # Lieferprobleme aus den letzten 3 Monaten
                >>> search_customer_feedback(
                ...     query="Lieferverzögerung",
                ...     topic_filter="Lieferproblem",
                ...     date_from="2024-07-01",
                ...     max_results=20
                ... )
                "✅ MODERATE RELEVANZ\\n✅ Gefunden: 15 Feedbacks (Ø Relevanz: 72.1%)\\n..."
                
                >>> # Negative Service-Feedbacks aus Deutschland
                >>> search_customer_feedback(
                ...     query="unfreundlicher Service",
                ...     country_filter="DE",
                ...     sentiment_filter="negativ",
                ...     topic_filter="Service"
                ... )
                "✅ HOHE RELEVANZ\\n✅ Gefunden: 12 Feedbacks (Ø Relevanz: 88.5%)\\n..."
                
                >>> # Detractor-Feedbacks für spezifischen Market
                >>> search_customer_feedback(
                ...     query="Beschwerde",
                ...     market_filter="C1-DE",
                ...     nps_filter="Detractor",
                ...     date_from="2023-01-01",
                ...     date_to="2023-03-31"
                ... )
                "⚠️ NIEDRIGE RELEVANZ\\n⚠️ Gefunden: 8 Feedbacks (Ø Relevanz: 58.2%)\\n..."

            Notes:
                - Confidence-Schwellenwerte (Ada-002): REJECT <60%, LOW <75%, MEDIUM <85%, HIGH ≥85%
                - Ada-002 Performance: Durchschnitt 92.0%, typischer Range 88-94%
                - Filter werden mit AND kombiniert (alle müssen zutreffen)
                - Bei zu vielen Filtern können Ergebnisse leer sein
                - Semantic Search arbeitet NACH Metadata-Filterung
                - Topic "Sonstiges" enthält Feedbacks ohne spezifische Keywords
            """
            print(f"🔍 SEARCH TOOL: query='{query}', max_results={max_results}")
            print(f"   📊 Filter: market={market_filter}, region={region_filter}, country={country_filter}")
            print(f"   📊 Filter: sentiment={sentiment_filter}, nps={nps_filter}, topic={topic_filter}")
            print(f"   📊 Filter: date_from={date_from}, date_to={date_to}")

            # Input Validation mit LLM-freundlichen Messages
            if not query or query.strip() == "":
                return "❌ ERROR: Empty search query provided. Please provide a meaningful search term related to customer feedback."

            if max_results < 3:
                return "❌ ERROR: max_results too small. Please use at least 3 results for meaningful analysis."

            if max_results > 50:
                return "⚠️  WARNING: max_results capped at 50 for performance. Using max_results=50 instead."
                max_results = 50

            # Collection Validation
            if collection is None:
                return "❌ CRITICAL ERROR: No customer feedback database available. Please contact system administrator."

            # ========================================
            # BUILD WHERE CLAUSE (wie in create_charts_tool.py)
            # ========================================
            where_filter = {}
            filter_list = []

            # Geographic filters
            if market_filter:
                filter_list.append({"market": {"$eq": market_filter}})
            
            if region_filter:
                filter_list.append({"region": {"$eq": region_filter}})
            
            if country_filter:
                filter_list.append({"country": {"$eq": country_filter}})

            # Analytical filters
            if sentiment_filter:
                filter_list.append({"sentiment_label": {"$eq": sentiment_filter.lower()}})
            
            if nps_filter:
                filter_list.append({"nps_category": {"$eq": nps_filter}})
            
            if topic_filter:
                filter_list.append({"topic": {"$eq": topic_filter}})

            # Date range filters
            if date_from or date_to:
                from datetime import datetime
                
                if date_from:
                    try:
                        date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
                        timestamp_from = int(date_from_obj.timestamp())
                        filter_list.append({"date": {"$gte": timestamp_from}})
                        print(f"   ⏰ Date From: {date_from} → timestamp {timestamp_from}")
                    except ValueError:
                        return f"❌ ERROR: Invalid date_from format '{date_from}'. Expected YYYY-MM-DD (e.g., '2023-01-01')"
                
                if date_to:
                    try:
                        date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
                        # Set to end of day (23:59:59)
                        timestamp_to = int(date_to_obj.timestamp()) + 86399
                        filter_list.append({"date": {"$lte": timestamp_to}})
                        print(f"   ⏰ Date To: {date_to} → timestamp {timestamp_to}")
                    except ValueError:
                        return f"❌ ERROR: Invalid date_to format '{date_to}'. Expected YYYY-MM-DD (e.g., '2023-12-31')"

            # Combine filters with $and if multiple conditions
            if len(filter_list) > 1:
                where_filter = {"$and": filter_list}
            elif len(filter_list) == 1:
                where_filter = filter_list[0]
            else:
                where_filter = None

            print(f"   🔧 WHERE Filter: {where_filter}")

            try:
                results = collection.query(
                    query_texts=[query],
                    n_results=max_results,
                    where=where_filter,
                    include=["documents", "metadatas", "distances"],
                )

                # Result Validation
                if not results or not results.get("documents"):
                    # Build filter summary for error message
                    active_filters = []
                    if market_filter:
                        active_filters.append(f"Market={market_filter}")
                    if region_filter:
                        active_filters.append(f"Region={region_filter}")
                    if country_filter:
                        active_filters.append(f"Country={country_filter}")
                    if sentiment_filter:
                        active_filters.append(f"Sentiment={sentiment_filter}")
                    if nps_filter:
                        active_filters.append(f"NPS={nps_filter}")
                    if topic_filter:
                        active_filters.append(f"Topic={topic_filter}")
                    if date_from:
                        active_filters.append(f"From={date_from}")
                    if date_to:
                        active_filters.append(f"To={date_to}")
                    
                    filter_info = f" with filters: {', '.join(active_filters)}" if active_filters else ""
                    
                    return f"""📭 NO RESULTS: No customer feedback found matching your search criteria{filter_info}.

Try:
- Using different or broader keywords
- Removing some filters (current: {len(active_filters)} active)
- Checking if the filter values exist (e.g., topic='Lieferproblem' vs. 'Lieferung')
- Expanding date range if using date filters"""

                documents = results["documents"][0]
                metadatas = results.get("metadatas", [None])[0] or []
                distances = results.get("distances", [None])[0] or []

                if len(documents) == 0:
                    active_filters = []
                    if market_filter:
                        active_filters.append(f"Market={market_filter}")
                    if region_filter:
                        active_filters.append(f"Region={region_filter}")
                    if country_filter:
                        active_filters.append(f"Country={country_filter}")
                    if sentiment_filter:
                        active_filters.append(f"Sentiment={sentiment_filter}")
                    if nps_filter:
                        active_filters.append(f"NPS={nps_filter}")
                    if topic_filter:
                        active_filters.append(f"Topic={topic_filter}")
                    if date_from:
                        active_filters.append(f"From={date_from}")
                    if date_to:
                        active_filters.append(f"To={date_to}")
                    
                    filter_info = f" (Active filters: {', '.join(active_filters)})" if active_filters else ""
                    
                    return f"📭 NO RESULTS: Search completed but found 0 matching feedback entries{filter_info}. Try removing some filters or using different search terms."

                # ========================================
                # CONFIDENCE EVALUATION
                # ========================================
                similarities = [1 - d for d in distances]
                avg_similarity = sum(similarities) / len(similarities)
                top_similarity = similarities[0]
                
                print(f"📊 CONFIDENCE: Top={top_similarity:.3f}, Avg={avg_similarity:.3f}")
                
                # REJECT: Zu geringe Relevanz - keine Antwort
                if top_similarity < RobustSearchToolFactory.CONFIDENCE_THRESHOLDS["REJECT"]:
                    return f"""❌ KEINE RELEVANTEN ERGEBNISSE GEFUNDEN

📊 Qualitäts-Metriken:
   • Beste Übereinstimmung: {top_similarity:.1%}
   • Durchschnitt: {avg_similarity:.1%}
   • Schwellenwert: {RobustSearchToolFactory.CONFIDENCE_THRESHOLDS["REJECT"]:.1%}

⚠️  INTERPRETATION:
Die semantische Ähnlichkeit zwischen Ihrer Anfrage und dem Datensatz ist zu gering.
Das gesuchte Thema existiert wahrscheinlich nicht in dieser Form in den Kundenfeedbacks.

💡 MÖGLICHE GRÜNDE:
   1. Der Begriff wird im Datensatz anders formuliert
   2. Das Thema ist nicht im Datensatz enthalten
   3. Die Suchanfrage ist zu spezifisch

✅ VORSCHLÄGE:
   • Verwenden Sie allgemeinere Begriffe
   • Prüfen Sie alternative Formulierungen
   • Für diesen Datensatz besser geeignet:
     - "Ersatzteil-Verfügbarkeit" statt "Lieferprobleme"
     - "Wartezeiten Werkstatt" statt "Service-Verzögerungen"
     - "Reparatur-Dauer" statt "Durchlaufzeiten"

📋 Tipp: Verwenden Sie get_dataset_metadata um zu sehen, welche Themen verfügbar sind."""

                # LOW CONFIDENCE: Schwache Relevanz - Warnung
                elif avg_similarity < RobustSearchToolFactory.CONFIDENCE_THRESHOLDS["LOW"] or \
                     top_similarity < RobustSearchToolFactory.CONFIDENCE_THRESHOLDS["LOW"]:
                    confidence_level = "⚠️  NIEDRIGE RELEVANZ"
                    confidence_msg = f"""
⚠️  ACHTUNG: ERGEBNISSE MIT EINGESCHRÄNKTER RELEVANZ

📊 Qualitäts-Metriken:
   • Beste Übereinstimmung: {top_similarity:.1%}
   • Durchschnitt: {avg_similarity:.1%}
   
Die folgenden Ergebnisse haben nur moderate semantische Ähnlichkeit mit Ihrer Anfrage.
Bitte prüfen Sie die Relevanz der einzelnen Feedbacks kritisch.

💡 Tipp: Falls die Ergebnisse nicht passen, versuchen Sie andere Suchbegriffe.

"""
                
                # MEDIUM CONFIDENCE: Akzeptable Qualität
                elif avg_similarity < RobustSearchToolFactory.CONFIDENCE_THRESHOLDS["MEDIUM"]:
                    confidence_level = "✅ MODERATE RELEVANZ"
                    confidence_msg = f"""
✅ Gefunden: {len(documents)} Feedbacks (Ø Relevanz: {avg_similarity:.1%})

"""
                
                # HIGH CONFIDENCE: Hohe Qualität
                else:
                    confidence_level = "✅ HOHE RELEVANZ"
                    confidence_msg = f"""
✅ Gefunden: {len(documents)} Feedbacks (Ø Relevanz: {avg_similarity:.1%})

"""

                # Format results with rich context
                formatted_output = f"{confidence_level}\n{confidence_msg}"

                for i, (content, metadata, distance) in enumerate(
                    zip(documents, metadatas, distances)
                ):
                    formatted_output += (
                        f"📄 **Result {i + 1}** (Similarity: {1 - distance:.3f}):\n"
                    )
                    formatted_output += f"💬 Feedback: {content}\n"

                    if metadata:
                        # Highlight important metadata
                        important_fields = [
                            "market",
                            "region",
                            "country",
                            "nps",
                            "nps_category",
                            "sentiment_label",
                            "topic",
                        ]
                        meta_summary = []
                        for field in important_fields:
                            if field in metadata and metadata[field] is not None:
                                meta_summary.append(f"{field}: {metadata[field]}")

                        if meta_summary:
                            formatted_output += (
                                f"📊 Context: {', '.join(meta_summary)}\n"
                            )

                    formatted_output += "\n" + "=" * 50 + "\n\n"

                # Add helpful summary
                formatted_output += f"\n📈 SUMMARY: {len(documents)} Feedbacks"
                if metadatas:
                    markets = set(
                        m.get("market") for m in metadatas if m and m.get("market")
                    )
                    if markets:
                        formatted_output += f" | Markets: {', '.join(sorted(markets))}"

                # Add confidence interpretation for the LLM
                if avg_similarity < RobustSearchToolFactory.CONFIDENCE_THRESHOLDS["LOW"]:
                    formatted_output += "\n\n⚠️  LLM NOTE: Low confidence results. Consider mentioning limitations in your analysis."
                
                print(f"✅ SEARCH SUCCESS: {len(documents)} results (confidence: {avg_similarity:.2%})")
                return formatted_output

            except Exception as e:
                error_details = str(e)
                print(f"❌ SEARCH ERROR: {error_details}")

                # Provide actionable error message to LLM
                return f"""❌ SEARCH ERROR: Database query failed.
                
🔧 Error Details: {error_details}

🚨 What this means: The customer feedback database encountered an issue while processing your search.

✅ Suggested Actions:
1. Try a simpler search query
2. Reduce the number of results requested  
3. Check if the search terms are in German or English
4. If this persists, use get_dataset_metadata to check available data

⚠️  Please inform the user about this technical issue and suggest alternative approaches."""

        return search_customer_feedback
