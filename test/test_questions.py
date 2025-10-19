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
    def get_all_questions(cls):
        """
        Returns all test questions from all categories.

        Returns:
            list[str]: Combined list of all test questions (67 total)
            
        Notes:
            - Concatenates all category question lists
            - Useful for running complete test suite
            - Order follows category order from get_all_categories()
        """
        all_questions = []
        for category in cls.get_all_categories():
            all_questions.extend(cls.get_questions_by_category(category))
        return all_questions

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


# ============================================================================
# CRITICAL MISSING TEST SCENARIOS
# ============================================================================

class CriticalMissingTests:
    """
    Test scenarios that are currently NOT covered by standard tests.
    These are CRITICAL for comprehensive system validation.
    
    Categories:
    - CHART_GENERATION: Tests Chart Creator Agent (currently 0% tested!)
    - TEMPORAL_ANALYSIS: Time-range filtering and trend analysis
    - DEALERSHIP_SPECIFIC: Dealership-level filtering and comparison
    - TOPIC_ANALYSIS: Topic and subtopic-based queries
    """

    # 1. CHART GENERATION (CRITICAL - Chart Creator Agent never tested!)
    CHART_GENERATION_QUESTIONS = [
        "Erstelle ein Diagramm zur NPS-Verteilung",
        "Zeige mir ein Chart mit der Sentiment-Entwicklung über Zeit",
        "Visualisiere die Top 10 Probleme als Balkendiagramm",
        "Erstelle eine Grafik zur Marktverteilung",
        "Zeige die NPS-Scores der verschiedenen Märkte im Chart",
        "Vergleiche Promoter vs Detractor visuell im Diagramm",
        "Erstelle ein Tortendiagramm der Sentiment-Verteilung",
        "Zeitlicher Verlauf der Feedbacks als Liniendiagramm",
    ]

    # 2. TEMPORAL ANALYSIS (Zeit-Filterung - kaum getestet)
    TEMPORAL_ANALYSIS_QUESTIONS = [
        "Analysiere Feedbacks aus Januar 2023",
        "Wie hat sich das Sentiment zwischen 2023 und 2024 entwickelt?",
        "Zeige mir Feedbacks vom letzten Quartal 2024",
        "Vergleiche Q1 2023 mit Q1 2024",
        "Welche Probleme traten im Sommer 2023 auf?",
        "Feedbacks der letzten 6 Monate analysieren",
        "Gibt es saisonale Muster im Sentiment?",
        "Entwicklung der NPS-Scores über das Jahr 2024",
    ]

    # 3. DEALERSHIP-SPECIFIC (LIMITATION TEST - Not in structured metadata!)
    # These questions test if system correctly explains that dealer names
    # are only in verbatim text, not as structured metadata for filtering/charts
    DEALERSHIP_QUESTIONS = [
        "Wie ist die Bewertung von 'Autohaus Goldgrube'?",
        "Vergleiche Service-Station Rakete mit Werkstatt Schraubenkönig",
        "Welche Werkstatt hat die besten NPS-Scores?",
        "Zeige negative Feedbacks für Autopark Wunderland",
        "Top 5 best-performing Dealerships",
        "Welche Werkstätten haben Probleme mit Terminvergabe?",
        "Analysiere Motorwelt Sternschnuppe Kundenfeedbacks",
    ]

    # 4. TOPIC & SUBTOPIC ANALYSIS (0% tested - Hauptkategorien!)
    TOPIC_ANALYSIS_QUESTIONS = [
        "Analysiere alle Feedbacks zum Thema 'Reifenwechsel'",
        "Wie ist das Sentiment bei 'Service & Beratung'?",
        "Zeige Probleme mit 'Preis-Leistung'",
        "Feedbacks zur Kategorie 'Kommunikation' analysieren",
        "Vergleiche Topics 'Reinigung & Pflege' vs 'Fahrzeugqualität'",
        "Welches Topic hat die meisten negativen Feedbacks?",
        "Subtopic 'Verfügbarkeit von Terminen' analysieren",
        "Alle Topics mit schlechtem NPS-Score zeigen",
    ]

    # 5. OFF-TOPIC / OUT-OF-SCOPE (ECHTE Edge Cases!)
    # System sollte höflich ablehnen: "Das kann ich leider nicht beantworten..."
    OFF_TOPIC_QUESTIONS = [
        # Völlig andere Themen
        "Was ist die Hauptstadt von Frankreich?",
        "Wie wird das Wetter morgen?",
        "Erkläre mir die Quantenphysik",
        "Schreibe mir ein Gedicht über den Frühling",
        
        # Technische Off-Topic Fragen
        "Wie funktioniert ein Verbrennungsmotor?",
        "Was kostet ein neues Auto?",
        "Welche Automarken gibt es?",
        
        # Persönliche Fragen
        "Wie alt bist du?",
        "Was isst du gerne?",
        "Hast du Freunde?",
        
        # Anleitungen (nicht im Scope)
        "Wie wechsle ich einen Reifen?",
        "Anleitung für Ölwechsel",
        "Wie bediene ich mein Navigationssystem?",
        
        # Kauf-/Verkaufsanfragen
        "Ich möchte ein Auto kaufen",
        "Wo kann ich einen Service-Termin buchen?",
        "Wie kontaktiere ich eine Werkstatt?",
        
        # Business-Fragen außerhalb Scope
        "Wie viele Mitarbeiter hat das Unternehmen?",
        "Was ist der Umsatz?",
        "Wer ist der CEO?",
    ]

    @classmethod
    def get_all_critical_tests(cls):
        """Returns all critical missing test questions INCLUDING off-topic edge cases"""
        return (
            cls.CHART_GENERATION_QUESTIONS +
            cls.TEMPORAL_ANALYSIS_QUESTIONS +
            cls.DEALERSHIP_QUESTIONS +
            cls.TOPIC_ANALYSIS_QUESTIONS +
            cls.OFF_TOPIC_QUESTIONS
        )

    @classmethod
    def get_critical_categories(cls):
        """Returns list of critical test category names"""
        return [
            "CHART_GENERATION_QUESTIONS",
            "TEMPORAL_ANALYSIS_QUESTIONS",
            "DEALERSHIP_QUESTIONS",
            "TOPIC_ANALYSIS_QUESTIONS",
            "OFF_TOPIC_QUESTIONS",
        ]


