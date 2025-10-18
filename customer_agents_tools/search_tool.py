from agents import function_tool


class SearchToolFactory:
    """Enhanced Search Tool Factory with extended error handling for LLM feedback"""

    # Confidence Thresholds for Semantic Search Quality (optimized for Ada-002)
    # Test Performance with Ada-002: Average 92.0%, Range 88.8%-94.1%
    CONFIDENCE_THRESHOLDS = {
        "REJECT": 0.60,      # <60%: No results (Ada-002: all queries >88%)
        "LOW": 0.75,         # <75%: Warning low quality (Ada-002: rarely <75%)
        "MEDIUM": 0.85,      # <85%: Moderate quality (Ada-002: 88-94% typical)
        # ≥85%: High quality (Ada-002 Cross-Lingual Performance)
    }

    @staticmethod
    def create_search_tool(collection):
        """Creates Search Tool with enhanced error handling for LLMs"""

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
            Semantically searches customer feedback database with optional metadata filters.

            Args:
                query (str): Semantic search query in German or English.
                    Examples: "Lieferprobleme", "Service-Beschwerden", "positive Erfahrungen"
                    
                max_results (int, optional): Number of results (3-50). Default: 15.
                    For Top-N analyses set accordingly (e.g. "Top 5" → max_results=5)
                
                market_filter (str | None, optional): Market filter for specific market.
                    Format: "REGION-COUNTRY" (e.g. "C1-DE", "CE-IT")
                    None = search all markets. Default: None
                
                region_filter (str | None, optional): Region filter.
                    Values: "C1", "CE", etc.
                    None = all regions. Default: None
                
                country_filter (str | None, optional): Country filter (ISO 3166-1 Alpha-2).
                    Values: "DE", "IT", "FR", "ES", etc.
                    None = all countries. Default: None
                
                sentiment_filter (str | None, optional): Sentiment filter.
                    Values: "positiv", "neutral", "negativ" (German filter values!)
                    None = all sentiments. Default: None
                
                nps_filter (str | None, optional): NPS category filter.
                    Values: "Promoter" (9-10), "Passive" (7-8), "Detractor" (0-6)
                    None = all NPS categories. Default: None
                
                topic_filter (str | None, optional): Topic filter.
                    Values: "Lieferproblem", "Service", "Produktqualität", "Preis",
                           "Terminvergabe", "Werkstatt", "Kommunikation", "Sonstiges"
                    (German topic values!)
                    None = all topics. Default: None
                
                date_from (str | None, optional): Start date for time range filter.
                    Format: "YYYY-MM-DD" (e.g. "2023-01-01")
                    None = no start date. Default: None
                
                date_to (str | None, optional): End date for time range filter.
                    Format: "YYYY-MM-DD" (e.g. "2023-12-31")
                    None = no end date. Default: None

            Returns:
                str: Formatted results with confidence rating or error message.
                    Format: "[CONFIDENCE]\n[RESULTS]\n[SUMMARY]"
                    
                    On success - List of feedbacks with metadata:
                      • market: Market ID (e.g. "C1-DE")
                      • region: Business region (e.g. "C1", "CE")
                      • country: ISO country code (e.g. "DE", "IT")
                      • nps: Net Promoter Score (0-10)
                      • nps_category: Detractor/Passive/Promoter
                      • sentiment_label: positiv/neutral/negativ
                      • topic: Topic category (e.g. "Service", "Lieferproblem")
                      • date_str: Date as string
                    
                    On error: Detailed error message with solution suggestions
                    On low confidence: Warning about limited relevance
                    On no results: Info about filter combination

            Raises:
                None: All errors are returned as formatted string messages

            Examples:
                >>> # Basic search without filters
                >>> search_customer_feedback("Probleme mit Lieferung", max_results=10)
                "✅ HOHE RELEVANZ\\n✅ Gefunden: 10 Feedbacks (Ø Relevanz: 85.3%)\\n..."
                
                >>> # Delivery problems from last 3 months
                >>> search_customer_feedback(
                ...     query="Lieferverzögerung",
                ...     topic_filter="Lieferproblem",
                ...     date_from="2024-07-01",
                ...     max_results=20
                ... )
                "✅ MODERATE RELEVANZ\\n✅ Gefunden: 15 Feedbacks (Ø Relevanz: 72.1%)\\n..."
                
                >>> # Negative service feedbacks from Germany
                >>> search_customer_feedback(
                ...     query="unfreundlicher Service",
                ...     country_filter="DE",
                ...     sentiment_filter="negativ",
                ...     topic_filter="Service"
                ... )
                "✅ HOHE RELEVANZ\\n✅ Gefunden: 12 Feedbacks (Ø Relevanz: 88.5%)\\n..."
                
                >>> # Detractor feedbacks for specific market
                >>> search_customer_feedback(
                ...     query="Beschwerde",
                ...     market_filter="C1-DE",
                ...     nps_filter="Detractor",
                ...     date_from="2023-01-01",
                ...     date_to="2023-03-31"
                ... )
                "⚠️ NIEDRIGE RELEVANZ\\n⚠️ Gefunden: 8 Feedbacks (Ø Relevanz: 58.2%)\\n..."

            Notes:
                - IMPORTANT: Filter values are in GERMAN (data compatibility)
                  sentiment_filter: "positiv", "neutral", "negativ"
                  topic_filter: "Lieferproblem", "Service", "Terminvergabe", etc.
                - Confidence thresholds (Ada-002): REJECT <60%, LOW <75%, MEDIUM <85%, HIGH ≥85%
                - Ada-002 Performance: Average 92.0%, typical range 88-94%
                - Filters are combined with AND (all must match)
                - Too many filters may result in empty results
                - Semantic search operates AFTER metadata filtering
                - Topic "Sonstiges" contains feedbacks without specific keywords
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
                if top_similarity < SearchToolFactory.CONFIDENCE_THRESHOLDS["REJECT"]:
                    return f"""❌ KEINE RELEVANTEN ERGEBNISSE GEFUNDEN

📊 Qualitäts-Metriken:
   • Beste Übereinstimmung: {top_similarity:.1%}
   • Durchschnitt: {avg_similarity:.1%}
   • Schwellenwert: {SearchToolFactory.CONFIDENCE_THRESHOLDS["REJECT"]:.1%}

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
                elif avg_similarity < SearchToolFactory.CONFIDENCE_THRESHOLDS["LOW"] or \
                     top_similarity < SearchToolFactory.CONFIDENCE_THRESHOLDS["LOW"]:
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
                elif avg_similarity < SearchToolFactory.CONFIDENCE_THRESHOLDS["MEDIUM"]:
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
                if avg_similarity < SearchToolFactory.CONFIDENCE_THRESHOLDS["LOW"]:
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

                        ⚠️  Please inform the user about this technical issue and suggest alternative approaches.
                        """
        return search_customer_feedback
