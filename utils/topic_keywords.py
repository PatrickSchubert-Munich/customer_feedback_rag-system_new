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
- Fahrzeugübergabe: Abholung, Übergabe, Auslieferung des Fahrzeugs
- Probefahrt: Testfahrt, Fahrzeug ausprobieren
- Finanzierung: Leasing, Kredit, Finanzierungsangebote
- Ersatzwagen: Leihwagen, Ersatzfahrzeug während Reparatur
- Sonstiges: Alles andere
"""

# Topic-Kategorien mit zugehörigen Keywords (Case-insensitive)
# ERWEITERTE VERSION: Massiv erweiterte Keywords um "Sonstiges" zu reduzieren
TOPIC_KEYWORDS = {
    "Lieferproblem": [
        # Basis-Keywords
        "lieferung", "liefern", "geliefert", "versand", "verspätung", 
        "verspätet", "verzögerung", "nicht angekommen", "fehlend", 
        "zustellung", "transport", "paket", "lieferzeit", "lieferdatum",
        "nicht erhalten", "nicht geliefert", "späte lieferung", "lieferverzug",
        # Erweiterte Keywords
        "verzug", "auslieferung", "liefertermin", "zustelltermin", "wartezeit lieferung",
        "wochen gewartet", "monate gewartet", "noch nicht da", "immer noch nicht",
        "wann kommt", "wo bleibt", "lieferstatus", "tracking", "sendungsverfolgung",
        "verzögert", "verschoben", "verschleppt", "lieferschwierigkeiten",
        "lieferengpass", "nicht verfügbar", "ausverkauft", "nachlieferung",
        "teillieferung", "unvollständig geliefert", "fehlt noch", "wartet auf",
        "angekündigt aber nicht", "zugesagt aber", "sollte längst da sein"
    ],
    
    "Service": [
        # Basis-Keywords
        "service", "kundenservice", "beratung", "beraten", "freundlich",
        "unfreundlich", "hilfsbereit", "kompetenz", "mitarbeiter",
        "personal", "bedienung", "ansprechpartner", "höflich", "unhöflich",
        "empfang", "rezeption", "kundenbetreuung", "servicequalität",
        # Erweiterte Keywords
        "verkäufer", "verkäuferin", "berater", "beraterin", "händler",
        "autohaus", "betreuung", "support", "hotline", "servicecenter",
        "sehr freundlich", "super freundlich", "top service", "hervorragender service",
        "ausgezeichneter service", "kompetente beratung", "fachkundige beratung",
        "sehr hilfsbereit", "zuvorkommend", "entgegenkommend", "professionell",
        "unprofessionell", "inkompetent", "keine ahnung", "schlecht beraten",
        "schlechter service", "mieser service", "katastrophaler service",
        "arrogant", "überheblich", "respektlos", "ignoriert", "abgewimmelt",
        "nicht ernst genommen", "herablassend", "genervt", "unwillig",
        "keine hilfe", "niemand kümmert sich", "allein gelassen"
    ],
    
    "Produktqualität": [
        # Basis-Keywords
        "qualität", "defekt", "kaputt", "mangel", "mängel", "beschädigt",
        "fehler", "fehlerhaft", "problem", "funktioniert nicht", 
        "gebrochen", "riss", "kratzer", "verarbeitung", "zustand",
        "schaden", "beschädigung", "defizit", "qualitätsmangel",
        # Erweiterte Keywords
        "minderwertig", "billig verarbeitet", "schlechte qualität", "hochwertig",
        "erstklassig", "top qualität", "ausgezeichnete qualität", "premium",
        "lackschaden", "lackfehler", "dellen", "beulen", "rost", "korrosion",
        "spaltmaße", "schlecht verarbeitet", "wackelt", "klappert", "knarzt",
        "geräusche", "quietscht", "pfeift", "rattert", "vibriert",
        "materialfehler", "fertigungsfehler", "produktionsfehler", "montagefehler",
        "nicht passgenau", "asymmetrisch", "schief", "unsauber",
        "abgenutzt", "verschlissen", "porös", "brüchig", "spröde",
        "funktionsstörung", "ausfall", "defekt ab werk", "serienfehler",
        "rückruf", "reklamation", "gewährleistung", "garantiefall",
        "nicht einwandfrei", "beanstandung", "reklamiert"
    ],
    
    "Preis": [
        # Basis-Keywords
        "preis", "kosten", "teuer", "zu teuer", "überteuert", "rechnung",
        "bezahlung", "gebühr", "gebühren", "tarif", "euro", "€", "eur",
        "preisgestaltung", "preiswert", "günstig", "kostspielig",
        "aufschlag", "zusatzkosten", "preis-leistung",
        # Erweiterte Keywords
        "zu viel bezahlt", "wucher", "wucherpreis", "abzocke", "überzogen",
        "unverschämt teuer", "viel zu teuer", "maßlos überteuert", "horrende kosten",
        "exorbitant", "astronomisch", "gesalzen", "gepfeffert",
        "fairer preis", "angemessener preis", "guter preis", "super preis",
        "schnäppchen", "sonderangebot", "rabatt", "nachlass", "discount",
        "teurere alternative", "günstiger woanders", "anderswo billiger",
        "preis-leistungs-verhältnis", "verhältnis stimmt nicht", "nicht gerechtfertigt",
        "für das geld", "bei dem preis", "angesichts der kosten",
        "versteckte kosten", "nebenkosten", "aufpreis", "mehrkosten",
        "pauschalpreis", "festpreis", "endpreis", "gesamtpreis",
        "mehrwertsteuer", "mwst", "netto", "brutto", "inkl", "exkl",
        "zahlung", "zahlungsbedingungen", "zahlungsmodalitäten", "bezahlt",
        "forderung", "betrag", "summe", "ausgabe", "investition"
    ],
    
    "Terminvergabe": [
        # Basis-Keywords
        "termin", "termine", "wartezeit", "warten", "gewartet", "appointment",
        "terminvergabe", "buchung", "reservierung", "verfügbarkeit",
        "ausgebucht", "kein termin", "terminplanung", "zeitfenster",
        "stunden gewartet", "lange wartezeit", "terminvereinbarung",
        # Erweiterte Keywords
        "vereinbaren", "vereinbart", "vereinbarung", "buchen", "gebucht",
        "reserviert", "anmeldung", "pünktlich", "unpünktlich", "verspätung",
        "terminabsage", "abgesagt", "verschoben", "verlegt", "storniert",
        "zu lange gewartet", "endlos gewartet", "ewig gewartet", "warteschlange",
        "wartebereich", "wartezimmer", "wartenummer", "sofort dran", "ohne wartezeit",
        "schnell termin", "kurzfristig", "langfristig", "wochen im voraus",
        "monate im voraus", "nicht verfügbar", "ausgebucht bis", "voll belegt",
        "keine termine frei", "frühester termin", "nächster termin",
        "terminkalender", "zeitplan", "zeitslot", "slot", "freie kapazität",
        "überlaufen", "überfüllt", "voll", "wenig los", "leer",
        "express", "notfall", "dringend", "eilig", "sofort",
        "flexibel", "flexible termine", "jederzeit", "rund um die uhr"
    ],
    
    "Werkstatt": [
        # Basis-Keywords
        "werkstatt", "reparatur", "reparieren", "repariert", "mechaniker",
        "inspektion", "wartung", "techniker", "werkstattbesuch",
        "reifenwechsel", "ölwechsel", "bremsen", "reifen", "motor",
        "getriebe", "fahrzeug", "auto", "wagen", "pkw", "reparaturzeit",
        "werkstattaufenthalt",
        # Erweiterte Keywords - Automotive-spezifisch
        "kfz", "kraftfahrzeug", "meister", "kfz-meister", "schrauber",
        "hebebühne", "diagnose", "diagnosegerät", "fehlercode", "auslesen",
        "hauptuntersuchung", "hu", "tüv", "abgasuntersuchung", "au",
        "serviceintervall", "inspektion fällig", "service fällig", "checkup",
        "durchsicht", "jahresinspektion", "zwischenservice", "kundendienst",
        "achsvermessung", "spureinstellung", "radlager", "stoßdämpfer",
        "auspuff", "katalysator", "abgasanlage", "klimaanlage", "klimaservice",
        "batteriewechsel", "batterie", "lichtmaschine", "anlasser",
        "zahnriemen", "zahnriemenwechsel", "steuerkette", "kupplung",
        "bremscheiben", "bremsbeläge", "bremsflüssigkeit", "bremsanlage",
        "scheibenwischer", "wischerblätter", "beleuchtung", "scheinwerfer",
        "rückleuchten", "innenraumfilter", "luftfilter", "kraftstofffilter",
        "motoröl", "getriebeöl", "kühlflüssigkeit", "frostschutz",
        "rostschutz", "unterbodenschutz", "lackierung", "smart repair",
        "delle", "steinschlag", "windschutzscheibe", "autoglas",
        "hupe", "airbag", "sicherheitsgurt", "elektronik", "steuergerät",
        "wegfahrsperre", "zentralverriegelung", "fensterheber", "schiebedach"
    ],
    
    "Kommunikation": [
        # Basis-Keywords
        "kommunikation", "information", "informiert", "benachrichtigung",
        "rückmeldung", "rückruf", "anruf", "telefon", "erreichbarkeit",
        "e-mail", "mail", "nachricht", "kontakt", "erreichen",
        "nicht erreichbar", "keine rückmeldung", "nicht informiert",
        "bescheid", "mitteilung", "telefonat", "informationsfluss",
        # Erweiterte Keywords
        "angerufen", "telefoniert", "zurückgerufen", "durchgestellt",
        "mailbox", "anrufbeantworter", "warteschleife", "hotline",
        "niemand geht ran", "niemand erreicht", "ständig besetzt", "besetzt",
        "rückrufbitte", "rückruf zugesagt", "meldet sich nicht", "keine reaktion",
        "ignoriert", "nicht beantwortet", "unbeantwortet", "keine antwort",
        "sms", "whatsapp", "messenger", "chat", "online", "schriftlich",
        "brief", "post", "fax", "kontaktformular", "formular ausgefüllt",
        "gut informiert", "immer auf dem laufenden", "regelmäßig updates",
        "proaktiv informiert", "rechtzeitig bescheid", "zeitnah informiert",
        "schlecht informiert", "keine updates", "im dunkeln gelassen",
        "nicht auf dem laufenden", "erfährt nichts", "vergessen zu informieren",
        "missverständnis", "falsch verstanden", "aneinander vorbeigeredet",
        "unklar", "verwirrend", "widersprüchlich", "klar kommuniziert",
        "deutlich", "verständlich", "nachvollziehbar", "transparent"
    ],
    
    "Fahrzeugübergabe": [
        # Basis-Keywords
        "übergabe", "abholung", "abholen", "auslieferung", "ausgeliefert",
        "übernahme", "fahrzeugübergabe", "übergabetermin", "abholtermin",
        "fahrzeug abholen", "wagen abholen", "neuwagen übergabe",
        "schlüsselübergabe", "fahrzeugauslieferung", "bereitstellung",
        "übergabeprozess", "fahrzeug erhalten", "in empfang genommen",
        # Erweiterte Keywords
        "schlüssel", "fahrzeugschlüssel", "autoschlüssel", "zweitschlüssel",
        "fahrzeugbrief", "zulassungsbescheinigung", "brief", "papiere",
        "fahrzeugpapiere", "kfz-brief", "serviceheft", "scheckheft",
        "bedienungsanleitung", "handbuch", "bordbuch", "garantie",
        "garantieheft", "garantiekarte", "werkstatthandbuch",
        "übergabeprotokoll", "abnahmeprotokoll", "checkliste",
        "einweisung", "erklärung", "vorführung", "gezeigt", "erklärt",
        "funktionen erklärt", "technik erklärt", "ausstattung gezeigt",
        "probegesessen", "kennzeichen", "nummernschilder", "angemeldet",
        "zugelassen", "zulassung", "versicherung", "versichert",
        "vollgetankt", "volltanken", "tank voll", "gewaschen", "sauber",
        "frisch poliert", "aufbereitet", "gereinigt", "gepflegt zustand",
        "bereit zur abholung", "abholbereit", "steht bereit", "wartet",
        "übergabezeremonie", "festlicher rahmen", "sekt", "geschenk"
    ],
    
    "Probefahrt": [
        # Basis-Keywords
        "probefahrt", "testfahrt", "probe fahren", "test fahren",
        "fahrzeug testen", "auto testen", "ausprobieren", "test drive",
        "probefahren", "testfahren", "fahrzeug ausprobieren",
        "eine runde fahren", "zur probe", "testlauf",
        # Erweiterte Keywords
        "testfahrzeug", "vorführwagen", "gefahren", "selbst gefahren",
        "mitgefahren", "beifahrer", "fahrerlebnis", "fahrgefühl",
        "testroute", "proberunde", "teststrecke", "kurze runde", "längere fahrt",
        "probesitzen", "sitzprobe", "platz nehmen", "hinsetzen",
        "motor gestartet", "angelassen", "losgefahren", "durchgestartet",
        "beschleunigt", "beschleunigung", "power", "leistung getestet",
        "kurven", "handling", "fahrverhalten", "straßenlage", "komfort",
        "lenkung", "bremsen getestet", "schaltung", "automatik",
        "ausstattung ausprobiert", "navigation getestet", "sound",
        "innenraum", "sitzkomfort", "raumgefühl", "platzverhältnisse",
        "kofferraum", "laderaum", "variabilität", "rückbank",
        "assistenzsysteme", "tempomat", "spurhalteassistent", "einparkhilfe",
        "rückfahrkamera", "totwinkelassistent", "abstandsregler",
        "begeistert", "überzeugt", "enttäuscht", "erwartet", "vorgestellt"
    ],
    
    "Finanzierung": [
        # Basis-Keywords
        "finanzierung", "leasing", "kredit", "rate", "raten",
        "anzahlung", "ratenzahlung", "kreditangebot", "leasingangebot",
        "finanzierungsangebot", "darlehen", "tilgung", "zinsen",
        "monatliche rate", "leasingvertrag", "kreditvertrag",
        "finanzierungsvertrag", "kreditgeber", "leasinggeber",
        "schlussrate", "restwert",
        # Erweiterte Keywords
        "bank", "bankfinanzierung", "autobank", "hausbank", "kreditinstitut",
        "zinssatz", "effektiver jahreszins", "sollzins", "zinskosten",
        "laufzeit", "kreditlaufzeit", "leasinglaufzeit", "monate", "jahre",
        "sonderzahlung", "sondertilgung", "einmalzahlung", "schlussrate",
        "ballon", "ballonfinanzierung", "drei-wege-finanzierung",
        "kilometerleasing", "restwertleasing", "full service leasing",
        "leasingfaktor", "leasingrate", "kreditrate", "finanzierungsrate",
        "bonitätsprüfung", "schufa", "bonität", "kreditwürdigkeit",
        "anzahlung", "eigenkapital", "eigenanteil", "zuzahlung",
        "ratenhöhe", "ratenpause", "flexible raten", "anpassbare raten",
        "vorzeitige rückzahlung", "ablösung", "umschuldung", "prolongation",
        "versicherung", "restschuldversicherung", "gap-versicherung",
        "vollkasko", "teilkasko", "haftpflicht", "versicherungsprämie",
        "inzahlungnahme", "gebrauchtwagen", "altfahrzeug", "restwert",
        "finanzierungszusage", "kreditgenehmigung", "bewilligung", "abgelehnt"
    ],
    
    "Ersatzwagen": [
        # Basis-Keywords
        "ersatzwagen", "leihwagen", "ersatzfahrzeug", "leihfahrzeug",
        "mietwagen", "überbrückungsfahrzeug", "ersatz", "leihauto",
        "ersatzauto", "mobilität", "mobilitätsgarantie",
        "ersatzstellung", "zur verfügung gestellt", "leihgabe",
        "fahrzeug gestellt", "auto gestellt",
        # Erweiterte Keywords
        "shuttle", "shuttleservice", "bringservice", "holservice",
        "abholservice", "hol- und bringservice", "abholen und bringen",
        "öffentliche verkehrsmittel", "öpnv", "taxi", "uber",
        "kostenloser ersatzwagen", "kostenlose mobilität", "gratis",
        "gegen gebühr", "gegen aufpreis", "selbstbeteiligung", "kaution",
        "mietvertrag", "leihvertrag", "übernahmeprotokoll", "rückgabe",
        "rückgabeprotokoll", "schaden am leihwagen", "kilometer",
        "kilometerbegrenzung", "freikilometer", "tankregelung", "vollgetankt",
        "vergleichbares fahrzeug", "gleichwertiges fahrzeug", "kleineres auto",
        "größeres auto", "ersatzklasse", "fahrzeugklasse",
        "sofort verfügbar", "am selben tag", "nächster tag", "wartezeit",
        "keine verfügbarkeit", "kein ersatzwagen", "ausgebucht",
        "versicherung", "versicherungsschutz", "haftung", "schaden",
        "reparaturdauer", "während der reparatur", "solange", "überbrückung"
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