# ============================================================================
# ADVANCED ANALYSIS TEST SCENARIOS
# ============================================================================

class AdvancedAnalysisTests:
    """
    Advanced analytical test scenarios for deep system validation.
    
    Categories:
    - STATISTICAL_AGGREGATION: Statistical computations and aggregations
    - MULTI_MARKET_COMPARISON: Cross-market comparative analysis
    - CHANNEL_SURVEY_ANALYSIS: Response channel and survey type filtering
    """

    # 1. STATISTICAL AGGREGATION (0% tested)
    STATISTICAL_QUESTIONS = [
        "Was ist der durchschnittliche NPS-Score pro Markt?",
        "Zeige die Standardabweichung der Sentiment-Scores",
        "Wie viele Feedbacks gibt es pro Monat?",
        "Durchschnittliche Token-Länge negativer Feedbacks?",
        "Mediane Wartezeit nach Märkten aufschlüsseln",
        "Korrelation zwischen NPS und Sentiment analysieren",
        "Prozentuale Verteilung aller Topics berechnen",
    ]

    # 2. MULTI-MARKET COMPARISON (0% tested systematisch)
    MARKET_COMPARISON_QUESTIONS = [
        "Vergleiche Deutschland, Schweiz und Frankreich",
        "Welcher europäische Markt hat die besten NPS-Werte?",
        "US vs China: Sentiment-Unterschiede analysieren",
        "Zeige Top-Probleme für alle asiatischen Märkte",
        "Vergleiche Nordamerika (US+CA) mit Europa",
        "In welchen Märkten gibt es die meisten Beschwerden?",
        "Ranking aller Märkte nach Kundenzufriedenheit",
    ]

    # 3. CHANNEL & SURVEY TYPE ANALYSIS (0% tested)
    CHANNEL_SURVEY_QUESTIONS = [
        "Wie unterscheidet sich das Feedback zwischen Online und Phone?",
        "Analysiere nur App-Feedbacks",
        "Vergleiche Email vs In-Person Feedbacks",
        "Welcher Kanal hat die höchste Zufriedenheit?",
        "Zeige Complaint-Feedbacks aus allen Kanälen",
        "Annual Survey vs Transaction Survey Unterschiede?",
        "Post-Service Feedbacks analysieren",
    ]

    @classmethod
    def get_all_advanced_tests(cls):
        """Returns all advanced analysis test questions"""
        return (
            cls.STATISTICAL_QUESTIONS +
            cls.MARKET_COMPARISON_QUESTIONS +
            cls.CHANNEL_SURVEY_QUESTIONS
        )

    @classmethod
    def get_advanced_categories(cls):
        """Returns list of advanced test category names"""
        return [
            "STATISTICAL_QUESTIONS",
            "MARKET_COMPARISON_QUESTIONS",
            "CHANNEL_SURVEY_QUESTIONS",
        ]


