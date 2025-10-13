from agents import function_tool


class RobustSearchToolFactory:
    """Verbesserte Search Tool Factory mit erweiterten Error Handling für LLM Feedback"""

    @staticmethod
    def create_enhanced_search_tool(collection):
        """Erstellt Search Tool mit verbessertem Error Handling für LLMs"""

        @function_tool
        def search_customer_feedback(query: str, max_results: int = 15) -> str:
            """
            Search customer feedback with enhanced error handling and LLM-friendly responses.

            Args:
                query (str): Semantic search query in German or English
                max_results (int): Number of results to return (3-50, default: 15)

            Returns:
                str: Formatted results or detailed error message for LLM understanding
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

                # Format results with rich context
                formatted_output = f"✅ SEARCH SUCCESS: Found {len(documents)} relevant customer feedback entries:\n\n"

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
                formatted_output += (
                    f"📈 SUMMARY: Retrieved {len(documents)} feedback entries. "
                )
                if metadatas:
                    markets = set(
                        m.get("market") for m in metadatas if m and m.get("market")
                    )
                    if markets:
                        formatted_output += (
                            f"Markets covered: {', '.join(sorted(markets))}. "
                        )

                formatted_output += "Use this data for your analysis."

                print(f"✅ SEARCH SUCCESS: Returned {len(documents)} results")
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
