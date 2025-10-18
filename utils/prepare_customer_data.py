# type: ignore
import pandas as pd
import tiktoken
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from utils.topic_keywords import classify_feedback_topic


class PrepareCustomerData(object):
    """
    A comprehensive data preparation class for customer feedback analysis.

    This class provides functionality to enhance customer feedback data with:
    - NPS score categorization (Detractor, Passive, Promoter)
    - Token count calculation for feedback texts
    - Sentiment analysis using Hugging Face transformers
    """

    def __init__(
        self,
        data: pd.DataFrame,
        nps_category: bool = False,
        nps_category_col_name: str = "NPS",
        feedback_length: bool = False,
        feedback_token_model: str = "gpt-4o-mini",
        feedback_col_name: str = "Verbatim",
        sentiment_analysis: bool = False,
        sentiment_col_name: str = "Verbatim",
        topic_classification: bool = False,
        topic_col_name: str = "Verbatim",
    ):
        """
        Initialize the PrepareCustomerData processor with optional data enhancement features.

        Args:
            data (pd.DataFrame): Input DataFrame containing customer feedback data
            nps_category (bool, optional): Enable NPS score categorization. Defaults to False.
            nps_category_col_name (str, optional): Column name containing NPS scores. Defaults to "NPS".
            feedback_length (bool, optional): Enable token count calculation. Defaults to False.
            feedback_token_model (str, optional): OpenAI model for token encoding. Defaults to "gpt-4o-mini".
            feedback_col_name (str, optional): Column name containing feedback text. Defaults to "Verbatim".
            sentiment_analysis (bool, optional): Enable sentiment analysis. Defaults to False.
            sentiment_col_name (str, optional): Column name for sentiment analysis. Defaults to "Verbatim".
            topic_classification (bool, optional): Enable topic classification. Defaults to False.
            topic_col_name (str, optional): Column name for topic classification. Defaults to "Verbatim".

        Raises:
            ValueError: If required columns are not found in the DataFrame when corresponding features are enabled.
        """
        self.data = data

        # Validierung der DataFrame-Spalten
        if nps_category and nps_category_col_name not in data.columns:
            raise ValueError(
                f"NPS column '{nps_category_col_name}' not found in DataFrame"
            )
        if feedback_length and feedback_col_name not in data.columns:
            raise ValueError(
                f"Feedback column '{feedback_col_name}' not found in DataFrame"
            )
        if sentiment_analysis and sentiment_col_name not in data.columns:
            raise ValueError(
                f"Sentiment column '{sentiment_col_name}' not found in DataFrame"
            )
        if topic_classification and topic_col_name not in data.columns:
            raise ValueError(
                f"Topic column '{topic_col_name}' not found in DataFrame"
            )

        # Bearbeitung
        if nps_category:
            self.nps_category_col_name = nps_category_col_name
            self.categorize_nps_score()
        if feedback_length:
            self.feedback_col_name = feedback_col_name
            self.feedback_token_model = feedback_token_model
            self.calculate_feedback_context_length()
        if sentiment_analysis:
            self.sentiment_col_name = sentiment_col_name
            self.sentiment_analysis()
        if topic_classification:
            self.topic_col_name = topic_col_name
            self.classify_topics()

    def categorize_nps_score(self) -> pd.DataFrame:
        """
        Categorize Net Promoter Score (NPS) values into standard categories.

        Creates a new column 'nps_category' with the following mapping:
        - 0-6: "Detractor" (customers likely to discourage others)
        - 7-8: "Passive" (customers satisfied but not enthusiastic)
        - 9-10: "Promoter" (customers likely to recommend)
        - NaN or invalid: "Invalid" (missing or out-of-range values)

        Returns:
            pd.DataFrame: The updated DataFrame with added 'nps_category' column

        Note:
            Modifies self.data in-place by adding the 'nps_category' column.
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

    def calculate_feedback_context_length(self) -> pd.DataFrame:
        """
        Calculate token count for feedback texts using tiktoken encoding.

        This method uses OpenAI's tiktoken library to accurately count tokens
        for the specified model, which is crucial for:
        - API cost estimation
        - Context window management
        - Text processing optimization

        Args:
            Uses self.feedback_token_model (str): OpenAI model name for token encoding
            Uses self.feedback_col_name (str): Column name containing text to tokenize

        Returns:
            pd.DataFrame: Updated DataFrame with new column '{feedback_col_name}_token_count'

        Note:
            - Falls back to 'cl100k_base' encoding for unknown models
            - Handles NaN values and non-string data gracefully
            - Returns 0 tokens for empty or invalid text entries
            - Modifies self.data in-place by adding the token count column
        """
        # Encoding für das entsprechende Modell laden
        try:
            encoding = tiktoken.encoding_for_model(self.feedback_token_model)
        except KeyError:
            # Fallback für unbekannte Modelle
            encoding = tiktoken.get_encoding(
                "cl100k_base"
            )  # Standard für GPT-4/GPT-3.5

        def count_tokens(text):
            if pd.isna(text) or not isinstance(text, str):
                return 0
            # Sehr einfach: Text zu Tokens enkodieren und Anzahl zurückgeben
            return len(encoding.encode(str(text)))

        # Token-Anzahl für jede Zeile berechnen
        self.data[f"{self.feedback_col_name}_token_count"] = self.data[
            self.feedback_col_name
        ].apply(count_tokens)

        return self.data

    def sentiment_analysis(self) -> pd.DataFrame:
        """
        Perform sentiment analysis on text data using Hugging Face transformers.

        This method uses a pre-trained transformer model to analyze sentiment
        and provides both categorical labels and confidence scores. The pipeline
        is created once for efficiency across all text entries.

        Args:
            Uses self.sentiment_col_name (str): Column name containing text for sentiment analysis

        Returns:
            pd.DataFrame: Updated DataFrame with two new columns:
                - 'sentiment_label': Categorical sentiment (e.g., "positiv", "negativ", "neutral")
                - 'sentiment_score': Confidence score (float between 0.0 and 1.0)

        Note:
            - Creates sentiment pipeline once for optimal performance
            - Handles NaN values and non-string data by returning "UNKNOWN" label
            - Returns "ERROR" label for processing exceptions
            - Modifies self.data in-place by adding sentiment columns
            - Common labels include: "positiv", "negativ", "neutral" (model-dependent)
        """
        analyzer = SentimentIntensityAnalyzer()

        def analyze_row(text):
            if pd.isna(text) or not isinstance(text, str):
                return {"label": "UNKNOWN", "sentiment_score": 0.0}

            try:
                # Pipeline aufrufen und Ergebnis zurückgeben
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

        # Sentiment für jede Zeile analysieren
        sentiment_results = self.data[self.sentiment_col_name].apply(analyze_row)

        # Ergebnisse in separate Spalten aufteilen
        self.data["sentiment_label"] = sentiment_results.apply(lambda x: x["label"])
        self.data["sentiment_score"] = sentiment_results.apply(
            lambda x: x["sentiment_score"]
        )

        return self.data

    def classify_topics(self) -> pd.DataFrame:
        """
        Klassifiziert Feedback-Texte in Topics basierend auf Keyword-Matching.

        Diese Methode verwendet die topic_keywords.py Logik um jeden Feedback-Text
        einer Kategorie zuzuordnen (z.B. "Lieferproblem", "Service", "Produktqualität").

        Args:
            Uses self.topic_col_name (str): Column name containing text for topic classification

        Returns:
            pd.DataFrame: Updated DataFrame with two new columns:
                - 'topic': Topic-Kategorie (str)
                - 'topic_confidence': Confidence-Score (float zwischen 0.0 und 1.0)

        Note:
            - Verwendet Keyword-Matching für schnelle Klassifizierung
            - Fallback auf "Sonstiges" wenn kein Topic passt
            - Modifies self.data in-place by adding topic columns
        """

        def classify_row(text):
            if pd.isna(text) or not isinstance(text, str):
                return {"topic": "Sonstiges", "confidence": 0.0}

            try:
                topic, confidence = classify_feedback_topic(text)
                return {"topic": topic, "confidence": confidence}
            except Exception:
                return {"topic": "Sonstiges", "confidence": 0.0}

        # Topic für jede Zeile klassifizieren
        print("\n🔍 Klassifiziere Topics...")
        topic_results = self.data[self.topic_col_name].apply(classify_row)

        # Ergebnisse in separate Spalten aufteilen
        self.data["topic"] = topic_results.apply(lambda x: x["topic"])
        self.data["topic_confidence"] = topic_results.apply(lambda x: x["confidence"])

        # Statistiken ausgeben
        topic_counts = self.data["topic"].value_counts()
        print(f"\n📊 Topic-Verteilung:")
        for topic, count in topic_counts.items():
            percentage = (count / len(self.data)) * 100
            print(f"   • {topic}: {count:,} ({percentage:.1f}%)")

        return self.data