# ============================================================================
# EXPLORATORY TEST SCENARIOS
# ============================================================================

class ExploratoryTests:
    """
    Exploratory test scenarios for niche features and metadata fields.
    
    Categories:
    - TEXT_LENGTH_ANALYSIS: Token/character length based filtering
    - PERSONA_DEMOGRAPHICS: Persona and demographic-based analysis
    - DEVICE_BROWSER_ANALYSIS: Technical metadata analysis
    """

    # 1. TEXT LENGTH ANALYSIS (20% tested - nur 1 test)
    TEXT_LENGTH_QUESTIONS = [
        "Zeige sehr kurze Feedbacks unter 50 Tokens",
        "Analysiere ausführliche Feedbacks über 200 Tokens",
        "Vergleiche kurze vs lange Feedbacks: Sentiment-Unterschiede?",
        "Durchschnittliche Länge bei Promoter vs Detractor",
        "Sind längere Feedbacks positiver oder negativer?",
        "Feedbacks zwischen 100 und 150 Tokens analysieren",
    ]

    # 2. PERSONA & DEMOGRAPHICS (0% tested - synthetic data!)
    PERSONA_DEMOGRAPHICS_QUESTIONS = [
        "Wie bewerten 'tech_enthusiast' Personas das System?",
        "Vergleiche Sentiment nach Altersgruppen",
        "Sind jüngere Kunden (18-35) zufriedener?",
        "Feedback von 'busy_professional' vs 'family_oriented'",
        "Welche tech_affinity Gruppe ist am kritischsten?",
        "Experienced_senior Feedbacks analysieren",
    ]

    # 3. DEVICE & BROWSER ANALYSIS (0% tested - interessant!)
    DEVICE_BROWSER_QUESTIONS = [
        "Desktop vs Mobile User: Sentiment-Unterschiede?",
        "Gibt es Unterschiede zwischen Chrome und Firefox Nutzern?",
        "Analysiere Feedbacks von Tablet-Nutzern",
        "Welches Device hat die negativsten Feedbacks?",
        "Browser-spezifische Probleme identifizieren",
    ]

    @classmethod
    def get_all_exploratory_tests(cls):
        """Returns all exploratory test questions"""
        return (
            cls.TEXT_LENGTH_QUESTIONS +
            cls.PERSONA_DEMOGRAPHICS_QUESTIONS +
            cls.DEVICE_BROWSER_QUESTIONS
        )

    @classmethod
    def get_exploratory_categories(cls):
        """Returns list of exploratory test category names"""
        return [
            "TEXT_LENGTH_QUESTIONS",
            "PERSONA_DEMOGRAPHICS_QUESTIONS",
            "DEVICE_BROWSER_QUESTIONS",
        ]


# ============================================================================
# COMPREHENSIVE TEST SUITE
# ============================================================================

