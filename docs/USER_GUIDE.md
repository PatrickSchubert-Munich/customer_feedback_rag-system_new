# 📘 User Guide - Customer Feedback RAG System

> Vollständige Anleitung für Endbenutzer

---

## 📖 Inhaltsverzeichnis

1. [Einführung](#-einführung)
2. [Erste Schritte](#-erste-schritte)
3. [Die Benutzeroberfläche](#-die-benutzeroberfläche)
4. [Features & Funktionen](#-features--funktionen)
5. [Beispielanfragen](#-beispielanfragen)
6. [Best Practices](#-best-practices)
7. [Häufig gestellte Fragen (FAQ)](#-häufig-gestellte-fragen-faq)
8. [Tipps & Tricks](#-tipps--tricks)
9. [Fehlerbehebung](#-fehlerbehebung)

---

## 🎯 Einführung

### Was ist das Customer Feedback RAG System?

Das **Customer Feedback RAG System** ist eine intelligente Anwendung, die künstliche Intelligenz nutzt, um Kundenfeedback automatisch zu analysieren. Das System kann:

- 🔍 **Feedback durchsuchen** nach bestimmten Themen oder Problemen
- 📊 **Visualisierungen erstellen** (Diagramme, Charts)
- 📈 **Trends erkennen** über Zeit, Märkte und Kategorien
- 💡 **Insights liefern** aus tausenden von Kundenmeinungen

### Für wen ist dieses System?

- **Customer Experience Manager** - Verstehen Sie Ihre Kunden besser
- **Product Manager** - Erkennen Sie Produktprobleme frühzeitig
- **Marketing Teams** - Analysieren Sie Sentiment und NPS
- **Support Teams** - Identifizieren Sie häufige Beschwerden
- **Executives** - Erhalten Sie schnelle Übersichten und Dashboards

### Was macht das System besonders?

✨ **Intelligente KI-Agents**

- Multi-Agent-Architektur mit spezialisierten KI-Assistenten
- Automatische Weiterleitung an den richtigen Experten
- Natürliche Konversation in deutscher Sprache

🚀 **Schnelle Antworten**

- Metadaten-Abfragen in Millisekunden
- Semantische Suche mit Vektordatenbank
- Echtzeit-Streaming der Antworten

📊 **Professionelle Visualisierungen**

- 10+ verschiedene Chart-Typen
- Automatische Datenvisualisierung
- Export-fähige PNG-Dateien

---

## 🚀 Erste Schritte

### Voraussetzungen

Bevor Sie beginnen, stellen Sie sicher, dass die Applikation läuft:

- Installation abgeschlossen (siehe [QUICK_START.md](../QUICK_START.md))
- Browser öffnet automatisch `http://localhost:8501`
- Willkommensnachricht ist sichtbar

### Die erste Anfrage

1. **Warten Sie auf die Bereitschaft**

   ```
   ✅ VectorStore bereit!
   💬 Stellen Sie mir eine Frage...
   ```

2. **Wählen Sie eine Beispielanfrage**

   - In der Sidebar finden Sie 5 vorbereitete Beispiele
   - Klicken Sie auf eine Frage
   - Die Frage wird automatisch gesendet

3. **Oder geben Sie eine eigene Frage ein**
   - Schreiben Sie in das Chat-Eingabefeld
   - Drücken Sie Enter oder klicken Sie "Send"
   - Warten Sie auf die Antwort (Streaming)

### Beispiel-Workflow

**Einfache Metadaten-Abfrage:**

```
Sie: "Wie ist die NPS-Verteilung in deinem Datensatz?"

System: Antwortet sofort mit Statistiken:
        - Anzahl Promoter/Passive/Detractor
        - NPS-Durchschnitt
        - Prozentuale Verteilung
```

**Komplexe Analyse mit Chart:**

```
Sie: "Erstelle ein Balkendiagramm der Top 5 Themen mit NPS-Scores"

System:
1. Analysiert die Anfrage
2. Erstellt das Diagramm
3. Zeigt das Bild im Chat
4. Liefert textuelle Zusammenfassung
```

---

## 💻 Die Benutzeroberfläche

### Hauptbereiche

```
┌─────────────────────────────────────────────────────────┐
│  HEADER                                                 │
│  🤖 Customer Feedback RAG System                        │
│  [Logo] [Titel] [Subtitle]                             │
├──────────┬──────────────────────────────────────────────┤
│          │  CHAT-BEREICH                                │
│ SIDEBAR  │  ┌────────────────────────────────────────┐ │
│          │  │ Willkommensnachricht                   │ │
│ • Stats  │  │ (beim ersten Laden)                    │ │
│ • Fragen │  └────────────────────────────────────────┘ │
│ • Charts │                                              │
│ • Optionen│  ┌────────────────────────────────────────┐│
│ • History│  │ 👤 User: Ihre Frage                    ││
│          │  └────────────────────────────────────────┘│
│          │                                              │
│          │  ┌────────────────────────────────────────┐│
│          │  │ 🤖 Assistant: Antwort                  ││
│          │  │                                        ││
│          │  │ [Chart wird hier angezeigt]            ││
│          │  └────────────────────────────────────────┘│
│          │                                              │
│          │  ┌────────────────────────────────────────┐│
│          │  │ 💬 Ihre Frage eingeben...      [Send]  ││
│          │  └────────────────────────────────────────┘│
├──────────┴──────────────────────────────────────────────┤
│  FOOTER                                                 │
│  Made with ❤️ and 🤖 AI                                │
└─────────────────────────────────────────────────────────┘
```

### Sidebar-Funktionen

**📊 Konversations-Statistiken**

- Anzahl der Nachrichten
- Genutzte Tokens
- Durchschnittliche Antwortzeit

**💡 Beispiel-Anfragen**

- 5 vordefinierte Fragen
- Klickbar zum direkten Senden
- Decken verschiedene Features ab

**🖼️ Chart-Größe**

- Klein, Mittel, Groß
- Wählen Sie die bevorzugte Darstellung
- Gilt für neu erstellte Charts

**🧹 Chart-Bereinigung**

- Automatisches Löschen alter Charts
- Spart Speicherplatz
- Ein/Ausschalten möglich

**🔄 Neue Konversation**

- Löscht Chat-Historie
- Startet frische Session
- Behält VectorStore bei

### Chat-Bereich

**Nachrichten-Typen:**

1. **User-Nachrichten** (👤)

   - Ihre Fragen und Anfragen
   - In blauem Container

2. **Assistant-Nachrichten** (🤖)

   - Antworten des Systems
   - Streaming (Wort für Wort)
   - Kann Charts enthalten

3. **System-Nachrichten** (ℹ️)
   - Statusmeldungen
   - Warnungen
   - Fehler

---

## ⚙️ Features & Funktionen

### 1. Metadaten-Abfragen

**Was sind Metadaten?**

- Statistische Übersichten über den Datensatz
- Schnelle Antworten ohne Tool-Aufrufe
- Bereits beim Start vorberechnet

**Verfügbare Metadaten:**

- 📊 NPS-Verteilung (Promoter, Passive, Detractor)
- 😊 Sentiment-Statistiken (positiv, neutral, negativ)
- 🌍 Märkte und Länder im Datensatz
- 📅 Zeitraum der Feedbacks
- 🔢 Anzahl der Einträge
- 💬 Token-Statistiken

**Beispiel-Fragen:**

```
"Wie ist die NPS-Verteilung?"
"Welche Märkte sind enthalten?"
"Wie viele Feedbacks gibt es?"
"Was ist der Zeitraum der Daten?"
"Wie ist die Sentiment-Verteilung?"
```

---

### 2. Semantische Feedback-Suche

**Was ist semantische Suche?**

- KI versteht die Bedeutung Ihrer Frage
- Nicht nur Keyword-Matching
- Findet relevante Feedbacks auch mit anderen Wörtern

**Such-Parameter:**

| Parameter            | Beschreibung             | Beispiel                           |
| -------------------- | ------------------------ | ---------------------------------- |
| **Query**            | Suchbegriff (semantisch) | "Lieferprobleme"                   |
| **max_results**      | Anzahl Ergebnisse (3-30) | 10 (Standard)                      |
| **market_filter**    | Markt-ID                 | "C1-DE"                            |
| **country_filter**   | Land (ISO-Code)          | "DE", "IT", "FR"                   |
| **region_filter**    | Region                   | "C1", "CE"                         |
| **sentiment_filter** | Sentiment                | "positiv", "negativ", "neutral"    |
| **nps_filter**       | NPS-Kategorie            | "Promoter", "Detractor", "Passive" |
| **topic_filter**     | Thema                    | "Service", "Lieferproblem"         |
| **date_from/to**     | Zeitraum                 | "2023-01-01" bis "2023-12-31"      |

**Beispiel-Fragen:**

_Einfache Suche:_

```
"Was sind die Top 5 Beschwerden?"
"Zeige mir Feedback zu Lieferproblemen"
"Welche positiven Erfahrungen gibt es?"
```

_Mit Filtern:_

```
"Negative Feedbacks aus Deutschland"
"Top 3 Beschwerden von Detractoren"
"Positive Reviews aus Italien im Q1 2023"
"Service-Probleme in der C1-Region"
```

_Top-N Analysen:_

```
"Top 5 Themen"         → max_results=5
"Erste 3 Probleme"     → max_results=3
"Zeige mir 12 Reviews" → max_results=12
```

**Was Sie erhalten:**

- Liste relevanter Feedbacks
- Metadaten zu jedem Feedback (NPS, Sentiment, Market, etc.)
- Zusammenfassung und Insights
- Business-Report Formatierung

---

### 3. Datenvisualisierung

**Verfügbare Chart-Typen:**

#### 📊 Sentiment Charts

- **sentiment_bar_chart** - Sentiment-Verteilung als Balkendiagramm
- **sentiment_pie_chart** - Sentiment-Verteilung als Kreisdiagramm

```
"Erstelle ein Sentiment-Balkendiagramm"
"Zeige Sentiment als Tortendiagramm"
```

#### 🎯 NPS Charts

- **nps_bar_chart** - NPS-Kategorien als Balkendiagramm
- **nps_pie_chart** - NPS-Verteilung als Kreisdiagramm

```
"Erstelle ein NPS-Balkendiagramm"
"Zeige NPS-Verteilung als Pie-Chart"
```

#### 🌍 Market Charts

- **market_bar_chart** - Feedback-Anzahl pro Markt
- **market_pie_chart** - Markt-Verteilung als Kreisdiagramm
- **market_sentiment_breakdown** - Sentiment pro Markt
- **market_nps_breakdown** - NPS pro Markt

```
"Zeige Feedback-Verteilung nach Märkten"
"Wie ist das Sentiment in verschiedenen Märkten?"
"NPS-Vergleich zwischen Ländern"
```

#### 🏷️ Topic Charts

- **topic_bar_chart** - Themen-Verteilung
- **topic_pie_chart** - Themen als Kreisdiagramm

```
"Zeige Top 5 Themen"
"Welche Themen sind am häufigsten?"
"Erstelle eine Themen-Übersicht"
```

#### 🏢 Dealership Charts

- **dealership_bar_chart** - Erwähnungen von Händlern

```
"Welche Händler werden am meisten erwähnt?"
"Top 5 Dealerships nach Erwähnungen"
```

#### 📅 Time Analysis

- **time_analysis** - Zeitreihen-Analyse (4 Subplots)
  - Feedback-Volumen über Zeit
  - Sentiment-Entwicklung
  - NPS-Trend
  - Topic-Verteilung

```
"Zeige Entwicklung über die letzten 7 Monate"
"Erstelle eine Zeitreihen-Analyse"
"Wie hat sich das Sentiment entwickelt?"
```

#### 📈 Overview Dashboard

- **overview** - Umfassendes Dashboard (6 Metriken)

```
"Erstelle ein Dashboard"
"Zeige mir eine Gesamtübersicht"
```

**Chart-Größen:**

- **Klein** - Kompakt, für schnelle Übersicht
- **Mittel** - Standard, ausgewogen
- **Groß** - Vollbild, für Präsentationen

**Chart-Steuerung:**

```
Sidebar → 🖼️ Chart-Größe wählen
         → 🧹 Auto-Bereinigung an/aus
```

---

### 4. Konversations-Historie

**Funktionen:**

- ✅ Persistente Historie während Session
- ✅ Context-Awareness (System erinnert sich)
- ✅ Historie-Limit (Token-Optimierung)
- ✅ Manuelle Löschung möglich

**Verwendung:**

```
Sie: "Zeige negative Feedbacks"
     [System liefert Ergebnisse]

Sie: "Und wie sieht es bei Promotern aus?"
     [System versteht Kontext: bezieht sich auf vorherige Frage]
```

**Historie löschen:**

- Sidebar → "🔄 Neue Konversation starten"
- Oder: Browser-Refresh (F5)

---

### 5. Multi-Chart-Support

**Was ist Multi-Chart?**

- System kann mehrere Charts in einer Antwort zeigen
- Automatische Erkennung von Chart-Markern
- Separate Anzeige jeder Visualisierung

**Beispiel:**

```
Sie: "Zeige mir Sentiment und NPS als Charts"

System erstellt:
1. sentiment_bar_chart
2. nps_bar_chart
Beide werden nacheinander angezeigt
```

---

## 📝 Beispielanfragen

### Kategorie: Metadaten & Übersicht

```
✅ "Wie ist die NPS-Verteilung in deinem Datensatz?"
✅ "Welche Märkte sind im Datensatz enthalten?"
✅ "Wie viele Feedbacks gibt es insgesamt?"
✅ "Was ist der Zeitraum der Daten?"
✅ "Gib mir eine Übersicht über den Datensatz"
✅ "Wie ist die Sentiment-Verteilung?"
✅ "Welche Themen gibt es im Datensatz?"
```

### Kategorie: Feedback-Analysen

```
✅ "Was sind die Top 5 Beschwerden?"
✅ "Zeige mir negative Feedbacks aus Deutschland"
✅ "Analysiere das Sentiment der Promoter"
✅ "Welche Probleme haben Detractoren?"
✅ "Was sagen Kunden über Lieferprobleme?"
✅ "Positive Erfahrungen aus Italien"
✅ "Service-Beschwerden in Q1 2023"
```

### Kategorie: Visualisierungen

```
✅ "Erstelle ein Balkendiagramm der Top 5 Themen mit NPS-Scores"
✅ "Zeige die Sentiment-Verteilung nach Märkten"
✅ "Erstelle eine Zeitreihen-Analyse der letzten 7 Monate"
✅ "Welche Händler haben die meisten Erwähnungen?"
✅ "NPS-Verteilung als Pie-Chart"
✅ "Dashboard mit allen Metriken"
```

### Kategorie: Geografische Analysen

```
✅ "Wie ist die NPS-Verteilung in Italien?"
✅ "Vergleiche Sentiment zwischen Deutschland und Frankreich"
✅ "Top 3 Themen in der C1-Region"
✅ "Negative Feedbacks aus Spanien"
✅ "Markt-Übersicht mit NPS-Breakdown"
```

### Kategorie: Zeitliche Analysen

```
✅ "Entwicklung des Sentiments über die Zeit"
✅ "NPS-Trend der letzten 6 Monate"
✅ "Feedback-Volumen im Q2 2023"
✅ "Themen-Verteilung über die Zeit"
```

### Kategorie: Kombinierte Analysen

```
✅ "Negative Service-Feedbacks von Detractoren in Deutschland"
✅ "Top 5 Lieferprobleme im Januar 2023"
✅ "Positive Reviews über Produktqualität von Promotern"
✅ "Sentiment-Analyse für Werkstatt-Themen nach Märkten"
```

---

## 💡 Best Practices

### 1. Formulierung von Fragen

**✅ GUT:**

```
"Top 5 Beschwerden"                    → Klar, präzise
"Negative Feedbacks aus Deutschland"   → Spezifisch
"NPS-Verteilung"                       → Direkt
```

**❌ VERMEIDEN:**

```
"Ähm, kannst du mir vielleicht..."    → Zu vage
"Alle Feedbacks"                       → Zu allgemein
"Was gibt es so?"                      → Unklar
```

### 2. Nutzung von Filtern

**Implizite Filter (System erkennt automatisch):**

```
"Negative Feedbacks"           → sentiment_filter="negativ"
"Detractor-Probleme"           → nps_filter="Detractor"
"Feedbacks aus Deutschland"    → country_filter="DE"
"Service-Beschwerden"          → topic_filter="Service"
```

**Explizite Zahlen:**

```
"Top 5"        → max_results=5
"Erste 3"      → max_results=3
"Zeige mir 10" → max_results=10
```

### 3. Chart-Erstellung

**Für Rankings/Vergleiche:**

```
✅ Balkendiagramm (bar_chart)
   → Besser für Vergleiche
   → Zeigt Werte direkt
```

**Für Verteilungen:**

```
✅ Kreisdiagramm (pie_chart)
   → Gut für Prozentanteile
   → Übersichtliche Proportionen
```

**Für zeitliche Entwicklung:**

```
✅ time_analysis
   → 4 Subplots mit Trends
   → Kompakte Zeitreihen-Übersicht
```

### 4. Kontext nutzen

**Multi-Turn-Konversationen:**

```
Sie: "Zeige negative Feedbacks"
     [Ergebnisse]

Sie: "Erstelle ein Chart dazu"
     [Chart basierend auf vorheriger Suche]

Sie: "Und wie sieht es bei Promotern aus?"
     [Neue Suche mit Kontext]
```

### 5. Effizienz

**Schnelle Antworten:**

- Metadaten-Fragen zuerst (sofortige Antwort)
- Dann spezifische Analysen
- Charts am Ende (dauern länger)

**Token-Optimierung:**

- Klare, präzise Fragen
- Nicht zu lange Historie
- Neue Konversation bei Themenwechsel

---

## 🎯 Tipps & Tricks

### Tipp 1: Beispielanfragen als Vorlage

Die 5 Beispielanfragen in der Sidebar decken alle Hauptfunktionen ab:

1. **Metadaten** - Zeigt Snapshot-Antwort
2. **Komplexe Analyse** - Demonstriert Feedback-Suche
3. **Sentiment + NPS** - Zeigt intelligente Filterung
4. **Geografisch** - Demonstriert Markt-Filter
5. **Chart** - Zeigt Visualisierung

→ Nutzen Sie diese als Vorlage für eigene Fragen!

### Tipp 2: Chart-Größe für Präsentationen

Für professionelle Präsentationen:

1. Sidebar → Chart-Größe: "Groß"
2. Frage stellen
3. Rechtsklick auf Chart → "Bild speichern als..."
4. Chart als PNG in Präsentation einfügen

### Tipp 3: Batch-Analysen

Mehrere Fragen hintereinander:

```
1. "NPS-Verteilung"
2. "Top 5 Beschwerden"
3. "Sentiment nach Märkten"
4. "Erstelle Dashboard"
```

→ System merkt sich Kontext

### Tipp 4: Fehlerbehandlung

Wenn keine Ergebnisse:

- System schlägt Alternativen vor
- Passen Sie Filter an
- Versuchen Sie breitere Suchbegriffe

### Tipp 5: Performance

Langsame Antworten?

- Reduzieren Sie Historie (Neue Konversation)
- Nutzen Sie spezifischere Filter
- Löschen Sie alte Charts (Sidebar)

---

## ❓ Häufig gestellte Fragen (FAQ)

### Allgemein

**F: Kann ich das System auf Englisch nutzen?**  
A: Das System ist primär für deutsche Fragen optimiert, versteht aber auch Englisch. Antworten sind immer auf Deutsch.

**F: Wie viele Fragen kann ich stellen?**  
A: Unbegrenzt während der Session. Beachten Sie aber API-Limits (OpenAI Rate Limits).

**F: Werden meine Daten gespeichert?**  
A: Chat-Historie existiert nur während der Browser-Session (In-Memory). Keine Persistenz.

### Funktionen

**F: Kann ich mehrere Charts gleichzeitig erstellen?**  
A: Ja! System unterstützt Multi-Chart-Anzeige. Fragen Sie z.B. "Zeige Sentiment und NPS als Charts".

**F: Kann ich Charts exportieren?**  
A: Ja! Rechtsklick auf Chart → "Bild speichern als..." (PNG-Format).

**F: Wie lange dauert eine Anfrage?**  
A:

- Metadaten: <1 Sekunde
- Feedback-Suche: 2-5 Sekunden
- Charts: 3-8 Sekunden

**F: Kann ich eigene Daten hochladen?**  
A: Aktuell nicht über UI. Entwickler können CSV-Dateien im `data/` Verzeichnis ersetzen.

### Technisch

**F: Welches LLM wird genutzt?**  
A: GPT-4o für Manager, GPT-4o-mini für Specialist Agents (konfigurierbar).

**F: Wie funktioniert die semantische Suche?**  
A: ChromaDB VectorStore mit OpenAI text-embedding-ada-002 Embeddings.

**F: Was ist der Unterschied zwischen synthetic und original data?**  
A:

- Synthetic: Künstlich generierte Daten (für Demo/Tests)
- Original: Echte Kundenfeedbacks (falls verfügbar)
  Wechsel in `streamlit_app.py` Zeile 42.

### Probleme

**F: "No results found" - was tun?**  
A:

1. Filter anpassen (weniger restriktiv)
2. Breitere Suchbegriffe nutzen
3. Zeitraum erweitern

**F: Charts werden nicht angezeigt**  
A:

1. Überprüfen Sie `charts/` Verzeichnis
2. Streamlit Cache löschen: `streamlit cache clear`
3. App neu starten

**F: "Rate limit exceeded"**  
A: OpenAI API-Limit erreicht. Warten Sie 1-2 Minuten oder upgraden Sie Plan.

---

## 🐛 Fehlerbehebung

### Problem: System antwortet nicht

**Symptome:**

- Spinner dreht sich endlos
- Keine Antwort erscheint

**Lösungen:**

1. Überprüfen Sie OpenAI API Key
2. Überprüfen Sie Internetverbindung
3. Browser-Console öffnen (F12) → Fehler prüfen
4. App neu starten

---

### Problem: Charts fehlen

**Symptome:**

- Chart-Marker sichtbar, aber kein Bild
- "Chart nicht gefunden" Warnung

**Lösungen:**

```powershell
# Charts-Verzeichnis erstellen
New-Item -ItemType Directory -Force -Path .\charts\

# Streamlit neu starten
# STRG+C im Terminal, dann:
streamlit run streamlit_app.py
```

---

### Problem: Langsame Antworten

**Ursachen:**

- Zu viel Historie
- Große max_results Werte
- Komplexe Chart-Generierung

**Lösungen:**

1. Neue Konversation starten (Sidebar)
2. Reduzieren Sie max_results (z.B. "Top 5" statt "alle")
3. Nutzen Sie spezifischere Filter

---

### Problem: "Keine Daten gefunden"

**Ursachen:**

- Zu restriktive Filter
- Falscher Zeitraum
- Nicht existierende Kategorien

**Lösungen:**

- System schlägt automatisch Alternativen vor
- Nutzen Sie weniger Filter gleichzeitig
- Überprüfen Sie Schreibweise (z.B. "DE" nicht "Deutschland")

---

### Problem: Falsche Antworten

**Mögliche Ursachen:**

- Unklare Fragestellung
- Zu wenig Kontext
- System misinterpretiert Frage

**Lösungen:**

1. Formulieren Sie Frage präziser
2. Geben Sie mehr Details
3. Nutzen Sie Beispiele aus Sidebar als Vorlage
4. Neue Konversation (frischer Kontext)

---

## 📞 Weitere Hilfe

**Für Entwickler:**

- Siehe [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- Siehe [ARCHITECTURE.md](ARCHITECTURE.md)

**Für Admins:**

- Siehe [QUICK_START.md](../QUICK_START.md)

**Community:**

- GitHub Issues (falls verfügbar)
- Support-Kontakt

---

## 🎓 Schulung & Training

### Empfohlene Lernkurve

**Woche 1: Grundlagen**

- Metadaten-Abfragen
- Einfache Feedback-Suche
- Erste Charts

**Woche 2: Fortgeschritten**

- Multi-Filter-Suche
- Verschiedene Chart-Typen
- Kontext-Nutzung

**Woche 3: Profi**

- Komplexe Analysen
- Batch-Queries
- Export & Präsentation

### Übungsaufgaben

1. **Aufgabe 1:** Finden Sie die 5 häufigsten Beschwerden
2. **Aufgabe 2:** Erstellen Sie ein Dashboard mit allen Metriken
3. **Aufgabe 3:** Analysieren Sie Sentiment-Unterschiede zwischen Märkten
4. **Aufgabe 4:** Identifizieren Sie Trends über Zeit
5. **Aufgabe 5:** Kombinieren Sie geografische und zeitliche Filter

---

**Viel Erfolg mit dem Customer Feedback RAG System! 🚀**

Bei weiteren Fragen: Siehe FAQ oder kontaktieren Sie Support.
