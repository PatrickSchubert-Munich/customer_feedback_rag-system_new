from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class SentimentType(str, Enum):
    """Sentiment-Kategorien"""

    POSITIVE = "positiv"
    NEGATIVE = "negativ"
    NEUTRAL = "neutral"


class IssueCategory(str, Enum):
    """Kategorien für Kundenprobleme"""

    DELIVERY = "lieferung"
    PRODUCT_QUALITY = "produktqualität"
    CUSTOMER_SERVICE = "kundenservice"
    PRICING = "preise"
    TECHNICAL = "technisch"
    OTHER = "sonstiges"


class QueryType(str, Enum):
    """Typen von Benutzeranfragen"""

    FEEDBACK_ANALYSIS = "feedback_analysis"
    TREND_ANALYSIS = "trend_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    GENERAL_INQUIRY = "general_inquiry"


class ChartType(str, Enum):
    """Verfügbare Chart-Typen"""
    
    SENTIMENT_BAR_CHART = "sentiment_bar_chart"  # Bar Chart für Sentiment
    SENTIMENT_PIE_CHART = "sentiment_pie_chart"  # Pie Chart für Sentiment
    NPS_BAR_CHART = "nps_bar_chart"  # Bar Chart für NPS
    NPS_PIE_CHART = "nps_pie_chart"  # Pie Chart für NPS
    MARKET_BAR_CHART = "market_bar_chart"  # Bar Chart für Market-Volumen
    MARKET_PIE_CHART = "market_pie_chart"  # Pie Chart für Market-Anteile
    MARKET_SENTIMENT_BREAKDOWN = "market_sentiment_breakdown"  # Sentiment pro Markt
    MARKET_NPS_BREAKDOWN = "market_nps_breakdown"  # NPS pro Markt
    TIME_ANALYSIS = "time_analysis"
    OVERVIEW = "overview"


class QueryIntent(BaseModel):
    """Analysierte Benutzerabsicht"""

    query_type: QueryType = Field(description="Typ der Anfrage")
    enhanced_query: str = Field(description="Verbesserte und präzisierte Anfrage")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extrahierte Parameter (NPS-Filter, Zeiträume, etc.)",
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Konfidenz der Intent-Erkennung"
    )
    reasoning: str = Field(description="Begründung für die Intent-Klassifikation")


class CustomerFeedback(BaseModel):
    """Ein einzelnes Kundenfeedback-Element mit vorhandenen Metadaten"""

    verbatim: str = Field(description="Der Inhalt des Feedbacks")

    # Analysierte Eigenschaften
    keywords: Optional[List[str]] = Field(
        default=None, description="Wichtige Schlüsselwörter aus dem Feedback"
    )
    category: Optional[IssueCategory] = Field(
        default=None, description="Kategorie des Problems"
    )
    severity: Optional[int] = Field(
        default=None, ge=1, le=5, description="Schweregrad des Problems (1-5)"
    )

    # Metadaten aus ChromaDB (angepasst an tatsächliche Datenstruktur)
    nps: Optional[int] = Field(default=None, description="NPS Score")
    nps_category: Optional[str] = Field(
        default=None, description="NPS Kategorie (Promoter/Passive/Detractor)"
    )
    market: Optional[str] = Field(default=None, description="Markt/Region")
    sentiment_label: Optional[str] = Field(
        default=None, description="Sentiment Label aus der Datenaufbereitung"
    )
    verbatim_token_count: Optional[int] = Field(
        default=None, description="Token-Anzahl des Feedbacks"
    )
    chunk_index: Optional[int] = Field(
        default=None, description="Chunk-Information bei mehrteiligen Feedbacks"
    )


class FeedbackAnalysisResult(BaseModel):
    """Container für mehrere Kundenfeedback-Elemente"""

    feedbacks: List[CustomerFeedback] = Field(
        description="Liste der gefundenen Feedbacks"
    )
    summary: str = Field(description="Zusammenfassung der häufigsten Probleme")
    total_count: int = Field(description="Anzahl der analysierten Feedbacks")


class KeyInsight(BaseModel):
    """Ein wichtiger Erkenntnisgewinn aus der Analyse"""

    title: str = Field(description="Titel der Erkenntnis")
    description: str = Field(description="Detaillierte Beschreibung")
    impact: str = Field(description="Auswirkung/Bedeutung für das Business")
    priority: str = Field(description="Priorität: Hoch/Mittel/Niedrig")


class ActionableRecommendation(BaseModel):
    """Konkrete Handlungsempfehlung"""

    action: str = Field(description="Konkrete Handlung")
    department: str = Field(description="Zuständige Abteilung")
    timeline: str = Field(description="Empfohlener Zeitrahmen")
    expected_impact: str = Field(description="Erwartete positive Auswirkung")


class SummaryStatistics(BaseModel):
    """Zusammenfassende Statistiken"""

    total_feedbacks: int = Field(description="Gesamtanzahl analysierter Feedbacks")
    avg_nps: float = Field(default=0.0, description="Durchschnittlicher NPS")
    promoter_percentage: float = Field(default=0.0, description="Anteil Promoter in %")
    detractor_percentage: float = Field(
        default=0.0, description="Anteil Detractor in %"
    )
    passive_percentage: float = Field(default=0.0, description="Anteil Passive in %")
    top_issues: List[str] = Field(
        default_factory=list, description="Häufigste Probleme"
    )
    sentiment_summary: str = Field(
        default="Keine Sentiment-Daten verfügbar",
        description="Sentiment-Verteilung als Text",
    )


class UserFriendlySummary(BaseModel):
    """Benutzerfreundliche Zusammenfassung aller Analyse-Ergebnisse"""

    executive_summary: str = Field(description="Executive Summary für Management")
    key_insights: List[KeyInsight] = Field(description="Die wichtigsten Erkenntnisse")
    statistics: SummaryStatistics = Field(description="Zusammenfassende Statistiken")
    actionable_recommendations: List[ActionableRecommendation] = Field(
        description="Konkrete Handlungsempfehlungen"
    )
    detailed_findings: str = Field(description="Detaillierte Ergebnisse für Analysten")
    methodology_note: str = Field(description="Kurze Erklärung der Analysemethodik")
