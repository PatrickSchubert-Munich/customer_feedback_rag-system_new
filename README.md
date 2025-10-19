# 🎯 Customer Feedback RAG System

> **Ein intelligentes KI-gestütztes System zur Analyse von Kundenfeedback mit Multi-Agent-Architektur**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-red.svg)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Über das Projekt

Das **Customer Feedback RAG System** ist eine fortschrittliche Anwendung, die künstliche Intelligenz nutzt, um Kundenfeedback automatisch zu analysieren, zu kategorisieren und zu visualisieren. Das System kombiniert **Retrieval-Augmented Generation (RAG)** mit einer **Multi-Agent-Architektur**, um präzise Antworten auf komplexe Fragen zu Kundenmeinungen zu liefern.

### 🎯 Hauptfunktionen

- **🤖 Intelligente Multi-Agent-Architektur**

  - Customer Manager Agent (Orchestrierung)
  - Feedback Analysis Expert (Semantische Suche)
  - Chart Creator Expert (Datenvisualisierung)
  - Output Summarizer (Business Reports)

- **🔍 Semantische Suche**

  - Vektorbasierte Suche mit ChromaDB
  - OpenAI Embeddings (text-embedding-ada-002)
  - Multi-Kriterien Filterung (NPS, Sentiment, Markt, Topic, Zeitraum)

- **📊 Automatische Visualisierung**

  - 10+ Chart-Typen (Sentiment, NPS, Market, Topic, Zeitreihen)
  - Dealership-Analyse (extrahiert Händlernamen aus Feedback-Text)
  - Dashboard-Übersichten mit mehreren Metriken

- **🎭 Umfassende Datenanalyse**

  - Sentiment-Analyse (VADER)
  - Topic-Klassifikation (Keyword-basiert)
  - NPS-Kategorisierung (Detractor, Passive, Promoter)
  - Token-Counting & Chunking-Optimierung

- **💬 Interaktive Chat-Oberfläche**
  - Streamlit-basierte Web-UI
  - Echtzeit-Streaming von Antworten
  - Konversations-Historie
  - Multi-Chart-Support

---

## 🚀 Quick Start

### Voraussetzungen

