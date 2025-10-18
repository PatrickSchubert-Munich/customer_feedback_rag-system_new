"""
Advanced Synthetic Data Generator für Kundenfeedback - Enterprise Edition
=========================================================================

Dieses erweiterte Modul erzeugt hochwertige synthetische Kundenfeedback-Daten mit:
- Maximaler Diversität (Alter, Geschlecht, Bildung, Region)
- Vollständiger Anonymisierung mit kreativen Fake-Namen
- Realistischer Variation und Authentizität
- Nahtloser Integration mit echten Daten
- Bias-Vermeidung durch statistische Kontrollen
- Skalierbar für tausende Datensätze
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string
import itertools
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')


@dataclass
class PersonaProfile:
    """Definiert eine Kundenpers ona mit allen relevanten Eigenschaften"""
    age_group: str
    gender: str
    education_level: str
    tech_affinity: str
    communication_style: str
    typical_concerns: List[str]
    text_patterns: Dict[str, float]
    typo_probability: float
    emoji_usage: float
    formality_level: float


class BiasMonitor:
    """
    Überwacht und verhindert Bias während der Datengenerierung.
    Limit: Keine Phrase/Topic darf mehr als 50x verwendet werden.
    """
    def __init__(self, max_repeats: int = 50):
        self.phrase_counter = defaultdict(int)
        self.topic_counter = defaultdict(int)
        self.persona_counter = defaultdict(int)
        self.market_counter = defaultdict(int)
        self.max_repeats = max_repeats
        
    def track_phrase(self, phrase: str) -> bool:
        """Prüft ob Phrase noch verwendet werden darf"""
        if self.phrase_counter[phrase] >= self.max_repeats:
            return False  # Phrase zu oft verwendet
        self.phrase_counter[phrase] += 1
        return True
        
    def track_topic(self, topic: str) -> bool:
        """Prüft Topic-Balance"""
        if self.topic_counter[topic] >= self.max_repeats * 2:  # Topics dürfen öfter vorkommen
            return False
        self.topic_counter[topic] += 1
        return True
        
    def get_report(self) -> Dict:
        """Gibt Bias-Report zurück"""
        return {
            'most_used_phrases': sorted(self.phrase_counter.items(), key=lambda x: x[1], reverse=True)[:10],
            'topic_distribution': dict(self.topic_counter),
            'total_phrases': len(self.phrase_counter),
            'warnings': [
                f"Phrase '{phrase}' verwendet {count}x (Limit: {self.max_repeats})" 
                for phrase, count in self.phrase_counter.items() 
                if count >= self.max_repeats
            ]
        }


class PhraseDiversifier:
    """
    Ersetzt monotone Phrasen wie "customer states" (2.331x im Original!)
    durch 100+ natürliche Variationen mit Usage-Tracking.
    """
    def __init__(self):
        self.usage_counter = defaultdict(int)
        
    def get_diverse_opening(self, sentiment: str, bias_monitor: BiasMonitor) -> str:
        """
        Holt eine Opening-Phrase die NICHT overused ist.
        Falls alle Optionen erschöpft, wähle die am wenigsten genutzte.
        """
        # Diese werden in _initialize_text_components() gesetzt
        # Hier nur Fallback für ältere Code-Pfade
        fallback_openings = {
            'positiv': ["Sehr zufrieden mit", "Top Service bei", "Empfehlenswert ist"],
            'neutral': ["War heute bei", "Hatte einen Termin bei"],
            'negativ': ["Enttäuschend war", "Probleme gab es bei"]
        }
        
        options = fallback_openings.get(sentiment, fallback_openings['neutral'])
        
        # Finde verfügbare Phrases
        available = [p for p in options if bias_monitor.track_phrase(p)]
        
        if available:
            chosen = random.choice(available)
        else:
            # Alle erschöpft - nimm die am wenigsten genutzte
            chosen = min(options, key=lambda p: self.usage_counter[p])
            self.usage_counter[chosen] += 1
            
        return chosen


class NPSSentimentCorrelator:
    """
    Stellt realistische Korrelation zwischen NPS und Sentiment her.
    Basierend auf Analyse: Detractors (16.8%) meist negativ, Promoters (55.8%) meist positiv.
    """
    def __init__(self):
        # Realistische Verteilungen aus Analyse
        self.correlation_map = {
            'Detractor': {'positiv': 0.05, 'neutral': 0.25, 'negativ': 0.70},  # 70% negativ
            'Passive': {'positiv': 0.20, 'neutral': 0.60, 'negativ': 0.20},    # 60% neutral
            'Promoter': {'positiv': 0.70, 'neutral': 0.25, 'negativ': 0.05}    # 70% positiv
        }
        
    def get_realistic_sentiment(self, nps_category: str) -> str:
        """Gibt sentiment basierend auf NPS-Kategorie zurück"""
        probs = self.correlation_map[nps_category]
        return np.random.choice(['positiv', 'neutral', 'negativ'], p=list(probs.values()))


class TextLengthController:
    """
    Kontrolliert Textlängen basierend auf echten Daten:
    Min: 1 Wort, Max: 361 Wörter, Median: 21, Mean: 28.5
    """
    def __init__(self):
        # Aus Analyse der 17.884 echten Feedbacks
        self.min_words = 1
        self.max_words = 361
        self.median_words = 21
        self.mean_words = 28.5
        self.std_words = 25  # Geschätzt aus Verteilung
        
    def get_realistic_length(self, sentiment: str) -> int:
        """
        Gibt realistische Wortanzahl zurück.
        Negative Feedbacks sind oft länger (Detailkritik).
        """
        if sentiment == 'negativ':
            # Negative Feedbacks tendieren zu mehr Details
            target = int(np.random.normal(self.mean_words * 1.3, self.std_words))
        elif sentiment == 'positiv':
            # Positive Feedbacks oft kürzer
            target = int(np.random.normal(self.mean_words * 0.8, self.std_words * 0.7))
        else:
            # Neutrale Feedbacks um Median
            target = int(np.random.normal(self.median_words, self.std_words * 0.6))
            
        # Clamp to realistic range
        return max(self.min_words, min(self.max_words, target))


class AdvancedSyntheticFeedbackGenerator:
    """
    Enterprise-Grade Generator für synthetische Kundenfeedback-Daten.
    
    Features:
    - Lernt aus echten Kundendaten
    - Vollständige Anonymisierung mit kreativen Fake-Namen
    - Demografische Diversität
    - Realistische Sprachmuster basierend auf echten Feedbacks
    - Zeitliche Dynamik
    - Bias-Kontrolle
    - Skalierbar für große Datenmengen
    """
    
    def __init__(self, seed: int = 42, enable_fun_mode: bool = True):
        """
        Initialisiert den Generator.
        
        Args:
            seed: Random seed für Reproduzierbarkeit
            enable_fun_mode: Aktiviert kreative/lustige Namen für Werkstätten
        """
        np.random.seed(seed)
        random.seed(seed)
        
        self.enable_fun_mode = enable_fun_mode
        self.learned_patterns = {}  # Speichert Muster aus echten Daten
        
        # NEU: Initialisiere Bias-Prevention und Quality-Control Komponenten
        self.bias_monitor = BiasMonitor(max_repeats=50)
        self.phrase_diversifier = PhraseDiversifier()
        self.nps_sentiment_correlator = NPSSentimentCorrelator()
        self.text_length_controller = TextLengthController()
        
        # Initialisiere alle Komponenten
        self._initialize_fake_entities()
        self._initialize_personas()
        self._initialize_markets_and_regions()
        self._initialize_topics()  # NEU: Topics mit Gewichtungen
        self._initialize_text_components()
        self._initialize_temporal_patterns()
        
        # NPS-Kategorien mit EXAKTEN Verteilungen aus Analyse (17.884 Feedbacks)
        # Detractors: 16.8%, Passives: 27.4%, Promoters: 55.8%
        self.nps_distribution = {
            'Detractor': list(range(0, 7)),   # NPS 0-6
            'Passive': list(range(7, 9)),     # NPS 7-8
            'Promoter': list(range(9, 11))    # NPS 9-10
        }
        self.nps_weights = {
            'Detractor': 0.168,  # 16.8% aus Analyse
            'Passive': 0.274,    # 27.4% aus Analyse
            'Promoter': 0.558    # 55.8% aus Analyse
        }
    
    def learn_from_real_data(self, real_data_path: str):
        """
        Lernt Muster aus echten Kundendaten
        
        Args:
            real_data_path: Pfad zur CSV-Datei mit echten Daten
        """
        print("📚 Lerne aus echten Kundendaten...")
        
        try:
            df_real = pd.read_csv(real_data_path, encoding='utf-8')
        except:
            df_real = pd.read_csv(real_data_path, encoding='latin-1')
            
        # Extrahiere Verbatims
        if 'Verbatim' in df_real.columns:
            verbatims = df_real['Verbatim'].dropna().tolist()
            
            # Analysiere Muster
            self.learned_patterns = {
                'phrase_patterns': self._extract_phrase_patterns(verbatims),
                'length_distribution': self._analyze_text_lengths(verbatims),
                'topic_indicators': self._extract_topic_indicators(verbatims),
                'sentiment_phrases': self._extract_sentiment_phrases(df_real),
                'common_issues': self._extract_common_issues(verbatims)
            }
            
            print(f"   ✓ {len(verbatims)} Verbatims analysiert")
            print(f"   ✓ {len(self.learned_patterns['phrase_patterns'])} Phrasen-Muster extrahiert")
            print(f"   ✓ {len(self.learned_patterns['common_issues'])} häufige Probleme identifiziert")
            
    def _extract_phrase_patterns(self, verbatims: List[str]) -> Dict:
        """Extrahiert wiederkehrende Phrasen aus echten Verbatims"""
        
        patterns = {
            'wartezeit': [],
            'service': [],
            'kosten': [],
            'kommunikation': [],
            'werkstatt': []
        }
        
        # Keywords für Kategorisierung
        keywords = {
            'wartezeit': ['warten', 'wartezeit', 'stunden', 'minuten', 'lange', 'dauerte'],
            'service': ['mitarbeiter', 'freundlich', 'unfreundlich', 'personal', 'beratung'],
            'kosten': ['euro', 'rechnung', 'preis', 'kosten', 'teuer', 'zahlen'],
            'kommunikation': ['rückruf', 'angerufen', 'erreicht', 'information', 'mitgeteilt'],
            'werkstatt': ['reparatur', 'werkstatt', 'arbeit', 'fahrzeug', 'problem']
        }
        
        for verbatim in verbatims:
            if not isinstance(verbatim, str):
                continue
                
            verbatim_lower = verbatim.lower()
            sentences = verbatim.split('.')
            
            for sentence in sentences:
                if len(sentence) > 10:  # Nur sinnvolle Sätze
                    for category, words in keywords.items():
                        if any(word in sentence.lower() for word in words):
                            # Anonymisiere den Satz
                            anonymized = self._anonymize_sentence(sentence)
                            if anonymized and anonymized not in patterns[category]:
                                patterns[category].append(anonymized)
                                
        return patterns
    
    def _anonymize_sentence(self, sentence: str) -> str:
        """Anonymisiert persönliche Daten in einem Satz"""
        
        # Entferne spezifische Namen und Orte
        anonymized = sentence
        
        # Ersetze Uhrzeiten
        import re
        anonymized = re.sub(r'\d{1,2}:\d{2}', 'XX:XX', anonymized)
        anonymized = re.sub(r'\d{1,2}\.\d{2}', 'XX:XX', anonymized)
        
        # Ersetze Datumsangaben
        anonymized = re.sub(r'\d{1,2}\.\d{1,2}\.\d{2,4}', 'XX.XX.XXXX', anonymized)
        
        # Ersetze Kennzeichen
        anonymized = re.sub(r'[A-Z]{1,3}-[A-Z]{1,2}\s?\d{1,4}', 'XX-XX XXXX', anonymized)
        
        # Ersetze E-Mail-Adressen
        anonymized = re.sub(r'[\w\.-]+@[\w\.-]+', 'kunde@example.com', anonymized)
        
        # Ersetze Telefonnummern
        anonymized = re.sub(r'[\d\s\-\+\(\)]{10,}', 'TELEFONNUMMER', anonymized)
        
        # Ersetze große Zahlen (vermutlich Preise oder IDs)
        anonymized = re.sub(r'\d{5,}', 'XXXXX', anonymized)
        
        return anonymized.strip()
    
    def _extract_common_issues(self, verbatims: List[str]) -> List[str]:
        """Extrahiert häufige Probleme aus Verbatims"""
        
        issues = []
        issue_patterns = [
            "wurde nicht zurückgerufen",
            "musste lange warten",
            "Termin nicht eingehalten",
            "Problem nicht behoben",
            "höhere Kosten als angegeben",
            "unfreundliches Personal",
            "keine Information erhalten",
            "Fahrzeug nicht fertig",
            "Ersatzteile nicht vorhanden",
            "schlechte Kommunikation"
        ]
        
        for pattern in issue_patterns:
            count = sum(1 for v in verbatims if isinstance(v, str) and pattern.lower() in v.lower())
            if count > 2:  # Nur häufige Probleme
                issues.append(pattern)
                
        return issues
    
    def _analyze_text_lengths(self, verbatims: List[str]) -> Dict:
        """Analysiert Textlängen-Verteilung"""
        
        lengths = [len(str(v).split()) for v in verbatims if isinstance(v, str)]
        
        return {
            'min': min(lengths) if lengths else 0,
            'max': max(lengths) if lengths else 0,
            'mean': np.mean(lengths) if lengths else 0,
            'std': np.std(lengths) if lengths else 0,
            'quartiles': np.percentile(lengths, [25, 50, 75]) if lengths else [0, 0, 0]
        }
    
    def _extract_topic_indicators(self, verbatims: List[str]) -> Dict:
        """Extrahiert Themen-Indikatoren aus Verbatims"""
        
        topics = {
            'Werkstatt': ['werkstatt', 'reparatur', 'inspektion', 'wartung'],
            'Service': ['service', 'beratung', 'mitarbeiter', 'personal'],
            'Terminvergabe': ['termin', 'wartezeit', 'pünktlich', 'verspätung'],
            'Kosten': ['preis', 'euro', 'rechnung', 'kosten', 'teuer'],
            'Kommunikation': ['anruf', 'rückruf', 'information', 'mitgeteilt']
        }
        
        topic_counts = {topic: 0 for topic in topics}
        
        for verbatim in verbatims:
            if not isinstance(verbatim, str):
                continue
            verbatim_lower = verbatim.lower()
            for topic, keywords in topics.items():
                if any(kw in verbatim_lower for kw in keywords):
                    topic_counts[topic] += 1
                    
        return topic_counts
    
    def _extract_sentiment_phrases(self, df_real: pd.DataFrame) -> Dict:
        """Extrahiert sentiment-spezifische Phrasen"""
        
        sentiment_phrases = {
            'positiv': [],
            'neutral': [],
            'negativ': []
        }
        
        if 'NPS' in df_real.columns and 'Verbatim' in df_real.columns:
            # Promoters (NPS 9-10) = meist positiv
            promoters = df_real[df_real['NPS'] >= 9]['Verbatim'].dropna()
            for verbatim in promoters:
                if isinstance(verbatim, str) and len(verbatim) > 20:
                    sentences = verbatim.split('.')
                    for s in sentences[:2]:  # Nur erste Sätze
                        if len(s) > 10:
                            sentiment_phrases['positiv'].append(self._anonymize_sentence(s))
            
            # Detractors (NPS 0-6) = meist negativ  
            detractors = df_real[df_real['NPS'] <= 6]['Verbatim'].dropna()
            for verbatim in detractors:
                if isinstance(verbatim, str) and len(verbatim) > 20:
                    sentences = verbatim.split('.')
                    for s in sentences[:2]:
                        if len(s) > 10:
                            sentiment_phrases['negativ'].append(self._anonymize_sentence(s))
                            
        return sentiment_phrases
    
    def _initialize_topics(self):
        """
        Initialisiert Topics mit exakten Gewichtungen aus Analyse von 17.884 Feedbacks
        KRITISCH: Reifenwechsel (nur 5x im Original!) und Reinigung (0x) wurden hinzugefügt
        """
        
        # MASSIV ERWEITERT - Basierend auf Analyse von 17.884 echten Feedbacks
        # Gewichtung nach tatsächlicher Häufigkeit:
        # Service & Beratung: 30.6%, Terminvergabe: 30.1%, Fahrzeugqualität: 15.6%
        self.topics_hierarchy = {
            'Service & Beratung': {  # 30.6% - HÖCHSTE PRIORITÄT
                'subtopics': [
                    'Freundlichkeit und Höflichkeit', 'Kompetenz der Berater', 
                    'Lösungsorientierung', 'Nachbetreuung', 'Kulanz',
                    'Beratungsqualität', 'Erreichbarkeit', 'Reaktionsgeschwindigkeit',
                    'Kundenorientierung', 'Beschwerdemanagement'
                ],
                'weight': 0.306
            },
            'Terminvergabe': {  # 30.1% - HÖCHSTE PRIORITÄT
                'subtopics': [
                    'Verfügbarkeit von Terminen', 'Flexibilität bei Terminen',
                    'Online-Terminbuchung', 'Wartezeit auf Termin', 'Pünktlichkeit',
                    'Spontane Termine', 'Terminabsage', 'Terminbestätigung',
                    'Terminverschiebung', 'Wartezeit vor Ort'
                ],
                'weight': 0.301
            },
            'Fahrzeugqualität': {  # 15.6%
                'subtopics': [
                    'Verarbeitungsqualität', 'Zuverlässigkeit', 'Ausstattung',
                    'Design', 'Fahreigenschaften', 'Materialqualität',
                    'Lackqualität', 'Technische Features', 'Langlebigkeit'
                ],
                'weight': 0.156
            },
            'Kommunikation': {  # 9.2%
                'subtopics': [
                    'Transparenz bei Kosten', 'Erreichbarkeit telefonisch',
                    'Rückmeldung nach Anfrage', 'Verständlichkeit',
                    'Proaktive Information', 'E-Mail-Kommunikation',
                    'Status-Updates', 'Sprachbarrieren'
                ],
                'weight': 0.092
            },
            'Werkstattservice': {  # 5.6%
                'subtopics': [
                    'Reparaturqualität', 'Inspektion', 'Wartung', 'Diagnose',
                    'Teilequalität', 'Sauberkeit Werkstatt', 'Ausstattung Werkstatt',
                    'Wartebereich', 'Ersatzteilbeschaffung'
                ],
                'weight': 0.056
            },
            'Preis-Leistung': {  # 4.3%
                'subtopics': [
                    'Werkstattkosten', 'Ersatzteilpreise', 'Fairness der Preise',
                    'Kostenvoranschlag', 'Zusatzkosten', 'Preistransparenz',
                    'Garantieleistungen', 'Kulanzregelung'
                ],
                'weight': 0.043
            },
            'Mitarbeiter': {  # 2.6%
                'subtopics': [
                    'Serviceberater', 'Mechaniker', 'Empfangspersonal',
                    'Verkaufspersonal', 'Management', 'Teamwork',
                    'Professionalität', 'Erscheinungsbild'
                ],
                'weight': 0.026
            },
            # UNTERREPRÄSENTIERT - Gezielt hinzugefügt (nur 5 Vorkommen in Originaldaten!)
            'Reifenwechsel': {  # 1.5% - MUSS GENERIERT WERDEN
                'subtopics': [
                    'Sommer-/Winterreifen Wechsel', 'Terminverfügbarkeit Reifenwechsel',
                    'Preis für Reifenwechsel', 'Einlagerung der Reifen',
                    'Reifenzustand prüfen', 'Auswuchten der Reifen',
                    'Ventile ersetzen', 'Dauer des Reifenwechsels',
                    'Online-Buchung Reifenwechsel', 'Express-Reifenwechsel',
                    'Reifenkauf beim Wechsel', 'Reifenentsorgung',
                    'Wartezeit Reifenwechsel', 'Rdks-System Anpassung',
                    'Felgenreinigung beim Wechsel'
                ],
                'weight': 0.015
            },
            # KOMPLETT FEHLEND - Gezielt ergänzt (0 Vorkommen in Originaldaten!)
            'Reinigung & Pflege': {  # 1.0% - NEU GENERIEREN
                'subtopics': [
                    'Fahrzeugwäsche nach Service', 'Innenraumreinigung',
                    'Aufbereitung des Fahrzeugs', 'Sauberhaltung bei Reparatur',
                    'Polsterreinigung', 'Lack aufpolieren',
                    'Motorwäsche', 'Felgenreinigung',
                    'Scheibenreinigung innen', 'Geruchsbeseitigung',
                    'Lederpflege', 'Kunststoffpflege',
                    'Unterbodenwäsche', 'Steinschlag-Behandlung',
                    'Nano-Versiegelung'
                ],
                'weight': 0.010
            },
            'Ersatzfahrzeug': {  # 0.8%
                'subtopics': [
                    'Verfügbarkeit Ersatzwagen', 'Zustand Ersatzfahrzeug',
                    'Kategorie Leihwagen', 'Buchung Ersatzwagen',
                    'Kosten Leihfahrzeug', 'Versicherung Ersatzwagen',
                    'Tankregelung Leihwagen'
                ],
                'weight': 0.008
            },
            'Digitale Services': {  # 0.5%
                'subtopics': [
                    'App-Nutzung', 'Website-Funktionalität', 'Online-Portal',
                    'Digitale Rechnung', 'SMS/E-Mail Updates',
                    'Online-Terminbuchung', 'Digitaler Kostenvoranschlag'
                ],
                'weight': 0.005
            }
        }
        
        # Sentiments für Feedback-Generierung
        self.sentiments = ['positiv', 'neutral', 'negativ']
        
    def _initialize_fake_entities(self):
        """Initialisiert kreative Fake-Namen für Anonymisierung"""
        
        # Kreative Werkstatt-Namen (lustig aber professionell)
        if self.enable_fun_mode:
            self.fake_dealerships = [
                "Autohaus Sonnenschein", "Werkstatt Blitzblank", "AutoCenter Regenbogen",
                "Motorwelt Sternschnuppe", "Autohaus Glücksklee", "Service-Center Traumwagen",
                "Autopark Wunderland", "Werkstatt Meisterhaft", "AutoPalast König",
                "Fahrzeugwelt Paradies", "Autohaus Goldgrube", "Service-Oase Wüstenfuchs",
                "Motorhof Edelstein", "Autohaus Zeitreise", "Werkstatt Turbozauber",
                "AutoArena Champion", "Servicewelt Premiumglanz", "Autohaus Meilenstein",
                "Werkstatt Schraubenkönig", "Motorreich Vollgas", "Autohaus Freudensprung",
                "Service-Station Rakete", "Autowelt Horizont", "Werkstatt Präzision Plus",
                "Autohaus Vertrauenssache"
            ]
        else:
            self.fake_dealerships = [
                "Autohaus Müller", "Werkstatt Schmidt", "AutoCenter Weber",
                "Motorwelt Fischer", "Autohaus Wagner", "Service-Center Becker",
                "Autopark Schulz", "Werkstatt Hoffmann", "AutoPalast König"
            ]
        
        # Mitarbeiter-Namen (divers und anonym)
        self.fake_employee_names = {
            'male': [
                "Herr Müller", "Herr Schmidt", "Herr Weber", "Herr Fischer", "Herr Meyer",
                "Herr Wagner", "Herr Becker", "Herr Schulz", "Herr Hoffmann", "Herr Schäfer",
                "Herr Koch", "Herr Bauer", "Herr Richter", "Herr Klein", "Herr Wolf"
            ],
            'female': [
                "Frau Schneider", "Frau Neumann", "Frau Schwarz", "Frau Zimmermann", "Frau Braun",
                "Frau Krüger", "Frau Hofmann", "Frau Schmitt", "Frau Lange", "Frau Werner",
                "Frau Schmitz", "Frau Krause", "Frau Meier", "Frau Lehmann", "Frau Köhler"
            ],
            'neutral': [
                "Das Service-Team", "Die Werkstatt-Crew", "Das Beratungsteam", "Die Technikabteilung",
                "Der Kundenservice", "Das Empfangsteam", "Die Serviceberater", "Das Management"
            ]
        }
        
        # Fake Städte/Regionen (kreativ aber realistisch)
        self.fake_cities = [
            "Neustadt", "Altdorf", "Bergheim", "Seestadt", "Waldburg", "Sonnenberg",
            "Rosenheim", "Grünwald", "Steinbach", "Goldbach", "Silbertal", "Kupferberg",
            "Eisenstadt", "Blaubeuren", "Rotenburg", "Weißkirchen", "Schwarzwald",
            "Friedrichshafen", "Wilhelmsburg", "Karlsfeld", "Ludwigshafen", "Marienberg"
        ]
        
        # Anonyme Kunden-IDs
        self.customer_id_prefixes = ["CUST", "KND", "USR", "CLT", "FDB"]
        
    def _initialize_personas(self):
        """Definiert diverse Kunden-Personas für realistische Variation"""
        
        self.personas = {
            'digital_native': PersonaProfile(
                age_group='18-35',
                gender='mixed',
                education_level='high',
                tech_affinity='very_high',
                communication_style='casual',
                typical_concerns=['App', 'Online-Services', 'Geschwindigkeit', 'Transparenz'],
                text_patterns={'short': 0.6, 'medium': 0.3, 'long': 0.1},
                typo_probability=0.15,
                emoji_usage=0.2,
                formality_level=0.3
            ),
            'busy_professional': PersonaProfile(
                age_group='30-50',
                gender='mixed',
                education_level='high',
                tech_affinity='high',
                communication_style='efficient',
                typical_concerns=['Zeit', 'Flexibilität', 'Qualität', 'Verlässlichkeit'],
                text_patterns={'short': 0.3, 'medium': 0.5, 'long': 0.2},
                typo_probability=0.05,
                emoji_usage=0.02,
                formality_level=0.7
            ),
            'experienced_senior': PersonaProfile(
                age_group='60+',
                gender='mixed',
                education_level='mixed',
                tech_affinity='low',
                communication_style='formal',
                typical_concerns=['Beratung', 'Vertrauen', 'Service', 'Preis'],
                text_patterns={'short': 0.1, 'medium': 0.4, 'long': 0.5},
                typo_probability=0.08,
                emoji_usage=0.01,
                formality_level=0.9
            ),
            'family_oriented': PersonaProfile(
                age_group='35-50',
                gender='mixed',
                education_level='mixed',
                tech_affinity='medium',
                communication_style='friendly',
                typical_concerns=['Sicherheit', 'Preis-Leistung', 'Kinderfreundlichkeit', 'Zuverlässigkeit'],
                text_patterns={'short': 0.2, 'medium': 0.6, 'long': 0.2},
                typo_probability=0.1,
                emoji_usage=0.05,
                formality_level=0.5
            ),
            'tech_enthusiast': PersonaProfile(
                age_group='25-45',
                gender='mixed',
                education_level='high',
                tech_affinity='very_high',
                communication_style='technical',
                typical_concerns=['Innovation', 'Features', 'Performance', 'Updates'],
                text_patterns={'short': 0.2, 'medium': 0.5, 'long': 0.3},
                typo_probability=0.03,
                emoji_usage=0.1,
                formality_level=0.6
            ),
            'price_conscious': PersonaProfile(
                age_group='mixed',
                gender='mixed',
                education_level='mixed',
                tech_affinity='medium',
                communication_style='direct',
                typical_concerns=['Kosten', 'Angebote', 'Rabatte', 'Transparenz'],
                text_patterns={'short': 0.4, 'medium': 0.5, 'long': 0.1},
                typo_probability=0.12,
                emoji_usage=0.03,
                formality_level=0.4
            )
        }
        
    def _initialize_markets_and_regions(self):
        """
        Initialisiert Märkte im korrekten Format: Region-Country
        Beispiel: C1-DE, C1-CH, C3-CN, C5-US
        
        Regionen: C1 (Europa), C3 (Asien), C5 (Nordamerika)
        """
        
        # Korrekte Market-Struktur mit Region-Country Format
        self.markets = [
            # C1 - Europa
            'C1-DE',  # Deutschland
            'C1-CH',  # Schweiz
            'C1-IT',  # Italien
            'C1-FR',  # Frankreich
            
            # C3 - Asien
            'C3-CN',  # China
            'C3-KR',  # Korea
            'C3-JP',  # Japan
            
            # C5 - Nordamerika
            'C5-US',  # USA
            'C5-CA',  # Kanada
        ]
        
        # Mapping: Market -> Region & Country
        self.market_mapping = {}
        for market in self.markets:
            parts = market.split('-')
            region = parts[0]
            country = parts[1]
            self.market_mapping[market] = {
                'region': region,
                'country': country
            }
        
        # Regionen-Info
        self.regions = {
            'C1': 'Europa',
            'C3': 'Asien',
            'C5': 'Nordamerika'
        }
        
    def _initialize_text_components(self):
        """Initialisiert Text-Bausteine basierend auf ECHTEN Kundenfeedbacks"""
        
        # MASSIV ERWEITERT - 100+ Variationen statt monotoner "customer states" Phrasen
        self.text_components = {
            'openings': {
                'positiv': [
                    # Direkte Zufriedenheitsäußerungen (20%)
                    "Ich bin sehr zufrieden mit",
                    "Ausgezeichneter Service bei", 
                    "Der Service war einwandfrei bei",
                    "Bin rundum zufrieden mit",
                    "Top Service und kaum Wartezeit bei",
                    "Hervorragend war die Betreuung bei",
                    "Sehr positiv überrascht von",
                    "Kann ich nur empfehlen:",
                    "Perfekt gelaufen ist mein Termin bei",
                    "Absolut zufrieden war ich mit",
                    "Begeistert bin ich von",
                    "Außergewöhnlich gut war der Service bei",
                    "Herausragend fand ich",
                    "Überzeugt hat mich",
                    "Fantastische Erfahrung bei",
                    
                    # Lobende Aussagen (20%)
                    "Der Kunde lobt ausdrücklich",
                    "Positiv hervorgehoben wird",
                    "Besonders gefallen hat dem Kunden",
                    "Der Kunde betont die exzellente Qualität bei",
                    "Zufrieden zeigt sich der Kunde mit",
                    "Der Kunde würde weiterempfehlen:",
                    "Beeindruckt war der Kunde von",
                    "Der Kunde hebt positiv hervor:",
                    "Sehr angetan ist der Kunde von",
                    
                    # Situative Positive (20%)
                    "Bei meinem letzten Besuch bei",
                    "Mein Termin verlief hervorragend bei",
                    "Die Inspektion war bestens organisiert bei",
                    "Alles lief reibungslos bei",
                    "Problemlos und schnell ging es bei",
                    "Überraschend positiv verlief mein Besuch bei",
                    "Sehr angenehm war mein Aufenthalt bei",
                    
                    # Persönliche Empfehlungen (20%)
                    "Ich empfehle definitiv",
                    "Ohne Einschränkung kann ich empfehlen:",
                    "Gerne wieder bei",
                    "Jederzeit wieder zu",
                    "Absolut empfehlenswert ist",
                    "Meine erste Wahl ist",
                    "Von mir 5 Sterne für",
                    
                    # Emotionale Positive (20%)
                    "Ich war begeistert von",
                    "Es freut mich sehr, dass",
                    "Ich bin froh, dass ich mich für",
                    "Sehr dankbar bin ich für",
                    "Toll war es bei"
                ],
                'neutral': [
                    # Sachliche Beschreibungen (40%)
                    "War heute bei",
                    "Hatte einen Termin bei",
                    "War zur Inspektion bei",
                    "Habe mein Fahrzeug gebracht zu",
                    "Meine Erfahrung mit",
                    "War wegen Reifenwechsel bei",
                    "Hatte einen Service-Termin bei",
                    "War zur Wartung bei",
                    "Der Termin fand statt bei",
                    "Gestern war ich bei",
                    "Diese Woche hatte ich einen Termin bei",
                    "Am Montag besuchte ich",
                    "Vergangene Woche war ich bei",
                    "Kürzlich hatte ich einen Termin bei",
                    "Letzte Woche brachte ich mein Fahrzeug zu",
                    
                    # Berichtende Aussagen (30%)
                    "Der Kunde berichtet von seinem Besuch bei",
                    "Laut Aussage des Kunden",
                    "Der Kunde schildert seine Erfahrung mit",
                    "Im Rahmen der Inspektion bei",
                    "Der Kunde beschreibt seinen Termin bei",
                    "Folgende Rückmeldung kam vom Kunden:",
                    "Der Kunde teilt seine Eindrücke von",
                    "Die Kundin berichtet über",
                    
                    # Neutrale Feststellungen (30%)
                    "Mein Eindruck von",
                    "Folgendes ist mir aufgefallen bei",
                    "Im Großen und Ganzen war mein Termin bei",
                    "Grundsätzlich verlief der Besuch bei",
                    "Soweit ich das beurteilen kann, war",
                    "Meine Wahrnehmung bei",
                    "Was mir bei diesem Termin auffiel:"
                ],
                'negativ': [
                    # Enttäuschungsäußerungen (25%)
                    "Leider sehr enttäuschend war mein Termin bei",
                    "Große Probleme gab es bei",
                    "Absolut nicht zufrieden mit",
                    "Katastrophaler Service bei",
                    "Sehr schlechte Erfahrung mit",
                    "Unzumutbar war der Service bei",
                    "Bodenlose Frechheit bei",
                    "Nie wieder",
                    "Stark enttäuscht bin ich von",
                    "Leider muss ich negativ berichten über",
                    "Sehr ärgerlich war mein Besuch bei",
                    "Frustrierend verlief mein Termin bei",
                    
                    # Kritische Aussagen (25%)
                    "Der Kunde kritisiert deutlich",
                    "Unzufrieden äußert sich der Kunde über",
                    "Der Kunde bemängelt",
                    "Kritisch bewertet der Kunde",
                    "Der Kunde beschwert sich über",
                    "Negativ aufgefallen ist dem Kunden bei",
                    "Der Kunde ist verärgert über",
                    "Enttäuscht zeigt sich der Kunde von",
                    
                    # Konkrete Problembeschreibungen (25%)
                    "Folgende Probleme traten auf bei",
                    "Leider verlief nicht alles wie geplant bei",
                    "Mehrere Mängel fielen auf bei",
                    "Nicht zufriedenstellend war bei",
                    "Es gab erhebliche Schwierigkeiten bei",
                    "Ärgerlich war die Situation bei",
                    
                    # Direkte Unzufriedenheit (25%)
                    "Ich bin sehr unzufrieden mit",
                    "Das war inakzeptabel bei",
                    "So geht man nicht mit Kunden um:",
                    "Eine Zumutung war der Besuch bei",
                    "Absolut nicht zu empfehlen:",
                    "Ich werde nicht mehr hingehen zu",
                    "Das war mein letzter Besuch bei",
                    "Unter aller Kanone war"
                ]
            },
            
            # AUS ECHTEN DATEN: Häufige Probleme
            'real_complaints': {
                'wartezeit': [
                    "musste über 2 Stunden warten obwohl Termin vereinbart war",
                    "Wartezeit war viel länger als angekündigt",
                    "statt der versprochenen 30 Minuten wurden es 2 Stunden",
                    "musste 3 Stunden warten für einen einfachen Reifenwechsel",
                    "trotz Termin um 9 Uhr wurde mein Fahrzeug erst um 11 Uhr angenommen",
                    "die angegebene Wartezeit von einer Stunde wurde deutlich überschritten",
                    "wartete über 1,5 Stunden obwohl es hieß maximal 45 Minuten"
                ],
                'kommunikation': [
                    "wurde nicht zurückgerufen wie versprochen",
                    "niemand konnte mir Auskunft geben",
                    "mehrmals angerufen aber nie jemanden erreicht",
                    "die versprochene Rückmeldung kam nie",
                    "musste selbst mehrfach nachfragen",
                    "Informationen waren widersprüchlich",
                    "wurde am Telefon falsch informiert"
                ],
                'service': [
                    "Mitarbeiter war sehr unfreundlich",
                    "fühlte mich nicht willkommen",
                    "wurde von oben herab behandelt",
                    "Personal wirkte genervt und desinteressiert",
                    "Empfang war sehr unfreundlich",
                    "Service-Berater hatte keine Zeit für mich",
                    "wurde einfach stehen gelassen"
                ],
                'werkstatt': [
                    "Problem wurde nicht behoben",
                    "zusätzliche Reparaturen ohne Rücksprache durchgeführt",
                    "Fahrzeug war nicht fertig wie versprochen",
                    "Rechnung war viel höher als Kostenvoranschlag",
                    "Arbeiten wurden nicht korrekt ausgeführt",
                    "musste nochmal kommen weil Fehler gemacht wurde",
                    "versprochene Fahrzeugwäsche wurde vergessen"
                ],
                'kosten': [
                    "Rechnung war doppelt so hoch wie angegeben",
                    "versteckte Kosten die vorher nicht genannt wurden",
                    "musste für Leistungen zahlen die nicht bestellt waren",
                    "Preise sind eine absolute Frechheit",
                    "für 5 Liter Öl 200 Euro ist Wucher",
                    "Stundensatz von 200 Euro ist unverschämt"
                ]
            },
            
            # AUS ECHTEN DATEN: Positive Aspekte
            'real_praise': {
                'service': [
                    "Mitarbeiter war sehr freundlich und kompetent",
                    "wurde sehr gut beraten",
                    "Service-Berater nahm sich viel Zeit",
                    "fühlte mich gut aufgehoben",
                    "Personal war äußerst hilfsbereit",
                    "kompetente und ehrliche Beratung"
                ],
                'werkstatt': [
                    "Arbeit wurde sauber ausgeführt",
                    "Problem wurde schnell gefunden und behoben",
                    "Fahrzeug war pünktlich fertig",
                    "faire Preise und transparente Abrechnung",
                    "Kostenvoranschlag wurde eingehalten"
                ],
                'wartezeit': [
                    "kurze Wartezeit",
                    "ging schneller als erwartet",
                    "konnte direkt warten",
                    "war in 30 Minuten fertig",
                    "keine Wartezeit",
                    "super schnell"
                ]
            },
            
            # ECHTE Schlusssätze aus Ihren Daten
            'closings': {
                'positiv': [
                    "Weiter so!",
                    "Immer wieder gerne!",
                    "Kann ich nur empfehlen.",
                    "Top Service!",
                    "Bin sehr zufrieden.",
                    "5 Sterne!",
                    "Gerne wieder!",
                    "Absolut empfehlenswert!"
                ],
                'neutral': [
                    "War okay.",
                    "Geht so.",
                    "Durchschnittlich.",
                    "Standard.",
                    "In Ordnung.",
                    "Akzeptabel."
                ],
                'negativ': [
                    "Sehr enttäuschend.",
                    "Nicht empfehlenswert.",
                    "Werde die Werkstatt wechseln.",
                    "Nie wieder!",
                    "Katastrophe!",
                    "Absolut inakzeptabel!",
                    "Für mich war es das letzte Mal.",
                    "Werde zu einem anderen Händler gehen."
                ]
            }
        }
        
        # Spezifische Beschwerden/Lob nach Thema
        self.specific_feedback_elements = {
            'Werkstatt': {
                'positiv': [
                    "schnelle Diagnose", "kompetente Mechaniker", "faire Preise",
                    "saubere Arbeit", "termingerechte Fertigstellung", "gute Beratung",
                    "transparente Kostenaufstellung", "professionelle Durchführung"
                ],
                'negativ': [
                    "lange Wartezeiten", "ungenaue Diagnose", "überhöhte Preise",
                    "unsaubere Arbeit", "Termine nicht eingehalten", "schlechte Kommunikation",
                    "versteckte Kosten", "inkompetente Mitarbeiter"
                ]
            },
            'Service': {
                'positiv': [
                    "freundliche Mitarbeiter", "kompetente Beratung", "schnelle Hilfe",
                    "individuelle Lösungen", "zuvorkommend", "hilfsbereit",
                    "professionell", "kundenorientiert"
                ],
                'negativ': [
                    "unfreundliches Personal", "keine Beratung", "lange Wartezeiten",
                    "desinteressiert", "unhöflich", "inkompetent",
                    "nicht erreichbar", "schlechte Einstellung"
                ]
            }
        }
        
    def _initialize_temporal_patterns(self):
        """Definiert zeitliche Muster für realistischere Daten"""
        
        self.temporal_patterns = {
            'seasonal': {
                'winter': {'Werkstatt': 0.3, 'Ersatzfahrzeug': 0.2},  # Mehr Werkstattbesuche
                'summer': {'Terminvergabe': -0.1, 'Service': 0.1},   # Urlaubszeit
                'spring': {'Fahrzeugqualität': 0.2},                  # Neuwagenkäufe
                'autumn': {'Preis-Leistung': 0.15}                    # Jahresend-Angebote
            },
            'weekday': {
                0: -0.1,  # Montag - negativer
                1: 0.0,   # Dienstag
                2: 0.0,   # Mittwoch
                3: 0.05,  # Donnerstag
                4: 0.1,   # Freitag - positiver
                5: 0.05,  # Samstag
                6: -0.05  # Sonntag
            },
            'time_of_day': {
                'morning': {'efficiency': 0.1, 'friendliness': -0.05},
                'noon': {'efficiency': 0.0, 'friendliness': 0.1},
                'afternoon': {'efficiency': -0.05, 'friendliness': 0.05},
                'evening': {'efficiency': -0.1, 'friendliness': -0.1}
            }
        }
        
    def _generate_customer_id(self) -> str:
        """Generiert eine anonyme Kunden-ID"""
        prefix = random.choice(self.customer_id_prefixes)
        numbers = ''.join(random.choices(string.digits, k=6))
        suffix = ''.join(random.choices(string.ascii_uppercase, k=2))
        return f"{prefix}-{numbers}-{suffix}"
        
    def _generate_session_id(self) -> str:
        """Generiert eine Session-ID für Tracking"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_part = ''.join(random.choices(string.hexdigits, k=8))
        return f"SID-{timestamp}-{random_part}"
        
    def _select_persona(self) -> Tuple[str, PersonaProfile]:
        """Wählt eine Persona mit Gewichtung für Diversität"""
        # Gewichtete Auswahl für realistische Verteilung
        weights = {
            'digital_native': 0.25,
            'busy_professional': 0.20,
            'experienced_senior': 0.15,
            'family_oriented': 0.20,
            'tech_enthusiast': 0.10,
            'price_conscious': 0.10
        }
        
        persona_name = random.choices(
            list(weights.keys()),
            weights=list(weights.values())
        )[0]
        
        return persona_name, self.personas[persona_name]
        
    def _apply_persona_style(self, text: str, persona: PersonaProfile) -> str:
        """Wendet Persona-spezifische Sprachmuster an"""
        
        # Formality anpassen
        if persona.formality_level < 0.3:
            # Casual style
            replacements = [
                ("Sehr geehrte", "Hey"),
                ("Mit freundlichen Grüßen", "LG"),
                ("Ich möchte", "Ich will"),
                ("könnten Sie", "könnt ihr")
            ]
            for old, new in replacements:
                text = text.replace(old, new)
                
        elif persona.formality_level > 0.7:
            # Formal style - DIVERSIFIZIERT statt monoton
            if random.random() < 0.15:  # Nur 15% statt immer
                formal_openings = [
                    "Sehr geehrte Damen und Herren, ",
                    "Guten Tag, ",
                    "Hallo, ",
                    "",  # Kein Opening
                ]
                text = random.choice(formal_openings) + text
            if not text.endswith("."):
                text += "."
            # Closings auch variieren
            if random.random() < 0.15:  # Nur 15%
                formal_closings = [
                    " Mit freundlichen Grüßen",
                    " Vielen Dank",
                    " Beste Grüße",
                    ""  # Kein Closing
                ]
                text += random.choice(formal_closings)
            
        # Emojis hinzufügen
        if random.random() < persona.emoji_usage:
            emoji_map = {
                'positiv': ['😊', '👍', '⭐', '✅', '🎉', '💯'],
                'neutral': ['🤔', '😐', '🤷', '📝', '➡️'],
                'negativ': ['😞', '👎', '😠', '❌', '😤', '💔']
            }
            sentiment = self._detect_sentiment(text)
            emoji = random.choice(emoji_map.get(sentiment, ['']))
            text = text + " " + emoji
            
        # Tippfehler hinzufügen
        if random.random() < persona.typo_probability:
            text = self._add_realistic_typos(text)
            
        return text
        
    def _add_realistic_typos(self, text: str) -> str:
        """Fügt realistische Tippfehler hinzu"""
        typo_types = [
            self._swap_adjacent_chars,
            self._duplicate_char,
            self._missing_char,
            self._wrong_case,
            self._common_misspelling
        ]
        
        # 1-3 Fehler pro Text (aber mindestens 10 Wörter nötig)
        words = len(text.split())
        if words < 10:
            return text  # Zu kurz für Typos
            
        num_typos = random.randint(1, min(3, words // 10))
        
        for _ in range(num_typos):
            typo_func = random.choice(typo_types)
            text = typo_func(text)
            
        return text
        
    def _swap_adjacent_chars(self, text: str) -> str:
        """Vertauscht benachbarte Zeichen"""
        words = text.split()
        if words:
            word_idx = random.randint(0, len(words) - 1)
            word = words[word_idx]
            if len(word) > 2:
                char_idx = random.randint(0, len(word) - 2)
                word = word[:char_idx] + word[char_idx+1] + word[char_idx] + word[char_idx+2:]
                words[word_idx] = word
        return ' '.join(words)
        
    def _duplicate_char(self, text: str) -> str:
        """Dupliziert einen Buchstaben"""
        words = text.split()
        if words:
            word_idx = random.randint(0, len(words) - 1)
            word = words[word_idx]
            if len(word) > 1:
                char_idx = random.randint(0, len(word) - 1)
                word = word[:char_idx] + word[char_idx] + word[char_idx:]
                words[word_idx] = word
        return ' '.join(words)
        
    def _missing_char(self, text: str) -> str:
        """Löscht einen Buchstaben"""
        words = text.split()
        if words:
            word_idx = random.randint(0, len(words) - 1)
            word = words[word_idx]
            if len(word) > 2:
                char_idx = random.randint(1, len(word) - 1)
                word = word[:char_idx] + word[char_idx+1:]
                words[word_idx] = word
        return ' '.join(words)
        
    def _wrong_case(self, text: str) -> str:
        """Ändert Groß-/Kleinschreibung"""
        words = text.split()
        if words:
            word_idx = random.randint(0, len(words) - 1)
            words[word_idx] = words[word_idx].lower() if word_idx == 0 else words[word_idx].upper()
        return ' '.join(words)
        
    def _common_misspelling(self, text: str) -> str:
        """Häufige Rechtschreibfehler"""
        common_errors = [
            ("das", "dass"), ("dass", "das"),
            ("seit", "seid"), ("seid", "seit"),
            ("wieder", "wider"), ("wider", "wieder"),
            ("ihr", "Ihr"), ("Ihr", "ihr")
        ]
        for old, new in common_errors:
            if old in text and random.random() < 0.3:
                text = text.replace(old, new, 1)
                break
        return text
        
    def _generate_dynamic_feedback_text(
        self, 
        topic: str, 
        sentiment: str, 
        persona: PersonaProfile,
        subtopic: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> str:
        """
        Generiert dynamischen Feedback-Text basierend auf gelernten Mustern
        MIT REALISTISCHEN TEXTLÄNGEN
        """
        
        # Berechne Ziel-Wortanzahl basierend auf Sentiment
        target_length = self.text_length_controller.get_realistic_length(sentiment)
        
        # Wenn wir aus echten Daten gelernt haben, nutze diese Muster
        if self.learned_patterns and random.random() < 0.7:  # 70% basiert auf echten Daten
            text = self._generate_from_learned_patterns(topic, sentiment, persona)
        else:
            # Basis-Struktur aufbauen
            components = []
            
            # Opening
            opening = random.choice(self.text_components['openings'][sentiment])
            
            # Werkstatt-Name einfügen
            dealership = random.choice(self.fake_dealerships)
            opening = opening + f" {dealership}"
            components.append(opening)
            
            # Hauptteil - ERWEITERT für realistische Längen
            main_points = []
            
            # Verwende echte Phrasen aus den Daten
            if sentiment == 'negativ' and 'real_complaints' in self.text_components:
                # Wähle eine Kategorie von Beschwerden
                complaint_category = random.choice(list(self.text_components['real_complaints'].keys()))
                complaint = random.choice(self.text_components['real_complaints'][complaint_category])
                main_points.append(complaint)
                
            elif sentiment == 'positiv' and 'real_praise' in self.text_components:
                # Wähle Lob-Kategorie
                praise_category = random.choice(list(self.text_components['real_praise'].keys()))
                praise = random.choice(self.text_components['real_praise'][praise_category])
                main_points.append(praise)
                
            # Füge weitere Details hinzu um Ziellänge zu erreichen
            current_length = len(' '.join(components + main_points).split())
            
            # Detaillierte Elemente für längere Texte
            while current_length < target_length * 0.8:  # Mindestens 80% der Ziellänge
                detail_options = []
                
                # Mitarbeiter-Erwähnung
                if random.random() < 0.5:
                    gender = random.choice(['male', 'female', 'neutral'])
                    employee = random.choice(self.fake_employee_names[gender])
                    if sentiment == 'positiv':
                        details = [
                            f"{employee} war sehr kompetent und freundlich",
                            f"Besonders {employee} hat sich sehr bemüht",
                            f"Die Beratung durch {employee} war erstklassig"
                        ]
                    elif sentiment == 'negativ':
                        details = [
                            f"{employee} war leider nicht hilfreich",
                            f"Von {employee} fühlte ich mich nicht ernst genommen",
                            f"Die Kommunikation mit {employee} verlief enttäuschend"
                        ]
                    else:
                        details = [
                            f"{employee} hat mich betreut",
                            f"Mein Ansprechpartner war {employee}"
                        ]
                    detail_options.extend(details)
                
                # Zeitangaben
                if random.random() < 0.4:
                    detail_options.extend([
                        f"Die Wartezeit betrug etwa {random.randint(15, 180)} Minuten",
                        f"Ich hatte meinen Termin um {random.randint(8, 17)}:00 Uhr",
                        f"Der gesamte Vorgang dauerte {random.choice(['länger als erwartet', 'wie versprochen', 'überraschend kurz'])}"
                    ])
                
                # Topic-spezifische Details
                if topic and random.random() < 0.6:
                    detail_options.extend([
                        f"Es ging um {topic.lower()}",
                        f"Bezüglich {topic.lower()} hatte ich einige Fragen",
                        f"Der {topic.lower()}-Service wurde durchgeführt"
                    ])
                
                # Wähle ein Detail
                if detail_options:
                    main_points.append(random.choice(detail_options))
                    current_length = len(' '.join(components + main_points).split())
                else:
                    break  # Keine weiteren Details verfügbar
            
            # Mitarbeiter erwähnen (falls noch nicht geschehen)
            if random.random() < 0.3 and current_length < target_length:
                gender = random.choice(['male', 'female', 'neutral'])
                employee = random.choice(self.fake_employee_names[gender])
                if sentiment == 'positiv':
                    main_points.append(f"{employee} war sehr kompetent")
                elif sentiment == 'negativ':
                    main_points.append(f"{employee} war leider nicht hilfreich")
                    
            # Zusammenfügen
            if main_points:
                main_text = ". ".join(main_points)
            else:
                main_text = ""
                
            # Closing
            closing = random.choice(self.text_components['closings'][sentiment])
            
            # Vollständiger Text
            text = opening + ". " + main_text + ". " + closing
        
        # Persona-Style anwenden (NACH Längen-Anpassung)
        text = self._apply_persona_style(text, persona)
        
        return text.strip()
    
    def _generate_from_learned_patterns(
        self, 
        topic: str, 
        sentiment: str, 
        persona: PersonaProfile
    ) -> str:
        """
        Generiert Text basierend auf gelernten Mustern aus echten Daten
        """
        
        # Wähle eine Werkstatt
        dealership = random.choice(self.fake_dealerships)
        
        # Basis-Opening
        opening = f"Mein Termin bei {dealership}"
        
        # Hauptteil aus gelernten Mustern
        main_parts = []
        
        if sentiment == 'negativ':
            # Nutze gelernte Probleme
            if 'phrase_patterns' in self.learned_patterns:
                categories = ['wartezeit', 'service', 'kommunikation', 'werkstatt', 'kosten']
                chosen_categories = random.sample(categories, min(2, len(categories)))
                
                for category in chosen_categories:
                    if category in self.learned_patterns['phrase_patterns']:
                        patterns = self.learned_patterns['phrase_patterns'][category]
                        if patterns:
                            phrase = random.choice(patterns)
                            # Ersetze Platzhalter mit Fake-Daten
                            phrase = phrase.replace('XX:XX', f"{random.randint(8,18)}:{random.choice(['00','15','30','45'])}")
                            phrase = phrase.replace('XXXXX', str(random.randint(100, 2000)))
                            main_parts.append(phrase)
                            
            # Füge häufige Probleme hinzu
            if 'common_issues' in self.learned_patterns and self.learned_patterns['common_issues']:
                issue = random.choice(self.learned_patterns['common_issues'])
                main_parts.append(f"Das Hauptproblem war: {issue}")
                
        elif sentiment == 'positiv':
            # Positive Aspekte
            positive_aspects = [
                "Der Service war ausgezeichnet",
                "Sehr kompetente Beratung",
                "Faire Preise",
                "Schnelle Abwicklung",
                "Freundliches Personal"
            ]
            main_parts.extend(random.sample(positive_aspects, 2))
            
        # Text zusammensetzen
        if main_parts:
            main_text = ". ".join(main_parts)
        else:
            main_text = "war durchschnittlich"
            
        # Abschluss basierend auf Sentiment
        if sentiment == 'negativ':
            closing = random.choice([
                "Werde die Werkstatt wechseln",
                "Sehr enttäuschend",
                "Nicht empfehlenswert",
                "Das war das letzte Mal"
            ])
        elif sentiment == 'positiv':
            closing = random.choice([
                "Immer wieder gerne",
                "Kann ich nur empfehlen",
                "Top Service",
                "Weiter so"
            ])
        else:
            closing = "War okay"
            
        # Vollständiger Text
        full_text = f"{opening}. {main_text}. {closing}."
        
        # Persona-Anpassungen
        full_text = self._apply_persona_style(full_text, persona)
        
        return full_text
        
    def _detect_sentiment(self, text: str) -> str:
        """Einfache Sentiment-Erkennung basierend auf Keywords"""
        positive_keywords = ['gut', 'super', 'toll', 'perfekt', 'zufrieden', 'empfehlen']
        negative_keywords = ['schlecht', 'enttäuscht', 'mangelhaft', 'problem', 'unzufrieden']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_keywords if word in text_lower)
        neg_count = sum(1 for word in negative_keywords if word in text_lower)
        
        if pos_count > neg_count:
            return 'positiv'
        elif neg_count > pos_count:
            return 'negativ'
        else:
            return 'neutral'
            
    def _apply_temporal_effects(
        self, 
        date: datetime, 
        sentiment_score: float,
        topic: str
    ) -> float:
        """Wendet zeitliche Effekte auf Sentiment an"""
        
        # Saisonale Effekte
        month = date.month
        if month in [12, 1, 2]:  # Winter
            season = 'winter'
        elif month in [3, 4, 5]:  # Frühling
            season = 'spring'
        elif month in [6, 7, 8]:  # Sommer
            season = 'summer'
        else:  # Herbst
            season = 'autumn'
            
        if topic in self.temporal_patterns['seasonal'][season]:
            sentiment_score += self.temporal_patterns['seasonal'][season][topic]
            
        # Wochentag-Effekt
        weekday = date.weekday()
        sentiment_score += self.temporal_patterns['weekday'][weekday]
        
        # Tageszeit-Effekt (simuliert)
        hour = random.randint(8, 20)
        if hour < 12:
            time_effect = self.temporal_patterns['time_of_day']['morning']['friendliness']
        elif hour < 14:
            time_effect = self.temporal_patterns['time_of_day']['noon']['friendliness']
        elif hour < 18:
            time_effect = self.temporal_patterns['time_of_day']['afternoon']['friendliness']
        else:
            time_effect = self.temporal_patterns['time_of_day']['evening']['friendliness']
            
        sentiment_score += time_effect * 0.1
        
        # Normalisieren auf [-1, 1]
        return max(-1, min(1, sentiment_score))
        
    def _calculate_realistic_nps_sentiment_correlation(
        self,
        nps_score: int,
        persona: PersonaProfile
    ) -> str:
        """Berechnet realistisches Sentiment mit Persona-Einfluss"""
        
        # Basis-Wahrscheinlichkeiten
        if nps_score >= 9:  # Promoter
            base_probs = {'positiv': 0.7, 'neutral': 0.25, 'negativ': 0.05}
        elif nps_score <= 6:  # Detractor
            base_probs = {'positiv': 0.05, 'neutral': 0.25, 'negativ': 0.7}
        else:  # Passive
            base_probs = {'positiv': 0.2, 'neutral': 0.6, 'negativ': 0.2}
            
        # Persona-Anpassungen (mit Clipping um negative Werte zu vermeiden)
        if persona.communication_style == 'critical':
            base_probs['negativ'] = min(0.9, base_probs['negativ'] + 0.1)
            base_probs['positiv'] = max(0.0, base_probs['positiv'] - 0.1)
        elif persona.communication_style == 'friendly':
            base_probs['positiv'] = min(0.9, base_probs['positiv'] + 0.1)
            base_probs['negativ'] = max(0.0, base_probs['negativ'] - 0.1)
            
        # Normalisieren und sicherstellen dass alle Werte >= 0 sind
        for key in base_probs:
            base_probs[key] = max(0.0, base_probs[key])
        
        total = sum(base_probs.values())
        if total == 0:
            total = 1  # Fallback
        probs = [base_probs[s]/total for s in self.sentiments]
        
        return np.random.choice(self.sentiments, p=probs)
        
    def generate_enterprise_dataset(
        self,
        n_samples: int = 5000,
        start_date: str = '2020-01-01',
        end_date: str = '2024-12-31',
        ensure_diversity: bool = True,
        include_metadata: bool = True
    ) -> pd.DataFrame:
        """
        Generiert Enterprise-Grade synthetische Daten
        
        Args:
            n_samples: Anzahl Datensätze
            start_date: Start-Datum
            end_date: End-Datum
            ensure_diversity: Erzwinge Diversität
            include_metadata: Füge Metadaten hinzu
            
        Returns:
            DataFrame mit synthetischen Daten
        """
        
        print(f">> Generiere {n_samples} synthetische Datensaetze...")
        if ensure_diversity:
            print("   >> Aktiviere Diversitaets-Kontrolle...")
        print("   >> Anonymisierung aktiv...")
        
        data = []
        
        # Datum-Range
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        date_range = (end - start).days
        
        # Diversitäts-Kontrolle - initialisiere Cycles (auch wenn nicht verwendet)
        personas_cycle = itertools.cycle(self.personas.keys())
        markets_cycle = itertools.cycle(self.markets)  # Verwende neue markets Liste
        topics_cycle = itertools.cycle(list(self.topics_hierarchy.keys()))
            
        for i in range(n_samples):
            # Progress indicator
            if i % 500 == 0 and i > 0:
                print(f"   >> {i}/{n_samples} Datensaetze generiert...")
                
            # Persona wählen
            if ensure_diversity:
                persona_name = next(personas_cycle)
                persona = self.personas[persona_name]
            else:
                persona_name, persona = self._select_persona()
                
            # NPS Score - MIT GEWICHTEN aus Analyse (16.8% / 27.4% / 55.8%)
            nps_category = np.random.choice(
                list(self.nps_weights.keys()),
                p=list(self.nps_weights.values())
            )
            nps_score = random.choice(self.nps_distribution[nps_category])
            
            # Market - KORREKTES FORMAT: Region-Country
            if ensure_diversity:
                market = next(markets_cycle)
            else:
                market = random.choice(self.markets)
            
            # Extrahiere Region und Country aus Market
            market_info = self.market_mapping[market]
            region = market_info['region']
            country = market_info['country']
                
            # Datum mit realistischer Verteilung
            # Mehr aktuelle Daten
            if random.random() < 0.3:  # 30% aus letztem Quartal
                days_ago = random.randint(0, 90)
            else:
                days_ago = random.randint(0, date_range)
            feedback_date = end - timedelta(days=days_ago)
            
            # Topic und Subtopic
            if ensure_diversity:
                topic = next(topics_cycle)
            else:
                topic = random.choice(list(self.topics_hierarchy.keys()))
            
            # NEU: Handle neue Topic-Struktur mit 'subtopics' und 'weight'
            topic_data = self.topics_hierarchy.get(topic, {})
            if isinstance(topic_data, dict):
                subtopics_list = topic_data.get('subtopics', [])
            else:
                # Fallback für alte Struktur
                subtopics_list = topic_data if isinstance(topic_data, list) else []
            
            subtopic = random.choice(subtopics_list) if subtopics_list else None
            
            # Sentiment (realistisch korreliert mit NPS)
            sentiment = self._calculate_realistic_nps_sentiment_correlation(
                nps_score, persona
            )
            
            # Generiere Text
            verbatim = self._generate_dynamic_feedback_text(
                topic, sentiment, persona, subtopic
            )
            
            # Sentiment Score berechnen
            base_sentiment_score = {
                'positiv': np.random.uniform(0.5, 1.0),
                'neutral': np.random.uniform(-0.2, 0.5),
                'negativ': np.random.uniform(-1.0, -0.3)
            }[sentiment]
            
            # Zeitliche Effekte anwenden
            sentiment_score = self._apply_temporal_effects(
                feedback_date, base_sentiment_score, topic
            )
            
            # Metadaten
            record = {
                # Kern-Daten
                'feedback_id': self._generate_session_id(),
                'customer_id': self._generate_customer_id(),
                'NPS': nps_score,
                'nps_category': nps_category,
                'Market': market,
                'Date': feedback_date.strftime('%Y-%m-%dT%H:%M:%S+00:00'),
                'Verbatim': verbatim,
                
                # Erweiterte Daten - verwende bereits extrahierte Werte
                'region': region,
                'country': country,
                'topic': topic,
                'subtopic': subtopic,
                'sentiment_label': sentiment,
                'sentiment_score': round(sentiment_score, 4),
                
                # Text-Metriken
                'Verbatim_token_count': len(verbatim.split()),
                'Verbatim_char_count': len(verbatim),
                
                # Tracking
                'dealership': random.choice(self.fake_dealerships),
                'response_channel': random.choice(['Online', 'Email', 'App', 'Phone', 'In-Person']),
                'survey_type': random.choice(['Post-Service', 'Annual', 'Transaction', 'Complaint']),
                
                # Quality Flags
                'is_synthetic': True,  # Wichtig für Mixing mit echten Daten
                'synthetic_version': '2.0',
                'generation_timestamp': datetime.now().isoformat()
            }
            
            # Zusätzliche Metadaten wenn gewünscht
            if include_metadata:
                record.update({
                    'persona_type': persona_name,
                    'age_group': persona.age_group,
                    'tech_affinity': persona.tech_affinity,
                    'communication_style': persona.communication_style,
                    'topic_confidence': round(random.uniform(0.3, 1.0), 2),
                    'response_time_seconds': random.randint(30, 600),
                    'device_type': random.choice(['Desktop', 'Mobile', 'Tablet']),
                    'browser': random.choice(['Chrome', 'Safari', 'Firefox', 'Edge']),
                    'city': random.choice(self.fake_cities)
                })
                
            data.append(record)
            
        df = pd.DataFrame(data)
        
        # Sortiere nach Datum
        df = df.sort_values('Date').reset_index(drop=True)
        
        print(f">> Erfolgreich {len(df)} Datensaetze generiert!")
        
        # Qualitätskontrolle
        self._run_quality_checks(df)
        
        return df
        
    def _run_quality_checks(self, df: pd.DataFrame):
        """Führt Qualitätschecks durch"""
        print("\n>> Qualitaetskontrolle:")
        
        # Check 1: Diversität
        unique_verbatims = df['Verbatim'].nunique()
        diversity_score = unique_verbatims / len(df)
        print(f"   >> Text-Diversitaet: {diversity_score:.2%} unique")
        
        # Check 2: Balance
        nps_balance = df['nps_category'].value_counts(normalize=True)
        print(f"   ✓ NPS-Balance: {nps_balance.to_dict()}")
        
        # Check 3: Sentiment-Korrelation
        correlation = df['NPS'].corr(df['sentiment_score'])
        print(f"   ✓ NPS-Sentiment Korrelation: {correlation:.3f}")
        
        # Check 4: Market-Verteilung
        market_distribution = df['Market'].value_counts()
        cv = market_distribution.std() / market_distribution.mean()
        print(f"   ✓ Market-Gleichverteilung CV: {cv:.3f} (niedriger=besser)")
        
        # Check 5: Keine leeren Werte
        null_check = df.isnull().sum().sum()
        print(f"   ✓ Fehlende Werte: {null_check}")
        
        if diversity_score < 0.8:
            print("   ⚠️  Warnung: Text-Diversität unter 80%")
        if cv > 0.5:
            print("   ⚠️  Warnung: Market-Verteilung ungleichmäßig")
            
    def analyze_bias_advanced(self, df: pd.DataFrame) -> Dict:
        """Erweiterte Bias-Analyse mit statistischen Tests"""
        
        from scipy import stats
        
        print("\n📈 Erweiterte Bias-Analyse läuft...")
        
        analysis = {
            'basic_distributions': {
                'nps': df['NPS'].value_counts().to_dict(),
                'sentiment': df['sentiment_label'].value_counts(normalize=True).to_dict(),
                'topics': df['topic'].value_counts(normalize=True).to_dict()
            },
            'statistical_tests': {},
            'diversity_metrics': {},
            'bias_indicators': {}
        }
        
        # Chi-Quadrat Tests für Unabhängigkeit
        categorical_pairs = [
            ('Market', 'sentiment_label'),
            ('Market', 'nps_category'),
            ('topic', 'sentiment_label')
        ]
        
        for var1, var2 in categorical_pairs:
            try:
                contingency_table = pd.crosstab(df[var1], df[var2])
                chi2_stat, p_val, _, _ = stats.chi2_contingency(contingency_table)
                chi2_stat = float(chi2_stat)
                p_val = float(p_val)
                
                analysis['statistical_tests'][f'{var1}_vs_{var2}'] = {
                    'chi2': round(chi2_stat, 4),
                    'p_value': round(p_val, 4),
                    'independent': p_val > 0.05,
                    'interpretation': 'Variables are independent' if p_val > 0.05 else 'Significant dependency detected'
                }
            except Exception as e:
                analysis['statistical_tests'][f'{var1}_vs_{var2}'] = {
                    'error': str(e)
                }
            
        # Shannon Entropy für Diversität
        from scipy.stats import entropy
        
        for column in ['Market', 'topic', 'sentiment_label']:
            value_counts = df[column].value_counts(normalize=True)
            shannon_entropy = entropy(value_counts)
            max_entropy = np.log(len(value_counts))
            normalized_entropy = shannon_entropy / max_entropy if max_entropy > 0 else 0
            
            analysis['diversity_metrics'][column] = {
                'shannon_entropy': round(float(shannon_entropy), 4),
                'normalized_entropy': round(float(normalized_entropy), 4),
                'interpretation': 'High diversity' if normalized_entropy > 0.8 else 'Low diversity'
            }
            
        # Bias Indicators
        # Gender representation in employee names (wenn vorhanden)
        if 'Verbatim' in df.columns:
            male_mentions = df['Verbatim'].str.contains('Herr', case=False).sum()
            female_mentions = df['Verbatim'].str.contains('Frau', case=False).sum()
            
            total_gendered = male_mentions + female_mentions
            if total_gendered > 0:
                analysis['bias_indicators']['gender_balance'] = {
                    'male_ratio': round(male_mentions / total_gendered, 3),
                    'female_ratio': round(female_mentions / total_gendered, 3),
                    'balanced': abs(0.5 - male_mentions/total_gendered) < 0.1
                }
                
        return analysis


def main():
    """Hauptfunktion mit erweiterten Features"""
    
    print("="*60)
    print("🚀 ENTERPRISE SYNTHETIC FEEDBACK GENERATOR v2.0")
    print("="*60)
    
    # Initialisierung
    generator = AdvancedSyntheticFeedbackGenerator(seed=42, enable_fun_mode=True)
    
    # Generiere große Datenmenge
    print("\n📊 Phase 1: Generierung großer Datenmenge")
    df_large = generator.generate_enterprise_dataset(
        n_samples=5000,
        start_date='2022-01-01',
        end_date='2024-12-31',
        ensure_diversity=True,
        include_metadata=True
    )
    
    # Erweiterte Analyse
    print("\n📊 Phase 2: Erweiterte Bias-Analyse")
    bias_analysis = generator.analyze_bias_advanced(df_large)
    
    print("\n📈 Analyse-Ergebnisse:")
    print(f"   • Sentiment-Verteilung: {bias_analysis['basic_distributions']['sentiment']}")
    
    for test, result in bias_analysis['statistical_tests'].items():
        print(f"   • {test}: {result['interpretation']} (p={result['p_value']:.4f})")
        
    for metric, result in bias_analysis['diversity_metrics'].items():
        print(f"   • {metric} Diversität: {result['interpretation']} (Entropy={result['normalized_entropy']:.2f})")
    
    # Beispiel-Output
    print("\n📄 Beispiel-Datensätze:")
    print("="*60)
    
    # Zeige verschiedene Personas
    for persona_type in ['digital_native', 'experienced_senior', 'busy_professional']:
        sample = df_large[df_large['persona_type'] == persona_type].iloc[0]
        print(f"\n👤 Persona: {persona_type}")
        print(f"   NPS: {sample['NPS']} ({sample['nps_category']})")
        print(f"   Topic: {sample['topic']} - {sample['subtopic']}")
        print(f"   Sentiment: {sample['sentiment_label']} ({sample['sentiment_score']:.2f})")
        print(f"   Werkstatt: {sample['dealership']}")
        print(f"   Feedback: \"{sample['Verbatim'][:150]}...\"")
    
    print("\n="*60)
    print("✅ GENERIERUNG ERFOLGREICH ABGESCHLOSSEN!")
    print(f"   • {len(df_large)} Datensätze generiert")
    print(f"   • {df_large['Verbatim'].nunique()} unique Texte")
    print(f"   • {df_large['dealership'].nunique()} verschiedene Werkstätten")
    print("="*60)


if __name__ == "__main__":
    main()