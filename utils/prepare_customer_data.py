# type: ignore
import pandas as pd
import tiktoken
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .topic_keywords import classify_feedback_topic


class PrepareCustomerData(object):
    """
    A comprehensive data preparation class for customer feedback analysis.

    This class automatically enhances customer feedback data with:
    - NPS score categorization (Detractor, Passive, Promoter)
    - Token count calculation for feedback texts
    - Sentiment analysis using VADER sentiment analyzer
    - Topic classification using keyword matching
    - Market split into region and country code (ISO format)
    
    All features are applied automatically to streamline the data preparation pipeline.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        nps_category_col_name: str = "NPS",
        feedback_col_name: str = "Verbatim",
        feedback_token_model: str = "gpt-4o-mini",
        market_col_name: str = "Market",
    ):
        """
        Initialize the PrepareCustomerData processor and automatically enhance the data.

        Args:
            data (pd.DataFrame): Input DataFrame containing customer feedback data
            nps_category_col_name (str, optional): Column name containing NPS scores. Defaults to "NPS".
            feedback_col_name (str, optional): Column name containing feedback text. Defaults to "Verbatim".
            feedback_token_model (str, optional): OpenAI model for token encoding. Defaults to "gpt-4o-mini".
            market_col_name (str, optional): Column name containing market information. Defaults to "Market".

        Raises:
            ValueError: If required columns are not found in the DataFrame.
        """
        self.data = data
        self.nps_category_col_name = nps_category_col_name
        self.feedback_col_name = feedback_col_name
        self.feedback_token_model = feedback_token_model
        self.market_col_name = market_col_name

        # Validierung der DataFrame-Spalten
        if nps_category_col_name not in data.columns:
            raise ValueError(
                f"NPS column '{nps_category_col_name}' not found in DataFrame"
            )
        if feedback_col_name not in data.columns:
            raise ValueError(
                f"Feedback column '{feedback_col_name}' not found in DataFrame"
            )
        if market_col_name not in data.columns:
            raise ValueError(
                f"Market column '{market_col_name}' not found in DataFrame"
            )

        # Execute all enhancements automatically
        print("\n🔧 Starting Data Enhancement Pipeline...")
        self.categorize_nps_score()
        self.split_market_column()
        self.calculate_feedback_context_length()
        self.sentiment_analysis()
        self.classify_topics()
        print("✅ Data Enhancement completed!\n")

    def categorize_nps_score(self) -> pd.DataFrame:
        """
        Categorizes Net Promoter Score (NPS) values into standard categories.

        Creates a new column 'nps_category' with the following mapping:
        - 0-6: "Detractor" (customers likely to discourage others)
        - 7-8: "Passive" (customers satisfied but not enthusiastic)
        - 9-10: "Promoter" (customers likely to recommend)
        - NaN or invalid: "Invalid" (missing or out-of-range values)

        Args:
            None (uses self.data and self.nps_category_col_name)

        Returns:
            pd.DataFrame: The updated DataFrame with added 'nps_category' column containing
                         categorical NPS classifications

        Notes:
            - Modifies self.data in-place by adding the 'nps_category' column
            - Handles string inputs by converting to integers
            - Returns "Invalid" for out-of-range or non-numeric values
            - Uses standard NPS categorization thresholds
        """

        def categorize_single_score(score):
            # Type Checking
            if isinstance(score, str) and score.isnumeric():
                try:
                    score = int(score)
                except TypeError:
                    return "Invalid"

            # Logic
            if 0 <= score <= 6:
                return "Detractor"
            elif 7 <= score <= 8:
                return "Passive"
            elif 9 <= score <= 10:
                return "Promoter"
            else:
                return "Invalid"

        self.data["nps_category"] = self.data[self.nps_category_col_name].apply(
            categorize_single_score
        )
        return self.data

    def split_market_column(self) -> pd.DataFrame:
        """
        Splits the Market column into Region and Country (ISO format).

        This method splits market identifiers (e.g., "C1-DE", "CE-IT") into:
        - Region: The prefix before the dash (e.g., "C1", "CE", "IT")
        - Country: The ISO country code after the dash (e.g., "DE", "IT", "FR")

        Creates two new columns:
        - 'region': Business region identifier (uppercase)
        - 'country': ISO 3166-1 alpha-2 country code (uppercase)

        Args:
            None (uses self.data and self.market_col_name)

        Returns:
            pd.DataFrame: Updated DataFrame with two new columns:
                - 'region' (str): Business region identifier
                - 'country' (str): ISO 3166-1 alpha-2 country code

        Notes:
            - Handles missing or malformed market values gracefully (returns "UNKNOWN")
            - If no dash is found, treats entire value as region with "UNKNOWN" country
            - If multiple dashes exist, uses first part as region and last part as country
            - Modifies self.data in-place by adding region and country columns
            - Prints statistics: unique regions/countries and top 5 of each
            - All values are converted to uppercase for consistency
        """

        def split_market(market_value):
            if pd.isna(market_value) or not isinstance(market_value, str):
                return {"region": "UNKNOWN", "country": "UNKNOWN"}

            try:
                # Split at hyphen/dash
                parts = market_value.split("-")
                
                if len(parts) == 2:
                    return {
                        "region": parts[0].strip().upper(),
                        "country": parts[1].strip().upper()
                    }
                elif len(parts) == 1:
                    # No dash found - entire value is region
                    return {
                        "region": parts[0].strip().upper(),
                        "country": "UNKNOWN"
                    }
                else:
                    # Multiple dashes - take first and last parts
                    return {
                        "region": parts[0].strip().upper(),
                        "country": parts[-1].strip().upper()
                    }
            except Exception:
                return {"region": "UNKNOWN", "country": "UNKNOWN"}

        # Split market for each row
        print("🌍 Splitting Market into Region and Country...")
        market_results = self.data[self.market_col_name].apply(split_market)

        # Split results into separate columns
        self.data["region"] = market_results.apply(lambda x: x["region"])
        self.data["country"] = market_results.apply(lambda x: x["country"])

        # Print statistics
        unique_regions = self.data["region"].nunique()
        unique_countries = self.data["country"].nunique()
        print(f"   • Found Regions: {unique_regions}")
        print(f"   • Found Countries: {unique_countries}")
        
        # Show top regions and countries
        top_regions = self.data["region"].value_counts().head(5)
        print(f"   • Top Regions: {', '.join(top_regions.index.tolist())}")
        
        top_countries = self.data["country"].value_counts().head(5)
        print(f"   • Top Countries: {', '.join(top_countries.index.tolist())}")

        return self.data

    def calculate_feedback_context_length(self) -> pd.DataFrame:
        """
        Calculates token count for feedback texts using tiktoken encoding.

        This method uses OpenAI's tiktoken library to accurately count tokens
        for the specified model, which is crucial for:
        - API cost estimation
        - Context window management
        - Text processing optimization

        Args:
            None (uses self.feedback_token_model and self.feedback_col_name)

        Returns:
            pd.DataFrame: Updated DataFrame with new column 'verbatim_token_count' (int)
                         containing the token count for each feedback text

        Notes:
            - Falls back to 'cl100k_base' encoding for unknown models
            - Handles NaN values and non-string data gracefully (returns 0)
            - Returns 0 tokens for empty or invalid text entries
            - Modifies self.data in-place by adding the token count column
            - Column name format: '{feedback_col_name}_token_count'
            - Uses model-specific encoding for accurate token counting
        """
        # Load encoding for the corresponding model
        try:
            encoding = tiktoken.encoding_for_model(self.feedback_token_model)
        except KeyError:
            # Fallback for unknown models
            encoding = tiktoken.get_encoding(
                "cl100k_base"
            )  # Standard for GPT-4/GPT-3.5

        def count_tokens(text):
            if pd.isna(text) or not isinstance(text, str):
                return 0
            # Simple: encode text to tokens and return count
            return len(encoding.encode(str(text)))

        # Calculate token count for each row
        self.data[f"{self.feedback_col_name}_token_count"] = self.data[
            self.feedback_col_name
        ].apply(count_tokens)

        return self.data

    def sentiment_analysis(self) -> pd.DataFrame:
        """
        Performs sentiment analysis on feedback texts using VADER sentiment analyzer.

        This method uses VADER (Valence Aware Dictionary and sEntiment Reasoner) 
        to analyze sentiment and provides both categorical labels and confidence scores.

        Args:
            None (uses self.data and self.feedback_col_name)

        Returns:
            pd.DataFrame: Updated DataFrame with two new columns:
                - 'sentiment_label' (str): Categorical sentiment classification:
                    * "positiv" (compound score ≥ 0.5)
                    * "neutral" (compound score > -0.5 and < 0.5)
                    * "negativ" (compound score ≤ -0.5)
                    * "UNKNOWN" (for NaN/non-string inputs)
                    * "ERROR" (for processing exceptions)
                - 'sentiment_score' (float): VADER compound score between -1.0 and 1.0

        Notes:
            - Handles NaN values and non-string data by returning "UNKNOWN" label with 0.0 score
            - Returns "ERROR" label with 0.0 score for processing exceptions
            - Modifies self.data in-place by adding both sentiment columns
            - Uses VADER's compound score for classification thresholds
            - Scores: -1.0 (most negative) to +1.0 (most positive)
        """
        analyzer = SentimentIntensityAnalyzer()

        def analyze_row(text):
            if pd.isna(text) or not isinstance(text, str):
                return {"label": "UNKNOWN", "sentiment_score": 0.0}

            try:
                # Call analyzer and return result
                scores = analyzer.polarity_scores(text)

                score = scores["compound"]
                sentiment = ""

                if score >= 0.5:
                    sentiment = "positiv"
                elif score > -0.5 and score < 0.5:
                    sentiment = "neutral"
                elif score <= -0.5:
                    sentiment = "negativ"
                else:
                    sentiment = "UNKNOWN"
                return {"label": sentiment, "sentiment_score": score}
            except Exception:
                return {"label": "ERROR", "sentiment_score": 0.0}

        # Analyze sentiment for each row
        sentiment_results = self.data[self.feedback_col_name].apply(analyze_row)

        # Split results into separate columns
        self.data["sentiment_label"] = sentiment_results.apply(lambda x: x["label"])
        self.data["sentiment_score"] = sentiment_results.apply(
            lambda x: x["sentiment_score"]
        )

        return self.data

    def classify_topics(self) -> pd.DataFrame:
        """
        Classifies feedback texts into topics based on keyword matching.

        This method uses the topic_keywords.py logic to assign each feedback text
        to a category (e.g., "Lieferproblem", "Service", "Produktqualität").

        Args:
            None (uses self.data and self.feedback_col_name)

        Returns:
            pd.DataFrame: Updated DataFrame with two new columns:
                - 'topic' (str): Topic category classification:
                    * "Lieferproblem" (delivery issues)
                    * "Service" (customer service)
                    * "Produktqualität" (product quality)
                    * "Preis" (pricing)
                    * "Terminvergabe" (appointment scheduling)
                    * "Werkstatt" (workshop/repair)
                    * "Kommunikation" (communication)
                    * "Fahrzeugübergabe" (vehicle handover)
                    * "Probefahrt" (test drive)
                    * "Finanzierung" (financing)
                    * "Ersatzwagen" (replacement vehicle)
                    * "Sonstiges" (other/misc)
                - 'topic_confidence' (float): Confidence score between 0.0 and 1.0

        Notes:
            - Uses keyword matching for fast classification
            - Falls back to "Sonstiges" if no topic matches
            - Handles NaN values and non-string data (returns "Sonstiges" with 0.0 confidence)
            - Returns "Sonstiges" with 0.0 confidence for processing exceptions
            - Modifies self.data in-place by adding both topic columns
            - Prints detailed topic distribution statistics with percentages
        """

        def classify_row(text):
            if pd.isna(text) or not isinstance(text, str):
                return {"topic": "Sonstiges", "confidence": 0.0}

            try:
                topic, confidence = classify_feedback_topic(text)
                return {"topic": topic, "confidence": confidence}
            except Exception:
                return {"topic": "Sonstiges", "confidence": 0.0}

        # Classify topic for each row
        print("\n🔍 Classifying Topics...")
        topic_results = self.data[self.feedback_col_name].apply(classify_row)

        # Split results into separate columns
        self.data["topic"] = topic_results.apply(lambda x: x["topic"])
        self.data["topic_confidence"] = topic_results.apply(lambda x: x["confidence"])

        # Print statistics
        topic_counts = self.data["topic"].value_counts()
        print(f"\n📊 Topic Distribution:")
        for topic, count in topic_counts.items():
            percentage = (count / len(self.data)) * 100
            print(f"   • {topic}: {count:,} ({percentage:.1f}%)")

        return self.data
