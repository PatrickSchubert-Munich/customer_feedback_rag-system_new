# 💻 Developer Guide - Customer Feedback RAG System

> Umfassende Entwickler-Dokumentation

---

## 📖 Inhaltsverzeichnis

1. [Projekt-Setup](#-projekt-setup)
2. [Code-Struktur](#-code-struktur)
3. [Entwicklungs-Workflow](#-entwicklungs-workflow)
4. [Agent-Entwicklung](#-agent-entwicklung)
5. [Tool-Entwicklung](#-tool-entwicklung)
6. [Chart-Generator-Entwicklung](#-chart-generator-entwicklung)
7. [Testing & Debugging](#-testing--debugging)
8. [Performance-Tuning](#-performance-tuning)
9. [Deployment](#-deployment)
10. [API-Referenz](#-api-referenz)
11. [Best Practices](#-best-practices)
12. [Troubleshooting](#-troubleshooting)

---

## 🚀 Projekt-Setup

### Entwicklungsumgebung einrichten

```powershell
# 1. Repository klonen
git clone <repository-url>
cd customer_feedback_rag-system_new

# 2. Virtual Environment erstellen
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Development Dependencies installieren
pip install -r requirements.txt

# 4. Pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Environment Variables

Erstelle `.env` Datei:

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-...

# Oder Azure OpenAI
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://....openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_DEPLOYMENT_NAME_MINI=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002

# Optional: Debugging
OPENAI_LOG_LEVEL=debug
LANGCHAIN_TRACING_V2=true
```

### IDE Setup (VS Code)

**Empfohlene Extensions:**

- Python (Microsoft)
- Pylance
- Ruff
- GitLens
- Markdown Preview Enhanced

**settings.json:**

```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "ruff",
  "editor.formatOnSave": true,
  "python.analysis.typeCheckingMode": "basic"
}
```

---

## 📂 Code-Struktur

### Directory Layout

```
customer_feedback_rag-system_new/
│
├── streamlit_app.py                    # Main application entry point
│
├── customer_agents/                    # Multi-Agent System
│   ├── __init__.py
│   ├── customer_manager_agent.py       # Orchestrator Agent
│   ├── feedback_analysis_agent.py      # Content Analysis Agent
│   ├── chart_creator_agent.py          # Visualization Agent
│   └── output_summarizer_agent.py      # Report Formatting Agent
│
├── customer_agents_tools/              # Agent Tools
│   ├── __init__.py
│   ├── search_tool.py                  # Semantic Search Tool
│   ├── create_charts_tool.py           # Chart Creation Tool
│   ├── get_metadata_tool.py            # Metadata Query Tool
│   └── chart_generators/               # Chart Generation Modules
│       ├── __init__.py
│       ├── _shared.py                  # Shared utilities
│       ├── sentiment_charts.py         # Sentiment visualizations
│       ├── nps_charts.py               # NPS visualizations
│       ├── market_charts.py            # Market visualizations
│       ├── topic_charts.py             # Topic visualizations
│       ├── dealership_charts.py        # Dealership analysis
│       ├── time_analysis_chart.py      # Time series analysis
│       └── overview_chart.py           # Dashboard generation
│
├── db/                                 # Database Layer
│   ├── __init__.py
│   ├── vectorstore.py                  # Abstract VectorStore base
│   └── vectorstore_chroma.py           # ChromaDB implementation
│
├── utils/                              # Utility Modules
│   ├── __init__.py
│   ├── helper_functions.py             # Core helper functions
│   ├── csv_loader.py                   # CSV data loader
│   ├── prepare_customer_data.py        # Data preprocessing
│   ├── topic_keywords.py               # Topic classification
│   ├── simple_history.py               # Conversation history
│   ├── chart_cleanup.py                # Chart management
│   └── synthetic_data_generator.py     # Synthetic data generation
│
├── streamlit_styles/                   # UI Styling
│   ├── __init__.py
│   ├── header_styles.py                # Header component
│   ├── footer_styles.py                # Footer component
│   ├── sidebar_styles.py               # Sidebar component
│   ├── layout_styles.py                # Layout styles
│   └── theme_config.py                 # Theme configuration
│
├── data/                               # Data Sources
│   ├── feedback_synthetic.csv          # Synthetic test data
│   └── feedback_data.csv               # Original data (if available)
│
├── test/                               # Test Modules
│   ├── __init__.py
│   └── test_questions.py               # Predefined test queries
│
├── charts/                             # Generated charts (auto-created)
├── chroma/                             # VectorStore persistence
│
├── docs/                               # Documentation
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   └── ARCHITECTURE.md
│
├── requirements.txt                    # Python dependencies
├── pyproject.toml                      # Project configuration
├── .env                                # Environment variables (not in repo)
├── .gitignore
└── README.md                           # Project overview
```

### Module Dependencies

```
streamlit_app.py
    ├─→ utils.helper_functions
    │   ├─→ customer_agents.*
    │   ├─→ customer_agents_tools.*
    │   ├─→ db.vectorstore_chroma
    │   └─→ utils.prepare_customer_data
    ├─→ streamlit_styles.*
    ├─→ test.test_questions
    └─→ utils.simple_history

customer_agents.*
    ├─→ customer_agents_tools.*
    └─→ utils.helper_functions (get_model_name)

customer_agents_tools.*
    ├─→ db.vectorstore_chroma (search_tool)
    └─→ chart_generators.* (create_charts_tool)

db.vectorstore_chroma
    ├─→ utils.prepare_customer_data
    └─→ db.vectorstore (base class)
```

---

## 🔄 Entwicklungs-Workflow

### Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/new-agent

# 2. Develop & test locally
streamlit run streamlit_app.py

# 3. Run tests
python -m pytest tests/

# 4. Commit & push
git add .
git commit -m "feat: Add new agent for X"
git push origin feature/new-agent

# 5. Create Pull Request
```

### Testing Loop

```python
# 1. Write test
def test_new_feature():
    result = my_function()
    assert result == expected

# 2. Run test
pytest tests/test_module.py -v

# 3. Fix & iterate
# 4. Commit when green
```

### Debugging Streamlit App

```powershell
# Debug Mode
streamlit run streamlit_app.py --logger.level=debug

# Mit Profiler
streamlit run streamlit_app.py --profiler
```

**Debugging in Code:**

```python
import streamlit as st

# Temporary debug output
st.write("DEBUG:", variable)
st.json(dict_variable)

# Logging
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Value: {x}")
```

---

## 🤖 Agent-Entwicklung

### Agent-Struktur

Alle Agents folgen diesem Pattern:

```python
from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from utils.helper_functions import get_model_name


def create_my_agent(tools, handoff_agents: list = []):
    """
    Creates My Custom Agent

    Args:
        tools: List of tool functions
        handoff_agents: List of agents for handoffs

    Returns:
        Agent: Configured agent instance
    """
    return Agent(
        name="My Agent Name",
        model=get_model_name("gpt4o_mini"),  # or "gpt4o"
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}

            You are My Agent - specialized in X.

            CRITICAL: All responses MUST be in GERMAN.

            [Detailed instructions here]

            [Tool descriptions]

            [Response format]
        """,
        tools=tools,
    )
```

### Neuen Agent hinzufügen

**Schritt 1: Agent-Datei erstellen**

`customer_agents/my_new_agent.py`:

```python
from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from utils.helper_functions import get_model_name


def create_my_new_agent(my_tool, handoff_agents: list = []):
    """
    Creates My New Agent for specific task
    """
    return Agent(
        name="My New Expert",
        model=get_model_name("gpt4o_mini"),
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}

            You are My New Expert - specialized in [task].

            CRITICAL: All responses MUST be in GERMAN.

            YOUR CAPABILITIES:
            • [Capability 1]
            • [Capability 2]

            TOOL: my_tool_name
            [Tool description]

            WORKFLOW:
            1. [Step 1]
            2. [Step 2]
            3. [Step 3]

            RULES:
            • [Rule 1]
            • [Rule 2]
        """,
        tools=[my_tool],
    )
```

**Schritt 2: Agent in System integrieren**

`utils/helper_functions.py` → `initialize_system()`:

```python
# Import new agent
from customer_agents.my_new_agent import create_my_new_agent

def initialize_system(...):
    # ... existing code ...

    # Create new agent
    my_new_agent = create_my_new_agent(
        my_tool=my_tool,
        handoff_agents=[]  # or other agents
    )

    # Add to handoff list
    customer_manager = create_customer_manager_agent(
        metadata_snapshot=snapshot,
        handoff_agents=[
            feedback_analysis_expert,
            chart_creator_expert,
            my_new_agent  # ← Add here
        ]
    )
```

**Schritt 3: Manager-Agent aktualisieren**

`customer_agents/customer_manager_agent.py`:

Der Manager erkennt neue Agents automatisch durch **dynamic agent detection**:

```python
# In create_customer_manager_agent:
for agent in handoff_agents:
    agent_name = agent.name
    available_agents.append(agent_name)

    # Auto-detect capabilities
    if "My New Expert" in agent_name:
        agent_capabilities[agent_name] = {
            "type": "my_type",
            "description": "Does X"
        }
```

**Schritt 4: Testen**

```python
# Test query
"[Query that should trigger new agent]"
# → Check logs for handoff to "My New Expert"
```

---

## 🛠️ Tool-Entwicklung

### Tool-Struktur

Tools verwenden den `@function_tool` Decorator:

```python
from agents import function_tool


@function_tool
def my_tool_name(
    param1: str,
    param2: int = 10,
    param3: str | None = None
) -> str:
    """
    Brief description of what tool does.

    Args:
        param1 (str): Description of param1
        param2 (int, optional): Description. Default: 10
        param3 (str | None, optional): Description. Default: None

    Returns:
        str: Description of return value

    Examples:
        >>> my_tool_name("test", param2=5)
        "Result"
    """
    # Implementation
    try:
        result = do_something(param1, param2, param3)
        return format_result(result)
    except Exception as e:
        return f"Error: {str(e)}"
```

### Factory Pattern für Tools

**Warum Factory?**

- Dependency Injection (z.B. VectorStore collection)
- Konfigurierbare Tools
- Testbarkeit

**Beispiel:**

```python
class MyToolFactory:
    """Factory for creating my_tool with dependencies"""

    @staticmethod
    def create_tool(dependency):
        """Creates tool with injected dependency"""

        @function_tool
        def my_tool(param: str) -> str:
            """Tool that uses injected dependency"""
            # Use dependency here
            result = dependency.do_something(param)
            return str(result)

        return my_tool
```

**Verwendung:**

```python
# In initialize_system()
my_tool = MyToolFactory.create_tool(dependency=collection)

# Pass to agent
my_agent = create_my_agent(my_tool)
```

### Neues Tool hinzufügen

**Schritt 1: Tool-Datei erstellen**

`customer_agents_tools/my_new_tool.py`:

```python
from agents import function_tool


class MyNewToolFactory:
    @staticmethod
    def create_tool(collection):

        @function_tool
        def my_new_tool(
            query: str,
            max_results: int = 10
        ) -> str:
            """
            Does something useful

            Args:
                query (str): User query
                max_results (int): Number of results

            Returns:
                str: Formatted results
            """
            try:
                # Implementation
                results = collection.query(query, n_results=max_results)
                return format_results(results)
            except Exception as e:
                return f"Error: {str(e)}"

        return my_new_tool
```

**Schritt 2: Tool in System integrieren**

`utils/helper_functions.py`:

```python
from customer_agents_tools.my_new_tool import MyNewToolFactory

def initialize_system(...):
    # ... create collection ...

    # Create new tool
    my_new_tool = MyNewToolFactory.create_tool(collection)

    # Pass to agent that needs it
    my_agent = create_my_agent(my_new_tool)
```

**Schritt 3: Testen**

```python
# Direct tool test
tool = MyNewToolFactory.create_tool(collection)
result = tool(query="test")
print(result)

# Agent test (via Streamlit)
# Ask question that triggers tool
```

---

## 📊 Chart-Generator-Entwicklung

### Chart-Generator-Struktur

Alle Chart-Generatoren befinden sich in `customer_agents_tools/chart_generators/`:

```python
# chart_generators/my_chart.py

import matplotlib.pyplot as plt
from ._shared import save_chart, apply_theme


def generate_my_chart(
    collection,
    market_filter: str | None = None,
    # ... other filters ...
) -> str:
    """
    Generates my custom chart

    Args:
        collection: ChromaDB collection
        market_filter: Optional market filter

    Returns:
        str: Path to saved chart PNG
    """
    try:
        # 1. Query data
        results = collection.get(
            where={"market": market_filter} if market_filter else None
        )

        # 2. Process data
        data = process_results(results)

        # 3. Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        apply_theme(fig, ax)

        # 4. Plot data
        ax.bar(data['x'], data['y'])
        ax.set_title("My Chart Title")
        ax.set_xlabel("X Label")
        ax.set_ylabel("Y Label")

        # 5. Save & return
        chart_path = save_chart(fig, "my_chart")
        return chart_path

    except Exception as e:
        return f"Error: {str(e)}"
```

### Shared Utilities

`chart_generators/_shared.py`:

```python
import matplotlib.pyplot as plt
import os
from datetime import datetime


def save_chart(fig, chart_type: str) -> str:
    """
    Saves chart to charts/ directory with timestamp

    Args:
        fig: Matplotlib figure
        chart_type: Chart type name (for filename)

    Returns:
        str: Absolute path to saved chart
    """
    # Ensure charts directory exists
    os.makedirs("charts", exist_ok=True)

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{chart_type}_{timestamp}.png"
    filepath = os.path.abspath(os.path.join("charts", filename))

    # Save with high DPI
    fig.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close(fig)

    return filepath


def apply_theme(fig, ax):
    """
    Applies consistent theme to chart

    Args:
        fig: Matplotlib figure
        ax: Matplotlib axis
    """
    # Colors
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')

    # Grid
    ax.grid(True, alpha=0.3, linestyle='--')

    # Spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
```

### Neuen Chart-Generator hinzufügen

**Schritt 1: Generator erstellen**

`customer_agents_tools/chart_generators/my_new_chart.py`:

```python
import matplotlib.pyplot as plt
from ._shared import save_chart, apply_theme


def generate_my_new_chart(
    collection,
    # ... parameters ...
) -> str:
    """Generates my new chart"""

    # Implementation (see structure above)
    pass
```

**Schritt 2: In create_charts_tool.py registrieren**

`customer_agents_tools/create_charts_tool.py`:

```python
# Import
from .chart_generators.my_new_chart import generate_my_new_chart

class ChartCreatorToolFactory:
    @staticmethod
    def create_tool(collection):

        @function_tool
        def feedback_analytics(
            chart_type: str,
            # ... existing params ...
        ) -> str:
            """
            Available chart types:
            • ... (existing types)
            • my_new_chart: Description of my new chart
            """

            # Add to dispatch
            if chart_type == "my_new_chart":
                return generate_my_new_chart(
                    collection=collection,
                    # ... pass filters ...
                )

            # ... rest of dispatch ...
```

**Schritt 3: Chart Creator Agent aktualisieren**

`customer_agents/chart_creator_agent.py`:

```python
instructions = f"""
    ...

    AVAILABLE CHART TYPES:
    ...
    My New Category: my_new_chart

    CHART SELECTION LOGIC:
    ...
    if "keyword" in query → my_new_chart

    ...
"""
```

**Schritt 4: Testen**

```python
# Via Streamlit
"Erstelle my_new_chart"

# Direct test
from customer_agents_tools.chart_generators.my_new_chart import generate_my_new_chart

chart_path = generate_my_new_chart(collection)
print(f"Chart saved: {chart_path}")
```

---

## 🧪 Testing & Debugging

### Unit Tests

**Test-Struktur:**

```python
# tests/test_my_module.py

import pytest
from my_module import my_function


class TestMyFunction:
    """Tests for my_function"""

    def test_basic_case(self):
        """Test basic functionality"""
        result = my_function("input")
        assert result == "expected"

    def test_edge_case(self):
        """Test edge case"""
        result = my_function("")
        assert result == ""

    def test_error_handling(self):
        """Test error handling"""
        with pytest.raises(ValueError):
            my_function(None)
```

**Ausführen:**

```powershell
# Alle Tests
pytest

# Spezifisches Modul
pytest tests/test_my_module.py

# Mit Coverage
pytest --cov=./ --cov-report=html

# Verbose
pytest -v -s
```

### Integration Tests

**Test Agents:**

```python
# tests/test_agents.py

from customer_agents.my_agent import create_my_agent
from customer_agents_tools.my_tool import MyToolFactory


def test_agent_with_tool():
    """Test agent uses tool correctly"""

    # Mock collection
    mock_collection = MockCollection()

    # Create tool
    tool = MyToolFactory.create_tool(mock_collection)

    # Create agent
    agent = create_my_agent(tool)

    # Test
    response = agent.run("test query")
    assert "expected" in response
```

### Debugging Tools

**Streamlit Debugging:**

```python
# Show session state
st.sidebar.write("Session State:", st.session_state)

# Show variable
st.write(f"DEBUG: {variable}")

# Show JSON
st.json({"key": "value"})

# Expandable debug section
with st.expander("🐛 Debug Info"):
    st.write("Variable:", variable)
    st.code(str(data))
```

**Logging:**

```python
import logging

# Setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Use
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning")
logger.error("Error", exc_info=True)
```

**OpenAI Agents Tracing:**

```python
# In helper_functions.py
from agents import trace

# Enable tracing for development
trace.enabled = True  # or set_tracing_disabled(False)

# View traces in console
# Shows agent calls, tool executions, etc.
```

### Test Questions

`test/test_questions.py` enthält vordefinierte Test-Fragen:

```python
class TestQuestions:
    META_QUESTIONS = [
        "Wie ist die NPS-Verteilung?",
        # ...
    ]

    FEEDBACK_ANALYSIS_QUESTIONS = [
        "Was sind die Top 5 Beschwerden?",
        # ...
    ]

    # ... more categories ...
```

**Verwendung:**

```python
from test.test_questions import TestQuestions

# Test all meta questions
for question in TestQuestions.META_QUESTIONS:
    response = query_system(question)
    print(f"Q: {question}")
    print(f"A: {response}\n")
```

---

## ⚡ Performance-Tuning

### Profiling

**Streamlit Profiler:**

```powershell
streamlit run streamlit_app.py --profiler
# Opens profiler UI
```

**Python Profiler:**

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
my_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumtime')
stats.print_stats(20)  # Top 20
```

### Optimization Strategies

**1. Caching**

```python
@st.cache_resource  # Singleton across sessions
def expensive_init():
    return initialize_something()

@st.cache_data(ttl=60)  # Cache for 60 seconds
def expensive_compute(param):
    return compute(param)
```

**2. Batch Processing**

```python
# Bad: Individual processing
for item in items:
    process(item)  # N API calls

# Good: Batch processing
batches = [items[i:i+100] for i in range(0, len(items), 100)]
for batch in batches:
    process_batch(batch)  # N/100 API calls
```

**3. Lazy Loading**

```python
# Bad: Load everything at start
data = load_all_data()

# Good: Load on demand
@st.cache_data
def get_data():
    if "data" not in st.session_state:
        st.session_state.data = load_all_data()
    return st.session_state.data
```

**4. Streaming**

```python
# Bad: Wait for complete response
response = agent.run(query)  # Blocks
st.write(response)

# Good: Stream tokens
async for token in agent.run_stream(query):
    st.write(token)  # Immediate feedback
```

### Monitoring

**Track Performance:**

```python
import time

start = time.time()
result = expensive_function()
duration = time.time() - start

logger.info(f"Function took {duration:.2f}s")

# In production
metrics = {
    "function": "expensive_function",
    "duration": duration,
    "timestamp": time.time()
}
# Send to monitoring system
```

---

## 🚀 Deployment

### Production Checklist

- [ ] Environment variables configured (`.env` not in repo!)
- [ ] Dependencies pinned in `requirements.txt`
- [ ] Error handling für alle external calls
- [ ] Logging konfiguriert
- [ ] API Keys in Secrets Manager (nicht in Code!)
- [ ] HTTPS aktiviert
- [ ] Rate limiting implementiert
- [ ] Monitoring setup
- [ ] Backup-Strategie für VectorStore

### Streamlit Cloud Deployment

```powershell
# 1. Push to GitHub
git add .
git commit -m "Prepare for deployment"
git push origin main

# 2. Streamlit Cloud
# → New app
# → Connect GitHub repo
# → Set environment variables in Secrets
# → Deploy
```

**Secrets Configuration:**

```toml
# .streamlit/secrets.toml (only on Streamlit Cloud)
OPENAI_API_KEY = "sk-..."
AZURE_OPENAI_API_KEY = "..."
# ... etc
```

### Docker Deployment

**Dockerfile:**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501"]
```

**Build & Run:**

```powershell
# Build
docker build -t feedback-rag-system .

# Run
docker run -p 8501:8501 `
    -e OPENAI_API_KEY="sk-..." `
    feedback-rag-system
```

---

## 📚 API-Referenz

### Core Functions

#### `initialize_system()`

```python
def initialize_system(
    is_azure_openai: bool,
    csv_path: str,
    vectorstore_type: str = "chroma",
    create_new_store: bool = False,
    embedding_model: str = "text-embedding-ada-002",
    is_synthetic_data: bool = False
) -> tuple[Agent, Collection]:
    """
    Initializes the complete RAG system

    Args:
        is_azure_openai: Use Azure OpenAI?
        csv_path: Path to CSV data
        vectorstore_type: Type of vectorstore
        create_new_store: Force recreation?
        embedding_model: Embedding model name
        is_synthetic_data: Using synthetic data?

    Returns:
        tuple: (customer_manager_agent, collection)
    """
```

#### `process_query_streamed()`

```python
async def process_query_streamed(
    customer_manager: Agent,
    user_input: str,
    session: SQLiteSession,
    history_limit: int
) -> AsyncGenerator[str | dict, None]:
    """
    Processes query with streaming response

    Args:
        customer_manager: Manager Agent instance
        user_input: User question
        session: SQLite session for agents
        history_limit: Max history turns

    Yields:
        str | dict: Tokens or chart info
    """
```

### VectorStore API

#### `ChromaVectorStore`

```python
class ChromaVectorStore(VectorStore):
    """ChromaDB implementation of VectorStore"""

    def __init__(
        self,
        data: pd.DataFrame,
        file_path: str = ".",
        file_name: str = "vectorstore",
        collection_name: str = "customer_feedback",
        batch_size: int = 100,
        embedding_model: str = "text-embedding-ada-002"
    ):
        """Initialize ChromaDB VectorStore"""

    def load(self) -> Collection:
        """
        Creates VectorStore from DataFrame

        Returns:
            Collection: ChromaDB collection
        """
```

### Agent API

#### `create_customer_manager_agent()`

```python
def create_customer_manager_agent(
    metadata_snapshot: Dict[str, str],
    handoff_agents: Optional[list] = None
) -> Agent:
    """
    Creates Customer Manager Agent

    Args:
        metadata_snapshot: Pre-computed metadata
        handoff_agents: List of specialist agents

    Returns:
        Agent: Configured manager agent
    """
```

### Tool API

#### `@function_tool` Decorator

```python
from agents import function_tool

@function_tool
def my_tool(param: str) -> str:
    """
    Tool docstring (shown to LLM!)

    Args:
        param: Parameter description

    Returns:
        str: Return value description
    """
    return "result"
```

---

## 💡 Best Practices

### Code Style

**Type Hints:**

```python
# ✅ Good
def process_data(data: pd.DataFrame, limit: int = 10) -> list[dict]:
    """Process data with type hints"""
    pass

# ❌ Bad
def process_data(data, limit=10):
    """No type hints"""
    pass
```

**Docstrings:**

```python
# ✅ Good: Comprehensive docstring
def my_function(param: str) -> str:
    """
    Brief description.

    Detailed description with examples.

    Args:
        param (str): Parameter description

    Returns:
        str: Return value description

    Raises:
        ValueError: When param is invalid

    Examples:
        >>> my_function("test")
        "result"
    """
    pass
```

**Error Handling:**

```python
# ✅ Good: Specific exceptions
try:
    result = risky_operation()
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    return None
except PermissionError as e:
    logger.error(f"Permission denied: {e}")
    return None

# ❌ Bad: Bare except
try:
    result = risky_operation()
except:  # Catches everything!
    pass
```

### Agent Instructions

**✅ Best Practices:**

1. **Clear Role Definition**

   ```
   You are the [Name] - specialized in [task].
   ```

2. **German Language Enforcement**

   ```
   CRITICAL: All responses MUST be in GERMAN.
   ```

3. **Step-by-Step Reasoning**

   ```
   WORKFLOW:
   1. Step 1
   2. Step 2
   3. Step 3
   ```

4. **Explicit Rules**

   ```
   RULES:
   • Rule 1
   • Rule 2
   ```

5. **Tool Documentation**

   ```
   TOOL: tool_name
   Parameters:
   • param1 (type): Description
   • param2 (type, optional): Description. Default: X
   ```

6. **Examples**
   ```
   EXAMPLES:
   Query: "..."
   → Action: tool_name(param="...")
   ```

### Performance

**✅ Do:**

- Cache expensive operations
- Use batch processing where possible
- Implement streaming for better UX
- Limit history to control costs
- Pre-compute metadata

**❌ Don't:**

- Load all data into memory
- Make unnecessary API calls
- Ignore caching opportunities
- Use unbounded loops
- Forget error handling

### Security

**✅ Do:**

- Store API keys in `.env`
- Validate all user inputs
- Use environment variables
- Implement rate limiting
- Log security events

**❌ Don't:**

- Hardcode API keys
- Trust user input
- Expose internal errors to users
- Allow unrestricted access
- Log sensitive data

---

## 🐛 Troubleshooting

### Common Issues

#### Issue: "ModuleNotFoundError"

**Symptom:**

```
ModuleNotFoundError: No module named 'agents'
```

**Solution:**

```powershell
# Check venv activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

---

#### Issue: VectorStore creation fails

**Symptom:**

```
Error creating VectorStore: ...
```

**Solutions:**

1. **Check CSV file**

   ```python
   import pandas as pd
   df = pd.read_csv("data/feedback_data.csv")
   print(df.columns)  # Must have: NPS, Verbatim, Market, Date
   ```

2. **Delete old VectorStore**

   ```powershell
   Remove-Item -Recurse -Force .\chroma\
   ```

3. **Check OpenAI API Key**
   ```powershell
   echo $env:OPENAI_API_KEY
   ```

---

#### Issue: Agent doesn't use tool

**Symptom:** Agent answers without calling tool

**Debug:**

```python
# Enable tracing
from agents import trace
trace.enabled = True

# Check agent instructions
print(agent.instructions)

# Check tool docstring (must be detailed!)
print(tool.__doc__)
```

**Solutions:**

1. Improve tool docstring (LLM reads it!)
2. Make instructions more explicit
3. Add examples in instructions

---

#### Issue: Charts not displaying

**Symptom:** Chart marker visible but no image

**Solutions:**

1. **Check charts directory**

   ```powershell
   New-Item -ItemType Directory -Force -Path .\charts\
   ```

2. **Check file paths**

   ```python
   # Must be absolute path
   chart_path = os.path.abspath("charts/chart.png")
   ```

3. **Clear Streamlit cache**
   ```powershell
   streamlit cache clear
   ```

---

#### Issue: Slow responses

**Causes & Solutions:**

1. **Too much history**

   ```python
   HISTORY_LIMIT = 3  # Reduce from 4+
   ```

2. **Large max_results**

   ```python
   # In search queries
   max_results = 10  # Not 30+
   ```

3. **Not using caching**
   ```python
   @st.cache_resource
   def init():
       # Cached!
   ```

---

## 📞 Support & Resources

### Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** - For end users
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[QUICK_START.md](../QUICK_START.md)** - Quick setup

### External Resources

- [Streamlit Docs](https://docs.streamlit.io/)
- [OpenAI Agents SDK](https://github.com/openai/openai-python)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [LangChain Docs](https://python.langchain.com/)

### Community

- GitHub Issues (if available)
- Stack Overflow (tag: streamlit, openai, rag)

---

**Happy Coding! 💻🚀**

Viel Erfolg bei der Entwicklung!