class ComprehensiveTestSuite:
    """
    Provides access to all test categories for comprehensive testing.
    
    Combines:
    - Standard tests (TestQuestions) - 67 tests
    - Critical missing tests (CriticalMissingTests) - 31 tests  
    - Advanced analysis tests (AdvancedAnalysisTests) - 21 tests
    - Exploratory tests (ExploratoryTests) - 17 tests
    - Real edge cases (RealEdgeCaseTests) - 64 tests
    - Stress & adversarial tests (StressTestQuestions) - ~100 tests
    
    Total: ~300 tests for complete coverage
    """

    @classmethod
    def get_all_tests(cls):
        """Returns ALL test questions from all categories"""
        return (
            TestQuestions.get_all_questions() +
            CriticalMissingTests.get_all_critical_tests() +
            AdvancedAnalysisTests.get_all_advanced_tests() +
            ExploratoryTests.get_all_exploratory_tests() +
            RealEdgeCaseTests.get_all_edge_cases() +
            StressTestQuestions.get_all_stress_tests()
        )

    @classmethod
    def get_all_categories(cls):
        """Returns all category names across all test classes"""
        return (
            TestQuestions.get_all_categories() +
            CriticalMissingTests.get_critical_categories() +
            AdvancedAnalysisTests.get_advanced_categories() +
            ExploratoryTests.get_exploratory_categories() +
            RealEdgeCaseTests.get_edge_case_categories() +
            StressTestQuestions.get_stress_categories()
        )

    @classmethod
    def get_priority_tests(cls, priority: str = "critical"):
        """
        Returns tests by priority level.
        
        Args:
            priority: "critical", "advanced", "exploratory", "edge", "stress", or "standard"
            
        Returns:
            list[str]: Questions for specified priority level
        """
        if priority.lower() == "critical":
            return CriticalMissingTests.get_all_critical_tests()
        elif priority.lower() == "advanced":
            return AdvancedAnalysisTests.get_all_advanced_tests()
        elif priority.lower() == "exploratory":
            return ExploratoryTests.get_all_exploratory_tests()
        elif priority.lower() == "edge":
            return RealEdgeCaseTests.get_all_edge_cases()
        elif priority.lower() == "stress":
            return StressTestQuestions.get_all_stress_tests()
        elif priority.lower() == "standard":
            return TestQuestions.get_all_questions()
        else:
            return cls.get_all_tests()

    @classmethod
    def get_test_statistics(cls):
        """Returns statistics about test coverage"""
        return {
            "standard_tests": len(TestQuestions.get_all_questions()),
            "critical_tests": len(CriticalMissingTests.get_all_critical_tests()),
            "advanced_tests": len(AdvancedAnalysisTests.get_all_advanced_tests()),
            "exploratory_tests": len(ExploratoryTests.get_all_exploratory_tests()),
            "edge_case_tests": len(RealEdgeCaseTests.get_all_edge_cases()),
            "stress_tests": len(StressTestQuestions.get_all_stress_tests()),
            "total_tests": len(cls.get_all_tests()),
            "total_categories": len(cls.get_all_categories()),
        }


# ============================================================================
# REAL EDGE CASE TEST SCENARIOS
# ============================================================================

