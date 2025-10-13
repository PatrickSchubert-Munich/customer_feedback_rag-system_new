"""
Comprehensive Test Questions for Multi-Agent Customer Feedback System

Kategorisiert nach erwarteter Tool-Nutzung und Komplexität
"""


class TestQuestions:
    """Strukturierte Test-Fragen für das Multi-Agent System"""

    # 1. META-FRAGEN (sollten metadata_tool nutzen)
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

    # 2. MARKT-VALIDIERUNG (sollten metadata_tool für Fehlerprüfung nutzen)
    MARKET_VALIDATION_QUESTIONS = [
        "Kannst du mir eine Auswertung zum Markt Schweiz geben?",
        "Analysiere den Markt Österreich",
        "Zeige mir Daten für den US-Markt",
        "Gibt es Feedbacks aus Frankreich?",
        "Wie ist die Stimmung in Italien?",
        "Probleme im skandinavischen Markt analysieren",
    ]

    # 3. FEEDBACK-ANALYSEN (sollten search_customer_feedback nutzen)
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

    # 4. SENTIMENT-ANALYSEN (sollten sentiment_analysis_agent nutzen)
    SENTIMENT_QUESTIONS = [
        "Wie ist die Stimmung der Kunden generell?",
        "Analysiere das Sentiment der Promoter",
        "Wie fühlen sich die Detractors?",
        "Sentiment-Entwicklung über Zeit",
        "Positive vs negative Stimmung vergleichen",
        "Emotionale Reaktionen der Kunden analysieren",
    ]

    # 5. USER-PARAMETER TESTS (sollten Parameter extrahieren)
    USER_PARAMETER_QUESTIONS = [
        "Zeige mir die Top 3 Probleme",
        "Die 15 häufigsten Beschwerden",
        "Nur 5 negative Feedbacks anzeigen",
        "Maximal 8 Kundenprobleme",
        "Erste 20 Feedbacks analysieren",
        "Top 12 kritische Punkte",
    ]

    # 6. KOMPLEXE QUERIES (Multi-Kriterien)
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
        """Gibt alle Kategorie-Namen zurück"""
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
        """Gibt Fragen einer bestimmten Kategorie zurück"""
        return getattr(cls, category_name, [])

    @classmethod
    def get_sample_questions(cls, num_per_category=2):
        """Gibt eine Stichprobe aus jeder Kategorie zurück"""
        sample = []
        for category in cls.get_all_categories():
            questions = cls.get_questions_by_category(category)
            sample.extend(questions[:num_per_category])
        return sample

    @classmethod
    def get_metadata_focused_questions(cls):
        """Gibt alle Fragen zurück, die metadata_tool nutzen sollten"""
        return cls.META_QUESTIONS + cls.MARKET_VALIDATION_QUESTIONS
