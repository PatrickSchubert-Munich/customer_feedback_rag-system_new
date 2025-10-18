"""
Topic-Klassifizierung für Customer Feedback basierend auf Keyword-Matching.

Kategorien:
- Lieferproblem: Verspätungen, fehlende Lieferungen, Versandprobleme
- Service: Kundenservice, Beratung, Freundlichkeit, Erreichbarkeit
- Produktqualität: Defekte, Mängel, Qualität des Produkts
- Preis: Kosten, Preisgestaltung, zu teuer
- Terminvergabe: Wartezeiten, Terminprobleme, Verfügbarkeit
- Werkstatt: Reparatur, technische Arbeiten, Mechaniker
- Kommunikation: Informationsfluss, Rückrufe, Erreichbarkeit
- Sonstiges: Alles andere
"""

# Topic-Kategorien mit zugehörigen Keywords (Case-insensitive)
TOPIC_KEYWORDS = {
    "Lieferproblem": [
        "lieferung", "liefern", "geliefert", "versand", "verspätung", 
        "verspätet", "verzögerung", "nicht angekommen", "fehlend", 
        "zustellung", "transport", "paket", "lieferzeit", "lieferdatum",
        "nicht erhalten", "nicht geliefert", "späte lieferung"
    ],
    
    "Service": [
        "service", "kundenservice", "beratung", "beraten", "freundlich",
        "unfreundlich", "hilfsbereit", "kompetenz", "mitarbeiter",
        "personal", "bedienung", "ansprechpartner", "höflich", "unhöflich",
        "empfang", "rezeption", "kundenbetreuung"
    ],
    
    "Produktqualität": [
        "qualität", "defekt", "kaputt", "mangel", "mängel", "beschädigt",
        "fehler", "fehlerhaft", "problem", "funktioniert nicht", 
        "gebrochen", "riss", "kratzer", "verarbeitung", "zustand",
        "schaden", "beschädigung", "defizit"
    ],
    
    "Preis": [
        "preis", "kosten", "teuer", "zu teuer", "überteuert", "rechnung",
        "bezahlung", "gebühr", "gebühren", "tarif", "euro", "€", "eur",
        "preisgestaltung", "preiswert", "günstig", "kostspielig",
        "aufschlag", "zusatzkosten"
    ],
    
    "Terminvergabe": [
        "termin", "termine", "wartezeit", "warten", "gewartet", "appointment",
        "terminvergabe", "buchung", "reservierung", "verfügbarkeit",
        "ausgebucht", "kein termin", "terminplanung", "zeitfenster",
        "stunden gewartet", "lange wartezeit"
    ],
    
    "Werkstatt": [
        "werkstatt", "reparatur", "reparieren", "repariert", "mechaniker",
        "inspektion", "wartung", "service", "techniker", "werkstattbesuch",
        "reifenwechsel", "ölwechsel", "bremsen", "reifen", "motor",
        "getriebe", "fahrzeug", "auto", "wagen", "pkw"
    ],
    
    "Kommunikation": [
        "kommunikation", "information", "informiert", "benachrichtigung",
        "rückmeldung", "rückruf", "anruf", "telefon", "erreichbarkeit",
        "e-mail", "mail", "nachricht", "kontakt", "erreichen",
        "nicht erreichbar", "keine rückmeldung", "nicht informiert",
        "bescheid", "mitteilung"
    ],
}

# Fallback-Kategorie
DEFAULT_TOPIC = "Sonstiges"


def classify_feedback_topic(text: str, confidence_threshold: float = 0.3) -> tuple[str, float]:
    """
    Klassifiziert ein Feedback basierend auf Keyword-Matching.
    
    Args:
        text (str): Der zu klassifizierende Feedback-Text
        confidence_threshold (float): Minimale Confidence für Topic-Zuweisung (0.0-1.0)
    
    Returns:
        tuple[str, float]: (Topic, Confidence-Score)
            - Topic: Kategorie-Name oder "Sonstiges"
            - Confidence: Wert zwischen 0.0 und 1.0
    
    Beispiel:
        >>> classify_feedback_topic("Die Lieferung kam viel zu spät")
        ('Lieferproblem', 0.85)
    """
    if not text or not isinstance(text, str):
        return (DEFAULT_TOPIC, 0.0)
    
    text_lower = text.lower()
    topic_scores = {}
    
    # Zähle Keyword-Treffer pro Topic
    for topic, keywords in TOPIC_KEYWORDS.items():
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        
        if matches > 0:
            # Confidence basiert auf: Anzahl Treffer / Anzahl Wörter im Text
            # Normalisiert auf 0-1 Skala
            word_count = len(text.split())
            confidence = min(1.0, (matches / max(1, word_count / 10)))
            topic_scores[topic] = confidence
    
    # Bestes Topic auswählen
    if topic_scores:
        best_topic = max(topic_scores.items(), key=lambda x: x[1])[0]
        best_confidence = topic_scores[best_topic]
        
        # Nur Topic zuweisen wenn Confidence hoch genug
        if best_confidence >= confidence_threshold:
            return (best_topic, best_confidence)
    
    # Fallback
    return (DEFAULT_TOPIC, 0.0)


def get_all_topics() -> list[str]:
    """
    Gibt alle verfügbaren Topic-Kategorien zurück.
    
    Returns:
        list[str]: Liste aller Topic-Namen inklusive "Sonstiges"
    """
    return list(TOPIC_KEYWORDS.keys()) + [DEFAULT_TOPIC]


def get_topic_keywords(topic: str) -> list[str]:
    """
    Gibt die Keywords für ein bestimmtes Topic zurück.
    
    Args:
        topic (str): Topic-Name
    
    Returns:
        list[str]: Liste der Keywords oder leere Liste
    """
    return TOPIC_KEYWORDS.get(topic, [])