- Python 3.12+
- uv - Schneller Python Package Manager ([Installation](https://docs.astral.sh/uv/))
- OpenAI API Key oder Azure OpenAI Zugang
- Git (optional)

### Installation & Start in 3 Schritten

```powershell
# 1. Repository klonen (oder ZIP herunterladen)
git clone <repository-url>
cd customer_feedback_rag-system_new

# 2. Dependencies mit uv installieren (10-100x schneller als pip!)
uv sync
# Oder: uv pip install -r requirements.txt

# 3. Umgebungsvariablen konfigurieren
# Erstelle .env Datei und füge deinen OpenAI API Key ein
# Oder setze direkt:
$env:OPENAI_API_KEY="your-api-key-here"

# 4. Applikation starten (uv run aktiviert automatisch das Environment)
uv run streamlit run streamlit_app.py
```

➡️ Die App öffnet sich automatisch im Browser unter `http://localhost:8501`

**Hinweis:** uv ist ein moderner, ultra-schneller Python Package Manager. Alternativ funktioniert auch pip/venv.

📚 **Detaillierte Anleitung:** Siehe [QUICK_START.md](QUICK_START.md)

---

## 📚 Dokumentation

### Für Benutzer

- **[USER_GUIDE.md](docs/USER_GUIDE.md)** - Vollständige Benutzeranleitung
  - Erste Schritte
  - Features & Funktionen
  - Beispielanfragen
  - Tipps & Best Practices

### Für Entwickler

- **[DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)** - Entwickler-Dokumentation

  - Projekt-Setup
  - Code-Struktur
  - API-Referenz
  - Testing & Debugging

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System-Architektur
  - Multi-Agent-Design
  - Datenfluss
  - VectorStore-Implementierung
  - Technologie-Stack

### Quick Reference

- **[QUICK_START.md](QUICK_START.md)** - Schnellanleitung zum Starten

---

## 🏗️ Architektur-Überblick

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                         │
│                  (Chat Interface)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Customer Manager Agent                         │
│           (Orchestration & Routing)                         │
└─────────┬───────────────────────────────────┬───────────────┘
          │                                   │
          ▼                                   ▼
┌───────────────────────┐         ┌──────────────────────────┐
│ Feedback Analysis     │         │  Chart Creator Expert    │
│      Expert           │         │                          │
│ (Semantic Search)     │         │  (Data Visualization)    │
└───────┬───────────────┘         └──────────┬───────────────┘
        │                                    │
        ▼                                    ▼
┌────────────────────────┐        ┌─────────────────────────┐
│  ChromaDB VectorStore  │        │  10+ Chart Generators   │
│  (OpenAI Embeddings)   │        │  (Matplotlib)           │
└────────────────────────┘        └─────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────┐
│              CSV Data Source                             │
│  • feedback_synthetic.csv (Synthetic Data)               │
│  • feedback_data.csv (Original Data)                     │
└──────────────────────────────────────────────────────────┘
```

**Technologie-Stack:**

- **Frontend:** Streamlit 1.50+
- **Backend:** Python 3.12+
- **LLM:** OpenAI GPT-4o / GPT-4o-mini (Azure unterstützt)
- **Vector DB:** ChromaDB 1.0.21+
- **Embeddings:** OpenAI text-embedding-ada-002
- **Sentiment:** VADER Sentiment Analyzer
- **Visualization:** Matplotlib 3.10+

---

## 💡 Beispiel-Anfragen

Das System kann eine Vielzahl von Fragen beantworten:

### 📊 Metadaten-Abfragen

```
"Wie ist die NPS-Verteilung in deinem Datensatz?"
"Welche Märkte sind im Datensatz enthalten?"
"Wie viele Feedbacks gibt es insgesamt?"
```

### 🔍 Feedback-Analysen

```
"Was sind die Top 5 Beschwerden?"
"Zeige mir negative Feedbacks aus Deutschland"
"Analysiere das Sentiment der Promoter"
"Welche Probleme haben Detractoren?"
```

### 📈 Visualisierungen

```
"Erstelle ein Balkendiagramm der Top 5 Themen mit NPS-Scores"
"Zeige die Sentiment-Verteilung nach Märkten"
"Erstelle eine Zeitreihen-Analyse der letzten 7 Monate"
"Welche Händler haben die meisten Beschwerden?"
```

### 🌍 Geografische Analysen

```
"Wie ist die NPS-Verteilung in Italien?"
"Vergleiche Sentiment zwischen Deutschland und Frankreich"
"Top 3 Themen in der C1-Region"
```

---

## 📁 Projekt-Struktur

```
customer_feedback_rag-system_new/
│
├── streamlit_app.py              # Hauptanwendung (Streamlit UI)
│
├── customer_agents/              # Multi-Agent-System
│   ├── customer_manager_agent.py       # Orchestrierung
│   ├── feedback_analysis_agent.py      # Feedback-Suche
│   ├── chart_creator_agent.py          # Visualisierung
│   └── output_summarizer_agent.py      # Report-Generierung
│
├── customer_agents_tools/        # Agent-Tools
│   ├── search_tool.py                  # Semantische Suche
│   ├── create_charts_tool.py           # Chart-Generierung
│   ├── get_metadata_tool.py            # Metadaten-Abfragen
│   └── chart_generators/               # 10+ Chart-Typen
│
├── db/                           # Datenbank-Layer
│   ├── vectorstore_chroma.py           # ChromaDB Implementierung
│   └── vectorstore.py                  # Abstract Base Class
│
├── utils/                        # Hilfsfunktionen
│   ├── prepare_customer_data.py        # Daten-Preprocessing
│   ├── csv_loader.py                   # CSV-Loader
│   ├── helper_functions.py             # Utility-Funktionen
│   ├── topic_keywords.py               # Topic-Klassifikation
│   └── simple_history.py               # Konversations-Historie
│
├── data/                         # Datenquellen
│   ├── feedback_synthetic.csv          # Synthetische Daten
│   └── feedback_data.csv               # Original-Daten
│
├── streamlit_styles/             # UI-Styling
│   ├── header_styles.py
│   ├── footer_styles.py
│   ├── sidebar_styles.py
│   └── theme_config.py
│
├── test/                         # Test-Fragen
│   └── test_questions.py
│
├── docs/                         # Dokumentation
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   └── ARCHITECTURE.md
│
├── requirements.txt              # Python Dependencies
├── pyproject.toml               # Projekt-Konfiguration
├── .env                         # Umgebungsvariablen (nicht im Repo)
└── README.md                    # Diese Datei
```

---

## ⚙️ Konfiguration

### Umgebungsvariablen

Erstelle eine `.env` Datei im Projektverzeichnis:

```bash
# Standard OpenAI
OPENAI_API_KEY=sk-...

# Oder Azure OpenAI
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_DEPLOYMENT_NAME_MINI=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002
```

### Datenquellen-Wahl

In `streamlit_app.py` (Zeile 42):

```python
# Flag to choose between synthetic or original data
USE_SYNTHETIC_DATA = True  # False = Original-Daten nutzen
```

### Historie-Limit

In `streamlit_app.py` (Zeile 59):

```python
# HISTORY LIMIT - Begrenzt Historie-Turns an LLM
HISTORY_LIMIT = 4  # None = unbegrenzt, 3-5 empfohlen
```

---

## 🧪 Testing

```powershell
# Test-Fragen ausführen
python -m test.test_questions

# Einzelne Komponenten testen
python -m utils.csv_loader
python -m utils.prepare_customer_data
```

---

## 🤝 Contribution

Beiträge sind willkommen! Bitte beachte:

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

---

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) für Details.

---

## 👤 Autor

**Patrick Schubert**  
VaWi - Generative Artificial Intelligence  
Hausarbeit SS 2025

---

## 🙏 Danksagungen

- **OpenAI** für GPT-4o und Embedding-Modelle
- **LangChain** für Agent-Framework
- **Streamlit** für die Web-UI
- **ChromaDB** für VectorStore
- **VADER** für Sentiment-Analyse

---

## 📞 Support & Kontakt

Bei Fragen oder Problemen:

1. Siehe [USER_GUIDE.md](docs/USER_GUIDE.md) für Benutzer-Hilfe
2. Siehe [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) für technische Details
3. Öffne ein Issue auf GitHub (falls verfügbar)

---

**Made with ❤️ and 🤖 AI**
