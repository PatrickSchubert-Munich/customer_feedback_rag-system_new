# 🚀 Quick Start Guide

> Starten Sie das Customer Feedback RAG System in wenigen Minuten!

---

## 📋 Voraussetzungen

Bevor Sie beginnen, stellen Sie sicher, dass Sie Folgendes haben:

- ✅ **Python 3.12 oder höher** ([Download](https://www.python.org/downloads/))
- ✅ **uv** - Schneller Python Package Manager ([Installation](https://docs.astral.sh/uv/getting-started/installation/))
- ✅ **OpenAI API Key** ([Registrierung](https://platform.openai.com/signup))
- ✅ **Git** (optional, für Klonen des Repos)
- ✅ **PowerShell** oder Command Prompt (Windows)

---

## 🎯 Installation in 4 Schritten

### Schritt 1: Projekt herunterladen

**Option A: Mit Git**

```powershell
git clone <repository-url>
cd customer_feedback_rag-system_new
```

**Option B: Als ZIP**

1. Repository als ZIP herunterladen
2. ZIP entpacken
3. Im Terminal zum Projektverzeichnis navigieren

---

### Schritt 2: uv installieren (falls noch nicht vorhanden)

```powershell
# Für Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Oder mit winget
winget install --id=astral-sh.uv -e

# Oder mit pip (falls Python bereits installiert)
pip install uv
```

**Warum uv?**

- ⚡ **10-100x schneller** als pip
- 🔒 **Automatisches Virtual Environment Management**
- 📦 **Integrierte Dependency Resolution**
- 🎯 **Kompatibel mit requirements.txt & pyproject.toml**

---

### Schritt 3: Projekt-Umgebung initialisieren und Dependencies installieren

```powershell
# uv erstellt automatisch ein Virtual Environment und installiert alle Dependencies
uv sync

# Oder mit requirements.txt (falls pyproject.toml nicht genutzt wird)
uv pip install -r requirements.txt
```

**Was passiert hier?**

- ✅ uv erstellt automatisch ein `.venv` Virtual Environment
- ✅ Installiert alle Dependencies aus `pyproject.toml` (oder `requirements.txt`)
- ✅ Locked Dependencies für reproduzierbare Builds
- ✅ Alles in einem Befehl!

**Wichtige Pakete die installiert werden:**

- `streamlit` - Web-Interface
- `openai` - OpenAI API Client
- `chromadb` - VectorStore
- `langchain` - Agent-Framework
- `pandas` - Datenverarbeitung
- `matplotlib` - Visualisierung
- `vadersentiment` - Sentiment-Analyse

**Alternative: Manuell installieren (falls sync nicht funktioniert)**

```powershell
# Virtual Environment erstellen
uv venv

# Environment aktivieren (optional - uv macht das automatisch)
# PowerShell:
.venv\Scripts\Activate.ps1
# CMD:
.venv\Scripts\activate.bat

# Dependencies installieren
uv pip install -r requirements.txt
```

---

### Schritt 4: Umgebungsvariablen konfigurieren

**Option A: .env Datei (Empfohlen)**

1. Erstellen Sie eine `.env` Datei im Projektverzeichnis:

```bash
# .env Datei
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

2. Oder für Azure OpenAI:

```bash
# Azure OpenAI Konfiguration
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_DEPLOYMENT_NAME_MINI=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002
```

**Option B: Umgebungsvariable setzen (temporär)**

```powershell
# Für aktuelle PowerShell-Session
$env:OPENAI_API_KEY="sk-proj-your-actual-api-key-here"
```

---

### Schritt 5: Applikation starten

```powershell
# Mit uv (automatisch im richtigen Environment)
uv run streamlit run streamlit_app.py

# Oder wenn Environment bereits aktiviert
streamlit run streamlit_app.py
```

✅ **Fertig!** Die App öffnet sich automatisch im Browser unter:

```
http://localhost:8501
```

**Hinweis:** `uv run` aktiviert automatisch das Virtual Environment und führt den Befehl aus - keine manuelle Aktivierung nötig!

---

## 🎬 Erster Start

Beim ersten Start der Applikation:

1. **VectorStore wird erstellt** (einmalig, dauert ~30-60 Sekunden)

   ```
   🔄 VectorStore wird erstellt...
   📊 Lade CSV-Daten...
   🧠 Erstelle Embeddings...
   ✅ VectorStore bereit!
   ```

2. **Chat-Interface erscheint**

   - Willkommensnachricht wird angezeigt
   - Beispielanfragen sind verfügbar
   - System ist bereit für Ihre Fragen

3. **Erste Anfrage testen**
   - Klicken Sie auf eine der Beispielanfragen
   - Oder geben Sie eine eigene Frage ein
   - Warten Sie auf die KI-Antwort (Streaming)

---

## 💡 Beispiel-Workflow

### 1. Metadaten-Abfrage (Schnell)

```
Frage: "Wie ist die NPS-Verteilung in deinem Datensatz?"

Antwort: Customer Manager antwortet direkt aus Metadaten-Snapshot
         (keine Tool-Calls nötig, sehr schnell)
```

### 2. Feedback-Analyse (Semantic Search)

```
Frage: "Was sind die Top 5 Beschwerden?"

Workflow:
1. Customer Manager → Handoff zu Feedback Analysis Expert
2. Feedback Analysis Expert → search_customer_feedback Tool
3. Feedback Analysis Expert → transfer_to_output_summarizer
4. Output Summarizer → Formatiert Ergebnisse als Business-Report
```

### 3. Visualisierung (Chart-Generierung)

```
Frage: "Erstelle ein Balkendiagramm der Top 5 Themen mit NPS-Scores"

Workflow:
1. Customer Manager → Handoff zu Chart Creator Expert
2. Chart Creator Expert → create_chart Tool (topic_bar_chart)
3. Chart wird als PNG gespeichert
4. Chart wird im Chat angezeigt
```

---

## ⚙️ Konfiguration (Optional)

### Datenquelle wechseln

Öffnen Sie `streamlit_app.py` und ändern Sie Zeile 42:

```python
# Synthetische Daten nutzen (Standard)
USE_SYNTHETIC_DATA = True

# Original-Daten nutzen
USE_SYNTHETIC_DATA = False
```

### Historie-Limit anpassen

In `streamlit_app.py` Zeile 59:

```python
# Anzahl der Historie-Turns die an LLM gesendet werden
HISTORY_LIMIT = 4  # Empfohlen: 3-5
# None = unbegrenzt (teuer!)
```

### VectorStore neu erstellen

In `streamlit_app.py` Zeile 50:

```python
# ACHTUNG: Löscht vorhandenen VectorStore!
FORCE_RECREATE_VECTORSTORE = True
```

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError"

**Lösung:**

```powershell
# Dependencies erneut mit uv installieren
uv sync

# Oder manuell
uv pip install -r requirements.txt

# Oder mit uv run (nutzt automatisch das richtige Environment)
uv run streamlit run streamlit_app.py
```

---

### Problem: "OpenAI API Key not found"

**Lösung:**

```powershell
# API Key setzen
$env:OPENAI_API_KEY="sk-proj-your-key"

# Oder .env Datei erstellen (siehe Schritt 4)
```

---

### Problem: "Port 8501 already in use"

**Lösung:**

```powershell
# Anderen Port nutzen (mit uv)
uv run streamlit run streamlit_app.py --server.port 8502

# Oder laufende Streamlit-Prozesse beenden
Get-Process streamlit | Stop-Process
```

---

### Problem: VectorStore-Erstellung schlägt fehl

**Lösung:**

```powershell
# Alte VectorStore-Daten löschen
Remove-Item -Recurse -Force .\chroma\

# App neu starten (mit uv)
uv run streamlit run streamlit_app.py
```

---

### Problem: "Rate limit exceeded" (OpenAI)

**Ursache:** Zu viele API-Anfragen in kurzer Zeit

**Lösung:**

- Warten Sie 1-2 Minuten
- Reduzieren Sie `HISTORY_LIMIT` in `streamlit_app.py`
- Nutzen Sie kleinere Modelle (gpt-4o-mini statt gpt-4o)
- Upgrade Ihren OpenAI Plan

---

### Problem: Charts werden nicht angezeigt

**Lösung:**

```powershell
# Überprüfen, ob charts/ Verzeichnis existiert
New-Item -ItemType Directory -Force -Path .\charts\

# Streamlit Cache löschen
streamlit cache clear

# App neu starten
```

---

## 📊 Performance-Optimierung

### Installation-Performance mit uv

**uv ist deutlich schneller als pip:**

- 📦 Dependency Installation: **10-100x schneller**
- 🔍 Dependency Resolution: **Instant** (vs. Minuten bei pip)
- 💾 Disk Space: **Effizientere Caching-Strategie**

**Vergleich:**

```
pip install -r requirements.txt    → ~2-3 Minuten
uv pip install -r requirements.txt → ~10-20 Sekunden
```

### Für schnellere Antworten

1. **Historie begrenzen**

   ```python
   HISTORY_LIMIT = 3  # Weniger Kontext = schneller
   ```

2. **Mini-Modell nutzen**

   ```python
   # In helper_functions.py get_model_name()
   # Nutzt automatisch gpt-4o-mini für Agents
   ```

3. **VectorStore-Cache nutzen**
   - Erstellen Sie VectorStore einmalig
   - Setzen Sie `FORCE_RECREATE_VECTORSTORE = False`

### Für bessere Qualität

1. **Mehr Historie**

   ```python
   HISTORY_LIMIT = 6  # Mehr Kontext = bessere Antworten
   ```

2. **GPT-4o nutzen**
   - Ändern Sie in `helper_functions.py` die Modell-Auswahl
   - Höhere Kosten, aber bessere Qualität

---

## 🎯 Nächste Schritte

Jetzt wo die App läuft:

1. 📚 Lesen Sie den **[USER_GUIDE.md](docs/USER_GUIDE.md)** für detaillierte Feature-Beschreibungen
2. 🏗️ Verstehen Sie die Architektur in **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**
3. 💻 Entwickeln Sie weiter mit **[DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)**

---

## 🆘 Weitere Hilfe

- **Benutzer-Probleme:** Siehe [USER_GUIDE.md](docs/USER_GUIDE.md)
- **Entwickler-Fragen:** Siehe [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)
- **Architektur-Details:** Siehe [ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## ✅ Checkliste

- [ ] Python 3.12+ installiert
- [ ] uv installiert (`uv --version` zum Testen)
- [ ] Repository geklont/heruntergeladen
- [ ] Dependencies mit uv installiert (`uv sync` oder `uv pip install -r requirements.txt`)
- [ ] OpenAI API Key konfiguriert (`.env` Datei)
- [ ] App gestartet (`uv run streamlit run streamlit_app.py`)
- [ ] Erste Testfrage gestellt
- [ ] VectorStore erfolgreich erstellt

---

## 💎 uv - Erweiterte Features

### Warum uv statt pip/venv?

**Performance:**

- ⚡ **10-100x schneller** bei Package-Installation
- 🚀 **Paralleles Downloading** von Packages
- 💨 **Instant Dependency Resolution** (keine lange Wartezeiten)

**Komfort:**

- 🎯 **Automatisches Virtual Environment Management** - kein manuelles Aktivieren nötig
- 🔒 **Lock-Files** für reproduzierbare Builds
- 📦 **Kompatibel** mit pip, requirements.txt & pyproject.toml
- 🛠️ **Eingebaute Tools** für Projekt-Management

**Weitere uv Befehle:**

```powershell
# Überprüfen Sie die uv Version
uv --version

# Projekt initialisieren (erstellt pyproject.toml)
uv init

# Dependencies hinzufügen
uv add streamlit openai

# Dependencies entfernen
uv remove package-name

# Python-Version wechseln
uv python install 3.12

# Alle verfügbaren Python-Versionen zeigen
uv python list

# Projekt-Info anzeigen
uv tree
```

**Ressourcen:**

- 📖 [uv Dokumentation](https://docs.astral.sh/uv/)
- 🐙 [GitHub Repository](https://github.com/astral-sh/uv)
- 💬 [Discord Community](https://discord.gg/astral-sh)

---

**Viel Erfolg! 🚀**

Bei Problemen: Siehe [Troubleshooting](#-troubleshooting) oder kontaktieren Sie den Support.
