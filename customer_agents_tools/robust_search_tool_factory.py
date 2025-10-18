from agents import function_tool


class RobustSearchToolFactory:
    """Verbesserte Search Tool Factory mit erweiterten Error Handling für LLM Feedback"""

    # Confidence Thresholds für Semantic Search Quality
    CONFIDENCE_THRESHOLDS = {
        "REJECT": 0.40,      # Unter diesem Wert: Keine Ergebnisse
        "LOW": 0.60,         # Unter diesem Wert: Warnung
        "MEDIUM": 0.75,      # Gute Qualität
    }

    @staticmethod
    def create_enhanced_search_tool(collection):
        """Erstellt Search Tool mit verbessertem Error Handling für LLMs"""

        @function_tool
        def search_customer_feedback(query: str, max_results: int = 15) -> str:
            """
            Durchsucht Kundenfeedback-Datenbank semantisch.

            Args:
                query (str): Semantische Suchanfrage in Deutsch oder Englisch.
                    Beispiele: "Lieferprobleme", "Service-Beschwerden", "positive Erfahrungen"
                max_results (int, optional): Anzahl Ergebnisse (3-50). Default: 15.
                    Bei Top-N Analysen entsprechend setzen (z.B. "Top 5" → max_results=5)

            Returns:
                str: Formatierte Ergebnisse mit Confidence-Bewertung oder Fehlermeldung.
                    Format: "[CONFIDENCE]\n[RESULTS]\n[SUMMARY]"
                    - Bei Erfolg: Liste von Feedbacks mit Metadaten (market, nps, sentiment)
                    - Bei Fehler: Detaillierte Fehlermeldung mit Lösungsvorschlägen
                    - Bei niedriger Confidence: Warnung über eingeschränkte Relevanz

            Raises:
                None: Alle Fehler werden als formatierte String-Meldungen zurückgegeben

            Examples:
                >>> search_customer_feedback("Probleme mit Lieferung", max_results=10)
                "✅ HOHE RELEVANZ\\n✅ Gefunden: 10 Feedbacks (Ø Relevanz: 85.3%)\\n..."
                
                >>> search_customer_feedback("xyz123", max_results=5)
                "❌ KEINE RELEVANTEN ERGEBNISSE GEFUNDEN\\n📊 Qualitäts-Metriken:..."

            Notes:
                - Confidence-Schwellenwerte: REJECT <40%, LOW <60%, MEDIUM <75%, HIGH ≥75%
                - Ergebnisse enthalten: Feedback-Text, Market, NPS, Sentiment
                - Bei multiplen Märkten: Automatische Gruppierung in Summary
            """
            print(f"🔍 SEARCH TOOL: query='{query}', max_results={max_results}")

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

            try:
                results = collection.query(
                    query_texts=[query],
                    n_results=max_results,
                    include=["documents", "metadatas", "distances"],
                )

                # Result Validation
                if not results or not results.get("documents"):
                    return "📭 NO RESULTS: No customer feedback found matching your search criteria. Try:\n- Using different keywords\n- Broader search terms\n- Checking if the market/timeframe exists"

                documents = results["documents"][0]
                metadatas = results.get("metadatas", [None])[0] or []
                distances = results.get("distances", [None])[0] or []

                if len(documents) == 0:
                    return "📭 NO RESULTS: Search completed but found 0 matching feedback entries. Try different search terms."

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
                            "nps",
                            "nps_category",
                            "sentiment_label",
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