class RealEdgeCaseTests:
    """
    ECHTE Edge Cases - Grenzfälle die das System BEANTWORTEN soll.
    
    Im Gegensatz zu OFF_TOPIC_QUESTIONS (die abgelehnt werden sollen)
    sind dies gültige Fragen an Systemgrenzen, die das System korrekt
    handhaben muss.
    
    Categories:
    - BOUNDARY_CASES: Numerische und zeitliche Grenzwerte
    - AMBIGUOUS_CASES: Mehrdeutige Formulierungen
    - CONFLICTING_CASES: Widersprüchliche oder unmögliche Filterkombinationen
    - DATA_EDGE_CASES: Sehr wenige oder sehr viele Treffer
    - LINGUISTIC_CASES: Tippfehler und umgangssprachliche Formulierungen
    - SPECIAL_CHAR_CASES: Sonderzeichen und Case-Sensitivity Tests
    """

    # 1. BOUNDARY CASES - Numerische und zeitliche Grenzwerte
    BOUNDARY_CASES = [
        "Zeige mir genau 1 Feedback",                           # Minimalwert n=1
        "Top 0 Probleme",                                        # Zero-Edge-Case
        "Feedbacks mit NPS Score 0",                            # Minimaler gültiger NPS
        "Feedbacks mit NPS Score 10",                           # Maximaler gültiger NPS
        "Erste Feedback im Datensatz",                          # Zeitliche Untergrenze
        "Neueste Feedback analysieren",                         # Zeitliche Obergrenze
        "Feedbacks vom ersten Tag (15.01.2024)",               # Start-Datum
        "Feedbacks vom letzten verfügbaren Tag",               # End-Datum
        "Kürzeste Feedbacks zeigen",                           # Minimum Token-Länge
        "Längste Feedbacks analysieren",                       # Maximum Token-Länge
        "Feedbacks mit genau 50 Tokens",                       # Spezifische Länge
        "NPS Score genau 5",                                   # Mittlerer Grenzwert
    ]

    # 2. AMBIGUOUS CASES - Mehrdeutigkeiten und unklare Formulierungen
    AMBIGUOUS_CASES = [
        "Wie ist die Situation?",                              # Keine Spezifikation
        "Zeige mir das Problem",                               # Singular statt Plural
        "Analysiere die Daten",                                # Keine Filter/Richtung
        "Gute Feedbacks analysieren",                          # "Gut" = Promoter? Positiv?
        "Schlechte Bewertungen zeigen",                        # "Schlecht" = Detractor? Negativ?
        "Mittelmäßige Feedbacks",                              # Passive? Neutral? Beides?
        "Wichtige Probleme identifizieren",                    # Was ist "wichtig"?
        "Feedbacks zu Autos",                                  # Zu generisch (alle?)
        "Kundenservice bewerten",                              # Service-Topic?
        "Zufriedenheit messen",                                # NPS? Sentiment? Beides?
    ]

    # 3. CONFLICTING CASES - Widersprüchliche Filterkombinationen
    CONFLICTING_CASES = [
        "Positive Feedbacks von Detractors",                   # Widerspruch: Detractor meist negativ
        "Negative Promoter-Feedbacks",                         # Widerspruch: Promoter meist positiv
        "Neutrale Feedbacks mit NPS 0",                        # NPS 0 = Detractor, nicht neutral
        "Positive Beschwerden analysieren",                    # Beschwerden sind per Definition negativ
        "Lobende Feedbacks mit NPS unter 3",                   # Lob + schlechter NPS = Widerspruch
        "Sehr zufriedene Detractors",                          # Detractor = unzufrieden
        "Unzufriedene Promoter zeigen",                        # Promoter = zufrieden
        "Feedbacks von 2025 bis 2024",                         # Zeitrückwärts (from > to)
        "NPS Score über 10",                                   # Außerhalb gültigem Bereich
        "Sentiment positiv und negativ gleichzeitig",          # Logischer Widerspruch
    ]

    # 4. DATA EDGE CASES - Daten-Grenzfälle (sehr wenig/viele Treffer)
    DATA_EDGE_CASES = [
        "Feedbacks mit Topic 'Raumfahrt'",                     # Topic existiert nicht
        "NPS 10 Feedbacks mit negativem Sentiment",            # Kombination existiert nicht
        "Promoter aus dem Jahr 2020",                          # Zeitbereich außerhalb
        "Alle Feedbacks analysieren",                          # Alle 10.000 Einträge
        "Zeige alle positiven Feedbacks",                      # ~4.700 Einträge
        "Jedes Feedback mit Text zeigen",                      # Alle Einträge haben Text
        "Feedbacks von 'Autohaus Goldgrube' mit NPS 0 aus Januar 2024",  # Sehr spezifisch
        "Detractor über Reifenwechsel in China vom 15.01.2024",  # 4-Filter sehr spezifisch
        "Feedbacks ohne Text",                                 # Sollte 0 sein (alle haben Text)
        "Markt 'Antarktis' analysieren",                       # Nicht existierender Markt
    ]

    # 5. LINGUISTIC CASES - Tippfehler und umgangssprachliche Formulierungen
    LINGUISTIC_CASES = [
        "Zege mir die Top Problehme",                          # Multiple Tippfehler
        "Analusiere das Sentimant",                            # Tippfehler erkennbar
        "Wie ist de NPS Skore?",                               # Fehler aber verständlich
        "Was läuft schief bei uns?",                           # Umgangssprache
        "Warum meckern die Kunden so viel?",                   # Informell
        "Wo hakt's denn?",                                     # Dialekt/Umgangssprache
        "Zeig mal die miesesten Feedbacks",                    # Slang
        "Top Probleme bitte",                                  # Sehr informell
        "Gibt's Beschwerden über Service?",                    # Verkürzung "gibt es"
        "Was nervt die Leute?",                                # Umgangssprachlich
    ]

    # 6. SPECIAL CHARACTER & FORMATTING CASES - Sonderzeichen und Formatierung
    SPECIAL_CHAR_CASES = [
        "SERVICE",                                             # All Caps
        "service",                                             # All lowercase  
        "SeRvIcE",                                             # Mixed Case
        "Service/Beratung",                                    # Slash statt & (Topic existiert als "Service & Beratung")
        "Preis - Leistung",                                    # Spaces um Bindestrich
        "'Autohaus Goldgrube'",                                # Anführungszeichen
        "\"Autohaus Goldgrube\"",                              # Doppelte Anführungszeichen
        "Service&Beratung",                                    # Kein Space um &
        "Top!!!",                                              # Multiple Sonderzeichen
        "Service ???",                                         # Fragezeichen im Query
        "NPS > 8",                                             # Vergleichsoperator
        "Sentiment = positiv",                                 # Gleichheitszeichen
    ]

    @classmethod
    def get_all_edge_cases(cls):
        """Returns all edge case test questions"""
        return (
            cls.BOUNDARY_CASES +
            cls.AMBIGUOUS_CASES +
            cls.CONFLICTING_CASES +
            cls.DATA_EDGE_CASES +
            cls.LINGUISTIC_CASES +
            cls.SPECIAL_CHAR_CASES
        )

    @classmethod
    def get_edge_case_categories(cls):
        """Returns list of edge case category names"""
        return [
            "BOUNDARY_CASES",
            "AMBIGUOUS_CASES",
            "CONFLICTING_CASES",
            "DATA_EDGE_CASES",
            "LINGUISTIC_CASES",
            "SPECIAL_CHAR_CASES",
        ]

    @classmethod
    def get_critical_edge_cases(cls):
        """Returns only critical edge cases (boundary + conflicting)"""
        return cls.BOUNDARY_CASES + cls.CONFLICTING_CASES

    @classmethod
    def get_linguistic_edge_cases(cls):
        """Returns only linguistic edge cases (typos + colloquial)"""
        return cls.LINGUISTIC_CASES + cls.SPECIAL_CHAR_CASES


