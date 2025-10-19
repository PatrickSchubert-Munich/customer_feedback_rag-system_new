# 🏗️ Architecture Documentation - Customer Feedback RAG System

> Umfassende Dokumentation der System-Architektur

---

## 📖 Inhaltsverzeichnis

1. [Übersicht](#-übersicht)
2. [System-Architektur](#-system-architektur)
3. [Multi-Agent-Design](#-multi-agent-design)
4. [Datenfluss](#-datenfluss)
5. [VectorStore-Implementierung](#-vectorstore-implementierung)
6. [Technologie-Stack](#-technologie-stack)
7. [Datenmodell](#-datenmodell)
8. [Design-Patterns](#-design-patterns)
9. [Performance-Optimierungen](#-performance-optimierungen)
10. [Sicherheit & Best Practices](#-sicherheit--best-practices)

---

## 🎯 Übersicht

### System-Zweck

Das Customer Feedback RAG System ist eine **Multi-Agent RAG-Anwendung**, die folgende Kernfunktionen kombiniert:

1. **Retrieval-Augmented Generation (RAG)**

   - Vektorbasierte semantische Suche
   - Kontext-angereicherte LLM-Antworten
   - Metadaten-Filter für präzise Ergebnisse

2. **Multi-Agent-Orchestrierung**

   - Spezialisierte Agents für verschiedene Tasks
   - Automatische Handoff-Logik
   - Parallele Tool-Nutzung

3. **Datenvisualisierung**
   - 10+ Chart-Typen
   - Automatische Chart-Generierung
   - PNG-Export

### Architektur-Prinzipien

✅ **Modular** - Klare Trennung der Komponenten  
✅ **Skalierbar** - Einfaches Hinzufügen neuer Agents/Tools  
✅ **Testbar** - Isolierte Komponenten für Unit-Tests  
✅ **Wartbar** - Dokumentierter Code, Type Hints  
✅ **Performant** - Caching, Streaming, Batch-Processing

---

## 🏛️ System-Architektur

### High-Level-Architektur

```
┌────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                      │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Streamlit Web UI (streamlit_app.py)         │ │
│  │  • Chat Interface                                        │ │
│  │  • Sidebar Controls                                      │ │
│  │  • Chart Display                                         │ │
│  │  • Session Management                                    │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                         AGENT LAYER                             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │          Customer Manager Agent (Orchestrator)          │  │
│  │  • Request Routing                                      │  │
│  │  • Metadata Snapshot (embedded)                         │  │
│  │  • Agent Handoffs                                       │  │
│  └───────────────┬─────────────────────────────────────────┘  │
│                  │                                              │
│     ┌────────────┼────────────┐                                │
│     ▼            ▼            ▼                                │
│  ┌──────┐   ┌──────┐    ┌────────┐                            │
│  │ FBI  │   │ CCI  │    │  OSI   │                            │
│  │Expert│   │Expert│    │ Agent  │                            │
│  └──────┘   └──────┘    └────────┘                            │
│     │            │           │                                 │
│     │ Feedback   │ Chart     │ Output                          │
│     │ Analysis   │ Creator   │ Summarizer                      │
│     │            │           │                                 │
└─────┼────────────┼───────────┼─────────────────────────────────┘
      │            │           │
      ▼            ▼           ▼
┌────────────────────────────────────────────────────────────────┐
│                         TOOL LAYER                              │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐     │
│  │   Search     │  │   Chart      │  │   Metadata      │     │
│  │   Tool       │  │   Creator    │  │   Tool          │     │
│  │              │  │   Tool       │  │                 │     │
│  └──────┬───────┘  └──────┬───────┘  └─────────────────┘     │
│         │                 │                                    │
└─────────┼─────────────────┼────────────────────────────────────┘
          │                 │
          ▼                 ▼
┌────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │            ChromaDB VectorStore                          │ │
│  │  • OpenAI Embeddings (text-embedding-ada-002)            │ │
│  │  • Cosine Distance Metric                                │ │
│  │  • 27 Metadata Fields                                    │ │
│  │  • Persistent Storage                                    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │            CSV Data Source                               │ │
│  │  • feedback_synthetic.csv (Synthetic)                    │ │
│  │  • feedback_data.csv (Original)                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │            Chart Storage                                 │ │
│  │  • charts/ directory                                     │ │
│  │  • PNG files                                             │ │
│  │  • Auto-cleanup                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### Component Diagram

```
┌─────────────────────┐
│  Streamlit App      │
│  (streamlit_app.py) │
└──────────┬──────────┘
           │
           │ calls initialize_system()
           ▼
┌────────────────────────────────────┐
│  Helper Functions                  │
│  (utils/helper_functions.py)       │
│  • initialize_system()              │
│  • process_query_streamed()         │
│  • build_metadata_snapshot()        │
└──────┬────────────┬─────────────────┘
       │            │
       │            └─────────────────┐
       │                              │
       ▼                              ▼
┌─────────────────┐          ┌────────────────┐
│  CSV Loader     │          │  Data Prep     │
│  (csv_loader)   │────────▶ │  (prepare_     │
└─────────────────┘          │   customer_    │
                             │   data)        │
                             └───────┬────────┘
                                     │
                                     ▼
                             ┌────────────────┐
                             │  VectorStore   │
                             │  (chroma)      │
                             └────────────────┘
```

---

## 🤖 Multi-Agent-Design

### Agent-Hierarchie

```
                    Customer Manager Agent
                           (Orchestrator)
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
    Feedback Analysis    Chart Creator    Output Summarizer
         Expert              Expert            Agent
            │                   │                │
            │                   │                │
      search_customer     feedback_analytics     (no tools)
         _feedback              tool
```

### Agent-Spezifikationen

#### 1. Customer Manager Agent

**Rolle:** Orchestrator, Central Entry Point

**Verantwortlichkeiten:**

- Request Routing & Classification
- Metadata-Fragen direkt beantworten
- Handoffs zu Specialist Agents
- Response Coordination

**Besonderheiten:**

- **Keine Tools** - Nutzt nur embedded Metadata Snapshot
- **Metadaten-Snapshot** - Vorberechnete Statistiken beim Start
- **Handoff-Logik** - Intelligente Weiterleitung

**Metadaten-Snapshot (embedded):**

```python
{
    "unique_markets": "C1-DE, C1-FR, CE-IT, ...",
    "nps_statistics": "Avg: 7.2, Median: 8, Detractor: 25%, ...",
    "sentiment_statistics": "Positiv: 45%, Neutral: 30%, ...",
    "topic_statistics": "Service: 230, Lieferung: 180, ...",
    "date_range": "2023-01-01 bis 2023-12-31",
    "verbatim_statistics": "Avg tokens: 45, Max: 850, ...",
    "dataset_overview": "1250 Feedbacks aus 8 Märkten",
    "total_entries": "1250"
}
```

**Handoff-Strategien:**

```python
# Content-Analysen → Feedback Analysis Expert
if "Beschwerde" or "feedback" or "Problem" in query:
    handoff_to(feedback_analysis_expert)

# Visualisierungen → Chart Creator Expert
if "Chart" or "Diagramm" or "zeige" in query:
    handoff_to(chart_creator_expert)

# Metadaten → Direkt aus Snapshot
if "NPS-Verteilung" or "Märkte" or "Anzahl":
    answer_from_snapshot()
```

**Model:** `gpt-4o` (High-quality routing decisions)

---

#### 2. Feedback Analysis Expert

**Rolle:** Content-based feedback analysis specialist

**Verantwortlichkeiten:**

- Semantische Feedback-Suche
- Filter-Anwendung (NPS, Sentiment, Market, Topic, Time)
- Result Aggregation & Analysis
- Handoff zu Output Summarizer (für umfangreiche Ergebnisse)

**Tools:**

- `search_customer_feedback` - Semantic search mit Multi-Criteria Filtering

**Chain-of-Thought Reasoning:**

```
STEP 1: Extract Explicit Numbers
  → "Top 5" → max_results=5

STEP 2: Identify Required Filters
  → "negativ" → sentiment_filter="negativ"
  → "Deutschland" → country_filter="DE"
  → "Promoter" → nps_filter="Promoter"

STEP 3: Formulate Search Query
  → Semantic terms: "Lieferprobleme"

STEP 4: Execute Search
  → search_customer_feedback(query, max_results, filters)

STEP 5: Decide Handoff
  → >3 results → transfer_to_output_summarizer
  → ≤3 results → Direct answer
```

**Model:** `gpt-4o-mini` (Cost-efficient, sufficient for structured tasks)

---

#### 3. Chart Creator Expert

**Rolle:** Data visualization specialist

**Verantwortlichkeiten:**

- Chart-Typ-Auswahl (10+ Typen)
- Chart-Generierung (PNG)
- Chart-Marker-Handling
- Error Handling & Fallbacks

**Tools:**

- `feedback_analytics` - Chart creation tool mit 10+ Typen

**Chart-Selection-Logic:**

```python
# Explicit Type
if "Balken" in query → *_bar_chart
if "Kreis" or "Pie" in query → *_pie_chart

# Time-based
if "über Zeit" or "Trend" or "Entwicklung" → time_analysis

# Topic-based
if "Sentiment" → sentiment_*
if "NPS" → nps_*
if "Markt" → market_*
if "Themen" → topic_bar_chart
if "Händler" → dealership_bar_chart
```

**Chart-Marker-Protocol:**

```
Tool returns: __CHART__/path/to/chart.png__CHART__
Agent preserves marker EXACTLY (no Markdown conversion!)
Streamlit extracts and displays chart
```

**Error Handling:**

```python
if "Keine Daten" in response:
    - Translate to friendly German
    - Suggest 3-4 alternative chart types
    - Keep it SHORT and helpful
```

**Model:** `gpt-4o-mini`

---

#### 4. Output Summarizer Agent

**Rolle:** Business report formatter

**Verantwortlichkeiten:**

- Format technical results as business reports
- Create executive summaries
- Highlight key insights
- Professional German language

**Tools:** None (pure formatting)

**Input:** Raw search results from Feedback Analysis Expert

**Output:** Structured business report with:

- Executive Summary
- Key Findings (numbered list)
- Detailed Insights
- Recommendations (if applicable)

**Model:** `gpt-4o-mini`

---

### Agent Communication Flow

#### Scenario 1: Metadata Query (Fast Path)

```
User: "Wie ist die NPS-Verteilung?"
  │
  ▼
Customer Manager Agent
  │ (checks embedded snapshot)
  │ → Finds "nps_statistics" in metadata
  │ → Answers directly
  ▼
Response: "NPS-Verteilung: Promoter 45%, Passive 30%, Detractor 25%"
```

**Latency:** <500ms  
**Cost:** 1 API call (Manager)

---

#### Scenario 2: Content Analysis (Multi-Agent)

```
User: "Was sind die Top 5 Beschwerden?"
  │
  ▼
Customer Manager Agent
  │ → Identifies: Content analysis required
  │ → Handoff decision
  ▼
Feedback Analysis Expert
  │ → Calls search_customer_feedback(query="Beschwerde", max_results=5)
  │ → Receives 5 feedbacks
  │ → >3 results → Handoff decision
  ▼
Output Summarizer Agent
  │ → Formats as business report
  │ → Returns structured summary
  ▼
Response: [Professional Business Report with Key Findings]
```

**Latency:** 3-5 seconds  
**Cost:** 3 API calls (Manager, Analyst, Summarizer) + 1 Tool call

---

#### Scenario 3: Visualization (Chart Creation)

```
User: "Erstelle ein NPS-Balkendiagramm"
  │
  ▼
Customer Manager Agent
  │ → Identifies: Visualization required
  │ → Handoff decision
  ▼
Chart Creator Expert
  │ → Calls feedback_analytics(chart_type="nps_bar_chart")
  │ → Receives __CHART__/path/to/chart.png__CHART__
  │ → Preserves marker EXACTLY
  ▼
Streamlit App
  │ → Extracts chart path from marker
  │ → Displays PNG image
  ▼
Response: [Short text + Chart display]
```

**Latency:** 3-8 seconds  
**Cost:** 2 API calls (Manager, Creator) + 1 Tool call

---

## 🔄 Datenfluss

### End-to-End Data Flow

```
┌─────────────┐
│ User Input  │
└──────┬──────┘
       │
       ▼
┌───────────────────────────┐
│ Streamlit Chat Input      │
│ • Text processing          │
│ • Session context          │
└──────┬────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│ process_query_streamed()       │
│ • Builds history context       │
│ • Limits history (HISTORY_LIMIT)│
│ • Calls Runner.run_stream()    │
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│ OpenAI Agents SDK              │
│ • Multi-Agent Orchestration    │
│ • Tool Execution               │
│ • Streaming Response           │
└──────┬─────────────────────────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌──────────────┐  ┌──────────────────┐
│ Tools        │  │ Agent Handoffs   │
│ • search     │  │ • Feedback Expert│
│ • charts     │  │ • Chart Creator  │
│ • metadata   │  │ • Summarizer     │
└──────┬───────┘  └────────┬─────────┘
       │                   │
       ▼                   ▼
┌──────────────────────────────────┐
│ Data Sources                     │
│ • VectorStore (semantic search)  │
│ • Metadata Snapshot (fast stats) │
│ • Chart Generators (viz)         │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Stream Response Tokens           │
│ • Word-by-word streaming         │
│ • Chart marker extraction        │
│ • Display in Streamlit           │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────┐
│ User Sees    │
│ Response     │
└──────────────┘
```

### VectorStore Creation Flow

```
┌────────────────┐
│ App Startup    │
└───────┬────────┘
        │
        ▼
┌─────────────────────────────┐
│ check_vectorstore_exists()  │
│ • Checks chroma/ directory  │
│ • Counts documents          │
└───────┬─────────────────────┘
        │
        ├─── Exists? ───┐
        │               │
        NO              YES
        │               │
        ▼               ▼
┌──────────────┐  ┌─────────────┐
│ Create New   │  │ Load Existing│
└──────┬───────┘  └─────────────┘
       │
       ▼
┌───────────────────────────┐
│ CSVLoader.load_data()     │
│ • Reads CSV               │
│ • Validates columns       │
└──────┬────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ PrepareCustomerData()        │
│ • NPS categorization         │
│ • Sentiment analysis (VADER) │
│ • Topic classification       │
│ • Token counting             │
│ • Market splitting           │
└──────┬───────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ ChromaVectorStore.load()        │
│ • Chunking (feedback-optimized) │
│ • Embedding (OpenAI Ada-002)    │
│ • Metadata enrichment (27 fields)│
│ • Batch processing (100/batch)  │
│ • Persistent storage            │
└─────┬───────────────────────────┘
      │
      ▼
┌──────────────────┐
│ VectorStore Ready│
└──────────────────┘
```

---

## 🗄️ VectorStore-Implementierung

### ChromaDB Architecture

```
chroma/
└── feedback_vectorstore/
    ├── chroma.sqlite3           # Metadata DB
    └── 5a8fcaf3-.../            # Embeddings & Data
        ├── data_level0.bin      # HNSW Index
        ├── header.bin           # Collection Info
        └── length.bin           # Document Lengths
```

### Chunking Strategy

**Feedback-Optimized Chunking:**

```python
# 99.9% of feedbacks are <4000 chars → NO chunking
if len(verbatim) < 4000:
    chunks = [verbatim]  # Preserve semantic unit

# Only extreme outliers (>4000 chars)
else:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,      # Large chunks
        chunk_overlap=500,    # High overlap for context
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_text(verbatim)
```

**Rationale:**

- Preserves semantic coherence
- Avoids fragmentation of feedback context
- Only splits extremely long texts
- High overlap ensures no context loss

### Metadata Schema (27 Fields)

```python
metadata = {
    # Identity
    "row_id": int,                    # DataFrame row index

    # NPS
    "nps": int,                       # 0-10
    "nps_category": str,              # Detractor/Passive/Promoter

    # Geography
    "market": str,                    # "C1-DE", "CE-IT"
    "region": str,                    # "C1", "CE"
    "country": str,                   # "DE", "IT", "FR" (ISO)

    # Time
    "date": int,                      # Unix timestamp
    "date_str": str,                  # "2023-01-15"

    # Sentiment
    "sentiment_label": str,           # positiv/neutral/negativ
    "sentiment_score": float,         # -1.0 to 1.0

    # Topic
    "topic": str,                     # Service/Lieferproblem/etc.
    "topic_confidence": float,        # 0.0 to 1.0

    # Text Metrics
    "verbatim_token_count": int,      # Token count
    "verbatim_preview": str,          # First 100 chars

    # Chunking Info
    "chunk_index": int,               # Current chunk (0-based)
    "total_chunks": int,              # Total chunks for this feedback

    # [... additional fields ...]
}
```

### Embedding Model

**Model:** `text-embedding-ada-002`

**Characteristics:**

- Dimensions: 1536
- Cross-Lingual Performance: 92% average (88.8%-94.1%)
- Optimized for: German, English, Italian, French, Spanish
- Cost: $0.0001 per 1K tokens

**Why Ada-002?**
✅ Superior cross-lingual performance  
✅ Cost-effective ($0.0001/1K tokens)  
✅ High accuracy for semantic search  
✅ Stable & Production-ready

### Distance Metric

**Metric:** Cosine Distance

```python
collection = client.create_collection(
    name="feedback_data",
    metadata={"hnsw:space": "cosine"}  # Explicit cosine
)
```

**Why Cosine?**

- Optimal for OpenAI embeddings
- Angle-based similarity (not magnitude)
- Range: 0 (identical) to 2 (opposite)

### Search Implementation

```python
def search_customer_feedback(
    query: str,
    max_results: int = 10,
    filters: dict = None
) -> list:
    """
    Semantic search with metadata filtering
    """
    # 1. Build WHERE clause from filters
    where_clause = build_where_clause(filters)

    # 2. Query ChromaDB
    results = collection.query(
        query_texts=[query],
        n_results=max_results,
        where=where_clause,
        include=["documents", "metadatas", "distances"]
    )

    # 3. Confidence thresholding
    filtered_results = apply_confidence_threshold(results)

    # 4. Format results
    return format_results(filtered_results)
```

**Confidence Thresholds (optimized for Ada-002):**

```python
CONFIDENCE_THRESHOLDS = {
    "REJECT": 0.60,   # <60%: No results
    "LOW": 0.75,      # <75%: Warning
    "MEDIUM": 0.85,   # <85%: Moderate
    # ≥85%: High quality
}
```

---

## 💻 Technologie-Stack

### Core Technologies

| Component           | Technology             | Version | Purpose                   |
| ------------------- | ---------------------- | ------- | ------------------------- |
| **Language**        | Python                 | 3.12+   | Core language             |
| **Web Framework**   | Streamlit              | 1.50+   | UI & Chat interface       |
| **LLM**             | OpenAI GPT-4o/4o-mini  | Latest  | Agent intelligence        |
| **Agent Framework** | OpenAI Agents SDK      | 0.3.1+  | Multi-agent orchestration |
| **Vector DB**       | ChromaDB               | 1.0.21+ | Semantic search           |
| **Embeddings**      | text-embedding-ada-002 | -       | Vector embeddings         |
| **Data Processing** | Pandas                 | 2.3+    | Data manipulation         |
| **Sentiment**       | VADER                  | 3.3.2   | Sentiment analysis        |
| **Visualization**   | Matplotlib             | 3.10+   | Chart generation          |
| **Environment**     | python-dotenv          | 1.1+    | Config management         |

### Dependencies Tree

```
streamlit 1.50+
├── openai 1.88+
│   └── openai-agents 0.3.1+
├── chromadb 1.0.21+
│   └── langchain-chroma 0.2.6+
├── pandas 2.3+
│   └── numpy 2.3+
├── matplotlib 3.10+
├── vadersentiment 3.3.2
└── python-dotenv 1.1+
```

### Azure vs Standard OpenAI Support

```python
# Detection Logic
def is_azure_openai() -> bool:
    return bool(
        os.environ.get("AZURE_OPENAI_API_KEY") and
        os.environ.get("AZURE_OPENAI_ENDPOINT") and
        os.environ.get("AZURE_OPENAI_API_VERSION")
    )

# Client Instantiation
if is_azure_openai():
    client = AsyncAzureOpenAI(...)
else:
    client = AsyncOpenAI(...)
```

**Supported Configurations:**

- ✅ Standard OpenAI API
- ✅ Azure OpenAI Service
- ✅ Mixed (Azure for LLM, OpenAI for Embeddings)

---

## 📊 Datenmodell

### CSV Schema

**Required Columns:**

| Column     | Type | Description        | Example                 |
| ---------- | ---- | ------------------ | ----------------------- |
| `NPS`      | int  | Net Promoter Score | 0-10                    |
| `Verbatim` | str  | Feedback text      | "Sehr gute Beratung..." |
| `Market`   | str  | Market ID          | "C1-DE", "CE-IT"        |
| `Date`     | str  | Date               | "2023-01-15"            |

**Auto-Generated Columns (by PrepareCustomerData):**

| Column                 | Type  | Description                | Source             |
| ---------------------- | ----- | -------------------------- | ------------------ |
| `nps_category`         | str   | Detractor/Passive/Promoter | NPS categorization |
| `region`               | str   | Business region            | Market split       |
| `country`              | str   | ISO country code           | Market split       |
| `sentiment_label`      | str   | positiv/neutral/negativ    | VADER              |
| `sentiment_score`      | float | -1.0 to 1.0                | VADER              |
| `topic`                | str   | Topic category             | Keyword matching   |
| `topic_confidence`     | float | 0.0 to 1.0                 | Keyword matching   |
| `verbatim_token_count` | int   | Token count                | tiktoken           |

### Data Processing Pipeline

```python
# 1. Load CSV
data = pd.read_csv("feedback_data.csv")

# 2. Enhance Data
enhanced_data = PrepareCustomerData(data)
# → Adds: nps_category, region, country, sentiment, topic, tokens

# 3. Create VectorStore
vectorstore = ChromaVectorStore(enhanced_data)
# → Chunks, embeds, stores with 27 metadata fields

# 4. Build Metadata Snapshot
snapshot = build_metadata_snapshot(vectorstore.collection)
# → Pre-computes statistics for fast access
```

### NPS Categorization

```python
def categorize_nps(score: int) -> str:
    if 0 <= score <= 6:
        return "Detractor"
    elif 7 <= score <= 8:
        return "Passive"
    elif 9 <= score <= 10:
        return "Promoter"
    else:
        return "Invalid"
```

### Sentiment Analysis (VADER)

**Why VADER?**

- ✅ Rule-based (no training needed)
- ✅ Fast (no API calls)
- ✅ Works reasonably well for German
- ✅ Provides compound score (-1 to 1)

```python
analyzer = SentimentIntensityAnalyzer()
scores = analyzer.polarity_scores(text)

# Categorization
if scores['compound'] >= 0.05:
    label = "positiv"
elif scores['compound'] <= -0.05:
    label = "negativ"
else:
    label = "neutral"
```

### Topic Classification

**Method:** Keyword-based matching

**Categories:**

1. Service & Beratung
2. Lieferproblem
3. Produktqualität
4. Preis & Finanzierung
5. Terminvergabe
6. Werkstatt & Reparatur
7. Kommunikation
8. Sonstiges (fallback)

**Implementation:** `utils/topic_keywords.py`

```python
# Keyword lists per category
KEYWORDS = {
    "Service & Beratung": ["service", "beratung", "berater", ...],
    "Lieferproblem": ["lieferung", "verzögerung", "wartezeit", ...],
    # ...
}

def classify_feedback_topic(text: str) -> tuple[str, float]:
    # Returns: (topic, confidence)
    # Confidence based on keyword match count
```

---

## 🎨 Design-Patterns

### 1. Factory Pattern

**Usage:** Tool creation

```python
class SearchToolFactory:
    @staticmethod
    def create_search_tool(collection):
        @function_tool
        def search_customer_feedback(...):
            # Implementation
        return search_customer_feedback
```

### 2. Strategy Pattern

**Usage:** Chart selection

```python
class ChartGeneratorStrategy:
    strategies = {
        "sentiment_bar_chart": generate_sentiment_bar,
        "nps_pie_chart": generate_nps_pie,
        # ...
    }

    def generate(chart_type: str, **kwargs):
        return strategies[chart_type](**kwargs)
```

### 3. Singleton Pattern

**Usage:** VectorStore instance

```python
@st.cache_resource
def get_vectorstore():
    # Cached across all users/sessions
    return ChromaVectorStore(...)
```

### 4. Observer Pattern

**Usage:** Streamlit session state

```python
# Streamlit automatically observes session_state changes
st.session_state.conversation.add_message(...)
# → UI auto-updates
```

### 5. Template Method Pattern

**Usage:** Agent instructions

```python
class BaseAgent:
    instructions = f"""
    {RECOMMENDED_PROMPT_PREFIX}

    {self.get_role_description()}
    {self.get_specific_instructions()}
    {self.get_tool_descriptions()}
    """
```

---

## ⚡ Performance-Optimierungen

### 1. Metadata Snapshot (Embedded)

**Problem:** Metadaten-Abfragen erfordern Tool-Calls → langsam

**Solution:** Pre-compute metadata beim Start, embed in Manager Agent

**Benefit:**

- Metadaten-Antworten in <500ms (vorher: 2-3 Sekunden)
- Keine Tool-Calls nötig
- Kostenersparnis (weniger API-Aufrufe)

```python
# Beim Start einmalig:
snapshot = build_metadata_snapshot(collection)

# Im Agent embedded:
manager_agent = Agent(
    instructions=f"...\n\nEmbedded Metadata:\n{snapshot}\n..."
)
```

### 2. Streaming Response

**Problem:** Warten auf vollständige Antwort → schlechte UX

**Solution:** Token-by-token streaming

**Benefit:**

- Sofortige Rückmeldung an User
- Gefühlte Latenz reduziert
- Bessere UX

```python
async for chunk in process_query_streamed(...):
    yield chunk  # Streamlit displays word-by-word
```

### 3. History Limiting

**Problem:** Unbegrenzte Historie → explodierende Token-Kosten

**Solution:** Limit auf letzte N Turns

**Configuration:**

```python
HISTORY_LIMIT = 4  # Nur letzte 4 Interaktionen
# None = unbegrenzt (teuer!)
```

**Benefit:**

- Konstante Token-Kosten
- Schnellere Antworten (weniger Context)
- Trade-off: Weniger Long-Term-Memory

### 4. Batch Embedding

**Problem:** Einzelne Embeddings langsam

**Solution:** Batch processing

```python
batch_size = 100
for i in range(0, len(docs), batch_size):
    batch = docs[i:i+batch_size]
    embeddings = embed_batch(batch)
```

**Benefit:**

- 5-10x schneller als einzeln
- Effizientere API-Nutzung

### 5. Caching

**Streamlit Caching:**

```python
@st.cache_resource  # Across all users
def get_vectorstore():
    return ChromaVectorStore(...)

@st.cache_data(ttl=1)  # Per session, 1 second TTL
def get_stats():
    return calculate_stats()
```

**Benefit:**

- VectorStore nur einmal geladen
- Wiederverwendung über Sessions
- Reduzierte Ladezeiten

### 6. Chart Cleanup

**Problem:** Charts akkumulieren → Speicher füllt sich

**Solution:** Auto-cleanup alter Charts

```python
# Nach jeder Chart-Generierung:
if cleanup_enabled:
    remove_old_charts(keep_recent=5)
```

**Benefit:**

- Konstanter Speicherverbrauch
- Keine manuelle Wartung nötig

---

## 🔒 Sicherheit & Best Practices

### 1. API Key Management

**✅ Best Practice:**

```python
# .env Datei (nicht in Git!)
OPENAI_API_KEY=sk-...

# Laden mit dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

**❌ Anti-Pattern:**

```python
# Hardcoded in Code (NIEMALS!)
api_key = "sk-proj-xyz123..."
```

### 2. Input Validation

**User Input:**

```python
# Sanitize user input
def sanitize_input(text: str) -> str:
    # Remove potentially harmful characters
    # Limit length
    # Validate encoding
    return cleaned_text
```

**Filter Values:**

```python
# Validate filter values against allowed set
ALLOWED_SENTIMENTS = ["positiv", "neutral", "negativ"]
if sentiment_filter not in ALLOWED_SENTIMENTS:
    raise ValueError(f"Invalid sentiment: {sentiment_filter}")
```

### 3. Error Handling

**Graceful Degradation:**

```python
try:
    results = search_customer_feedback(...)
except Exception as e:
    logger.error(f"Search failed: {e}")
    return "Entschuldigung, Suche fehlgeschlagen. Bitte versuchen Sie es erneut."
```

**User-Friendly Messages:**

```python
# ❌ Technical error
"ValueError: 'country' not in metadata"

# ✅ User-friendly
"Entschuldigung, dieser Markt wurde nicht gefunden. Verfügbare Märkte: DE, IT, FR"
```

### 4. Rate Limiting

**OpenAI API:**

```python
# Respect rate limits
# Implement exponential backoff
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(min=1, max=60))
def api_call_with_retry(...):
    return client.call(...)
```

### 5. Data Privacy

**PII Handling:**

- ✅ Anonymisiere Kundennamen in Feedbacks
- ✅ Keine sensiblen Daten in Logs
- ✅ Secure storage für API Keys

### 6. Code Quality

**Type Hints:**

```python
def search_tool(
    query: str,
    max_results: int = 10,
    filters: dict | None = None
) -> str:
    """Well-documented with types"""
```

**Docstrings:**

```python
"""
Comprehensive docstring with:
- Purpose
- Args (types, defaults, constraints)
- Returns (type, format)
- Raises (exceptions)
- Examples
"""
```

**Linting:**

```python
# pyproject.toml
[tool.ruff]
line-length = 88
```

---

## 🎯 Design Decisions & Rationale

### Why Multi-Agent Architecture?

**Alternative:** Single Agent mit allen Tools

**Chosen:** Multi-Agent mit Spezialisierung

**Rationale:**

- ✅ Separation of Concerns
- ✅ Einfacher zu debuggen
- ✅ Bessere Tool-Nutzung (Spezialist = effektiver)
- ✅ Skalierbar (neue Agents hinzufügen)
- ✅ Klare Verantwortlichkeiten

### Why Embedded Metadata Snapshot?

**Alternative:** Metadata-Tool mit Runtime-Calls

**Chosen:** Embedded Snapshot beim Start

**Rationale:**

- ✅ 5x schneller (<500ms statt 2-3 Sekunden)
- ✅ Kostenersparnis (keine Tool-Calls)
- ✅ Metadaten ändern sich selten
- ✅ Aktualisierung beim App-Start reicht

### Why ChromaDB over Pinecone?

**Alternative:** Pinecone (Cloud Vector DB)

**Chosen:** ChromaDB (Local Vector DB)

**Rationale:**

- ✅ Keine Cloud-Abhängigkeit
- ✅ Kostenfrei (keine Pinecone-Subscription)
- ✅ Schneller (lokal)
- ✅ Datenschutz (Daten bleiben lokal)
- ✅ Einfaches Setup (keine API Keys)

### Why VADER for Sentiment?

**Alternative:** LLM-based Sentiment (GPT-4)

**Chosen:** VADER (Rule-based)

**Rationale:**

- ✅ Kostenfrei (keine API-Calls)
- ✅ Sehr schnell (lokal)
- ✅ Deterministisch (reproduzierbar)
- ✅ Gute Baseline-Performance
- ❌ Trade-off: Weniger akkurat als LLM

### Why GPT-4o-mini for Specialists?

**Alternative:** GPT-4o für alle Agents

**Chosen:** GPT-4o für Manager, 4o-mini für Specialists

**Rationale:**

- ✅ Kostenoptimierung (4o-mini ist 60% günstiger)
- ✅ Manager braucht best reasoning (4o)
- ✅ Specialists haben structured tasks (4o-mini reicht)
- ✅ Schnellere Antworten (4o-mini ist schneller)

---

## 📚 Weitere Ressourcen

- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Code-Level Details
- **[USER_GUIDE.md](USER_GUIDE.md)** - Benutzer-Perspektive
- **[QUICK_START.md](../QUICK_START.md)** - Setup & Installation

---

**Architektur-Dokumentation erstellt mit ❤️ für Developer**
