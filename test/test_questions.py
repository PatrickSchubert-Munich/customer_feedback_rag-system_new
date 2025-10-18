class TestQuestions:
    """
    Structured test questions for the multi-agent system.
    
    This class organizes test questions into categories based on:
    - Expected agent/tool usage
    - Query complexity
    - Parameter extraction requirements
    - Edge cases and error handling
    
    Attributes:
        META_QUESTIONS (list[str]): Questions about system metadata and capabilities
        MARKET_VALIDATION_QUESTIONS (list[str]): Market-specific queries for validation
        FEEDBACK_ANALYSIS_QUESTIONS (list[str]): Customer feedback content analysis queries
        SENTIMENT_QUESTIONS (list[str]): Sentiment-focused analysis queries
        USER_PARAMETER_QUESTIONS (list[str]): Queries with explicit numerical parameters
        COMPLEX_QUESTIONS (list[str]): Multi-criteria complex queries
        EDGE_CASES (list[str]): Edge cases and error handling scenarios
    """

    # 1. META QUESTIONS (should use metadata_tool)
    META_QUESTIONS = [
        "Zu welchen Märkten kannst du Analysen erstellen?",
        "Wie ist die NPS-Verteilung in deinem Datensatz?",
        "Welche Sentiment-Labels verwendest du?",
        "Welchen Zeitraum decken deine Daten ab?",
        "Wie viele Feedbacks hast du insgesamt?",
        "Was ist der durchschnittliche NPS-Score?",
        "Welche Datenfelder sind verfügbar?",
        "Wie lang sind die Feedbacks durchschnittlich?",
        "Was für Analysen kannst du durchführen?",
        "Wie ist die Promoter-Detractor Verteilung?",
    ]

    # 2. MARKET VALIDATION (should use metadata_tool for error checking)
    MARKET_VALIDATION_QUESTIONS = [
        "Kannst du mir eine Auswertung zum Markt Schweiz geben?",
        "Analysiere den Markt Österreich",
        "Zeige mir Daten für den US-Markt",
        "Gibt es Feedbacks aus Frankreich?",
        "Wie ist die Stimmung in Italien?",
        "Probleme im skandinavischen Markt analysieren",
    ]

    # 3. FEEDBACK ANALYSIS (should use search_customer_feedback)
    FEEDBACK_ANALYSIS_QUESTIONS = [
        "Über welche Probleme beschweren sich die Kunden am häufigsten?",
        "Zeige mir negative Feedbacks aus Deutschland",
        "Was sind die Top 5 Beschwerden?",
        "Analysiere die häufigsten Kundenprobleme",
        "Welche Themen beschäftigen unzufriedene Kunden?",
        "Zeige mir detaillierte Probleme mit dem Service",
        "Die 10 wichtigsten Verbesserungsvorschläge",
        "Kritische Kundenfeedbacks analysieren",
        "Finde positive Kundenfeedbacks und analysiere sie",
        "Was loben Kunden am meisten in ihren Feedbacks?",
    ]

    # 4. SENTIMENT ANALYSIS (should use sentiment_analysis_agent)
    SENTIMENT_QUESTIONS = [
        "Wie ist die Stimmung der Kunden generell?",
        "Analysiere das Sentiment der Promoter",
        "Wie fühlen sich die Detractors?",
        "Sentiment-Entwicklung über Zeit",
        "Positive vs negative Stimmung vergleichen",
        "Emotionale Reaktionen der Kunden analysieren",
    ]

    # 5. USER PARAMETER TESTS (should extract numerical parameters)
    USER_PARAMETER_QUESTIONS = [
        "Zeige mir die Top 3 Probleme",
        "Die 15 häufigsten Beschwerden",
        "Nur 5 negative Feedbacks anzeigen",
        "Maximal 8 Kundenprobleme",
        "Erste 20 Feedbacks analysieren",
        "Top 12 kritische Punkte",
    ]

    # 6. COMPLEX QUERIES (multi-criteria filtering)
    COMPLEX_QUESTIONS = [
        "Zeige mir die Top 10 Probleme von Detractors",
        "Negative Feedbacks mit mehr als 100 Tokens",
        "Promoter mit neutralem Sentiment analysieren",
        "Häufigste Probleme bei NPS Score unter 5",
        "Detaillierte Analyse von Beschwerden über Service",
        "Sentiment-Verteilung bei verschiedenen NPS-Kategorien",
    ]

    # 7. EDGE CASES & ERROR HANDLING
    EDGE_CASES = [
        "Analysiere Daten für das Jahr 2025",
        "Zeige mir 1000 Feedbacks",  # Über Limit
        "Feedbacks mit NPS Score 15",  # Ungültiger NPS
        "Sentiment für nicht-existenten Markt",
        "Top -5 Probleme",  # Ungültige Zahl
        "Analysiere Daten aus der Zukunft",
    ]

    @classmethod
    def get_all_categories(cls):
        """
        Returns all category names available in the test suite.

        Returns:
            list[str]: List of category attribute names:
                - META_QUESTIONS
                - MARKET_VALIDATION_QUESTIONS
                - FEEDBACK_ANALYSIS_QUESTIONS
                - SENTIMENT_QUESTIONS
                - USER_PARAMETER_QUESTIONS
                - COMPLEX_QUESTIONS
                - EDGE_CASES
                
        Notes:
            - Categories are ordered by typical query complexity
            - Can be used for systematic testing across all categories
        """
        return [
            "META_QUESTIONS",
            "MARKET_VALIDATION_QUESTIONS",
            "FEEDBACK_ANALYSIS_QUESTIONS",
            "SENTIMENT_QUESTIONS",
            "USER_PARAMETER_QUESTIONS",
            "COMPLEX_QUESTIONS",
            "EDGE_CASES",
        ]

    @classmethod
    def get_questions_by_category(cls, category_name):
        """
        Returns questions from a specific category.

        Args:
            category_name (str): Name of the category (e.g., "META_QUESTIONS")

        Returns:
            list[str]: List of test questions in that category,
                      or empty list if category doesn't exist
                      
        Notes:
            - Uses getattr() for safe attribute access
            - Returns empty list for invalid category names
            - Case-sensitive category matching
        """
        return getattr(cls, category_name, [])

    @classmethod
    def get_sample_questions(cls, num_per_category=2):
        """
        Returns a sample of questions from each category.

        Args:
            num_per_category (int): Number of questions to sample from each category.
                                   Defaults to 2

        Returns:
            list[str]: Flattened list of sampled questions from all categories
            
        Notes:
            - Takes first N questions from each category
            - Useful for quick validation testing
            - Default sample size: 2 questions × 7 categories = 14 questions
            - Order matches category order in get_all_categories()
        """
        sample = []
        for category in cls.get_all_categories():
            questions = cls.get_questions_by_category(category)
            sample.extend(questions[:num_per_category])
        return sample

    @classmethod
    def get_metadata_focused_questions(cls):
        """
        Returns all questions that should primarily use metadata_tool.

        Returns:
            list[str]: Combined list of META_QUESTIONS and MARKET_VALIDATION_QUESTIONS
            
        Notes:
            - These questions focus on dataset statistics and market availability
            - Should NOT require vector search (search_customer_feedback)
            - Tests metadata retrieval and validation capabilities
            - Total: ~16 questions (10 meta + 6 market validation)
        """
        return cls.META_QUESTIONS + cls.MARKET_VALIDATION_QUESTIONS