# ============================================================================
# STRESS & ADVERSARIAL TEST SCENARIOS
# ============================================================================

class StressTestQuestions:
    """
    Stress tests with realistic user errors and extreme edge cases.
    These tests CHALLENGE the system with typos, ambiguity, impossible data,
    and adversarial inputs to validate robustness beyond "happy path"!
    
    Categories:
    - ADVERSARIAL_QUERIES: Typos, misspellings, umgangssprache, code-switching
    - AMBIGUOUS_STRESS: Very unclear, vague, multi-interpretable questions
    - IMPOSSIBLE_QUERIES: Non-existent data, contradictions, over-limits
    - NUMERICAL_STRESS: Extreme numbers, decimals, ranges
    - AGGREGATION_VALIDATION: Exact numerical validation required
    - CHART_STRESS: Chart generation extreme edge cases
    - TEMPORAL_AMBIGUITY: Relative time expressions
    - SPECIAL_CHARACTERS: Emojis, encoding, whitespace
    - EMPTY_MINIMAL: Empty or minimal queries
    """

    # 1. ADVERSARIAL QUERIES (Typos, Umgangssprache, Code-Switching)
    ADVERSARIAL_QUERIES = [
        # Rechtschreibfehler
        "Analusiere Fedbacks aus Detuschland",
        "Zeige negateive Stimmug",
        "NPS-Ferteilung anzeign",
        "Top 5 Probläme",
        
        # Umgangssprache / Slang
        "Wo hakt's bei den Kunden?",
        "Was nervt die Leute am meisten?",
        "Zeig mal die miesesten Feedbacks",
        "Wie läuft's in Deutschland?",
        "Gibt's krasse Beschwerden?",
        
        # Gemischte Sprachen (Code-Switching)
        "Zeige die top complaints aus Deutschland",
        "Was sind die main issues im US-Market?",
        "Performance vom deutschen Markt analysen",
        
        # Tippfehler + Abkürzungen
        "Zeig mir schlechte Rückmeldungen aus DE",
        "Analyse FR Markt pls",
        "NPS Score avg für CH?",
    ]

    # 2. AMBIGUOUS STRESS (Sehr mehrdeutig, unklar, vage)
    AMBIGUOUS_STRESS = [
        # Mehrdeutig: NPS gut oder Sentiment positiv?
        "Zeige mir gute Feedbacks",
        
        # Unklar: Welche Metrik?
        "Wie schneiden wir ab?",
        "Läuft es gut?",
        
        # Vage Zeit-Angaben
        "Analysiere kürzlich eingegangene Beschwerden",
        "Neueste Probleme zeigen",
        
        # Unvollständig
        "Top 10",
        "Analyse",
        "Vergleichen",
        
        # Widersprüchlich
        "Zeige positive Feedbacks von unzufriedenen Kunden",
        "Promoter mit negativem Sentiment",
        
        # Zu allgemein
        "Was läuft schlecht?",
        "Gibt es Probleme?",
        "Mach eine Analyse",
    ]

    # 3. IMPOSSIBLE QUERIES (Non-existente Daten, Widersprüche)
    IMPOSSIBLE_QUERIES = [
        # Non-existente Märkte
        "Analysiere Feedbacks aus Brasilien",
        "Wie ist die Stimmung in Australien?",
        "Mexiko-Markt Performance",
        "Feedbacks aus Spanien zeigen",
        "Österreich Analyse",
        
        # Non-existente Dealerships
        "Bewertung von Tesla Service Center",
        "AutoHaus Berlin Mitte analysieren",
        "Mercedes-Benz Zentrum München",
        
        # Unmögliche Kombinationen
        "Promoter mit NPS Score 0",
        "Negative Feedbacks mit NPS 10",
        "Detractors mit positivem Sentiment",
        
        # Zukunft/Vergangenheit außerhalb Range
        "Feedbacks aus dem Jahr 2030",
        "Daten von vor 100 Jahren",
        
        # Über Limits
        "Zeige mir 100000 Feedbacks",
        "Alle 999999 Beschwerden",
        
        # Non-existente Topics
        "Analyse zum Thema Autopilot",
        "Feedbacks zu Ladeinfrastruktur",
        "Probleme mit Elektroantrieb",
    ]

    # 4. NUMERICAL STRESS (Extreme Zahlen, Edge Cases)
    NUMERICAL_STRESS = [
        # Extreme Zahlen
        "Zeige mir die Top 999999 Probleme",
        "Top 0 Feedbacks",
        "Top -999 Probleme",
        
        # Dezimalzahlen
        "Top 3.5 Feedbacks",
        "Erste 10.2 Probleme",
        
        # Unklare Formate
        "Zeige erste 10-20 Feedbacks",
        "Top zehn Probleme",
        "Circa 15 Feedbacks",
        
        # Prozent (nicht implementiert!)
        "Zeige mir die Top 10% der Feedbacks",
        "Obere 25% nach Sentiment-Score",
        
        # Null/Leer
        "Zeige Feedbacks",
    ]

    # 5. AGGREGATION VALIDATION (Erfordert exakte Zahlen-Checks!)
    AGGREGATION_VALIDATION = [
        # Exakte Zählungen
        "Wie viele Feedbacks gibt es GENAU aus Deutschland?",
        "Exakte Anzahl Promoter im Datensatz?",
        "Was ist der EXAKTE durchschnittliche NPS-Score?",
        "Wie viele verschiedene Dealerships gibt es?",
        "Anzahl Feedbacks pro Markt auflisten",
        
        # Prozentuale Verteilungen
        "Zeige die prozentuale Verteilung aller Topics",
        "NPS-Kategorien in Prozent",
        
        # Cross-Checks
        "Ist Promoter + Passive + Detractor = Gesamtzahl?",
        "Stimmt die Sentiment-Verteilung mit NPS überein?",
    ]

    # 6. CHART STRESS (Chart Generation Edge Cases)
    CHART_STRESS = [
        # Chart mit zu vielen Datenpunkten
        "Erstelle Diagramm mit allen 10000 Feedbacks",
        
        # Unmögliche Chart-Typen
        "Erstelle ein 3D-Hologramm der NPS-Verteilung",
        "Zeige interaktive VR-Visualisierung",
        
        # Ungeeignete Daten
        "Liniendiagramm der Dealership-Namen",
        "Tortendiagramm mit 100 Slices",
        
        # Chart ohne Daten
        "Zeige Trend für Österreich",
        "Chart für nicht-existenten Markt",
        
        # Vage Chart-Requests
        "Mach ein Diagramm",
        "Visualisiere alles",
    ]

    # 7. TEMPORAL AMBIGUITY (Relative Zeit, unklar)
    TEMPORAL_AMBIGUITY = [
        # Relative Zeit
        "Feedbacks von gestern",
        "Letzte Woche",
        "Vor 3 Monaten",
        "Dieses Quartal",
        
        # Unklare Perioden
        "Neueste Feedbacks",
        "Aktuelle Daten",
        "Historische Trends",
        "Älteste Beschwerden",
        
        # Fehlende Jahresangabe
        "Feedbacks aus März",
        "Q2 Performance",
        "Sommerzeit Analyse",
    ]

    # 8. SPECIAL CHARACTERS & ENCODING
    SPECIAL_CHARACTERS = [
        # Emojis
        "Analysiere 🔥 Feedbacks",
        "Top 5 💯 Probleme",
        "Sentiment 😊😐😢 Verteilung",
        
        # Sonderzeichen
        "Feedbacks mit & und | oder",
        "Analyse für Markt C1-DE/CH/FR",
        "Zeige <wichtige> Feedbacks",
        
        # Whitespace
        "   Feedbacks   aus   Deutschland   ",
        "Analyse mit\\nZeilenumbruch",
    ]

    # 9. EMPTY & MINIMAL QUERIES
    EMPTY_MINIMAL = [
        "?",
        "...",
        "Ja",
        "Nein",
        "Ok",
        "Hallo",
        "Danke",
    ]

    @classmethod
    def get_all_stress_tests(cls):
        """Returns all stress test questions"""
        return (
            cls.ADVERSARIAL_QUERIES +
            cls.AMBIGUOUS_STRESS +
            cls.IMPOSSIBLE_QUERIES +
            cls.NUMERICAL_STRESS +
            cls.AGGREGATION_VALIDATION +
            cls.CHART_STRESS +
            cls.TEMPORAL_AMBIGUITY +
            cls.SPECIAL_CHARACTERS +
            cls.EMPTY_MINIMAL
        )

    @classmethod
    def get_stress_categories(cls):
        """Returns list of stress test category names"""
        return [
            "ADVERSARIAL_QUERIES",
            "AMBIGUOUS_STRESS",
            "IMPOSSIBLE_QUERIES",
            "NUMERICAL_STRESS",
            "AGGREGATION_VALIDATION",
            "CHART_STRESS",
            "TEMPORAL_AMBIGUITY",
            "SPECIAL_CHARACTERS",
            "EMPTY_MINIMAL",
        ]

    @classmethod
    def get_critical_stress_tests(cls):
        """Returns only critical stress tests (typos + impossible + numerical)"""
        return (
            cls.ADVERSARIAL_QUERIES +
            cls.IMPOSSIBLE_QUERIES +
            cls.NUMERICAL_STRESS
        )
