# 🚀 Trend Intelligence System (V1 Stable)

A personal intelligence platform for collecting, filtering, and analyzing high-signal information across AI, cybersecurity, startups, and developer ecosystems. This system reduces information overload by transforming raw data into actionable trends and strategic recommendations.

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Current Status](#-current-status-v1)
- [Roadmap](#-roadmap)

---

## 🌟 Overview

The Trend Intelligence System is a modular data pipeline that automates the discovery of emerging technologies and industry shifts. It collects data from primary sources, applies multi-stage filtering, performs semantic analysis using Local LLMs, and generates comprehensive intelligence reports.

### The Pipeline
1.  **Collect**: Multi-source ingestion (RSS, GitHub, arXiv, Hacker News).
2.  **Analyze**: Semantic processing and scoring using Ollama (`qwen2.5:3b`).
3.  **Report**: Generation of Markdown and JSON intelligence dashboards.

---

## ✨ Features

### Data Collectors
*   **RSS Feeds**: Monitors top-tier tech and security publications (BleepingComputer, Krebs, OpenAI, etc.).
*   **GitHub**: Tracks trending repositories, coding agents, and framework updates.
*   **arXiv**: Ingests the latest research papers in AI and cryptography.
*   **Hacker News**: Captures community-driven signals and breakout discussions.

### Intelligence Layer
*   **Topic Normalization**: Maps diverse mentions to a structured topic hierarchy.
*   **Scoring Engines**:
    *   **Trend Engine**: Measures topic volume and source diversity.
    *   **Signal Strength**: Evaluates community engagement and research backing.
    *   **Opportunity Engine**: Identifies high-potential "breakout" topics.
    *   **Strategic Advisor**: Categorizes topics into **Build**, **Learn**, or **Monitor**.

---

## 🛠 Installation

### 1. Prerequisites
*   Python 3.10+
*   [Ollama](https://ollama.com/) (required for the analysis stage)

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/Trend_Intelligence.git
cd Trend_Intelligence

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Model Setup
Ensure Ollama is installed and running, then pull the required model:
```bash
ollama pull qwen2.5:3b
```

---

## ⚙️ Configuration

Create a `.env` file in the root directory to enable the GitHub collector:
```env
GITHUB_TOKEN=your_github_personal_access_token
```

---

## 📖 Usage

The system is orchestrated through `main.py`. You can run individual stages or the full pipeline.

### Full Pipeline
```bash
python main.py full
```

### Individual Stages
```bash
# Collect raw data from all configured sources
python main.py collect

# Run LLM-based semantic analysis on new items
python main.py analyze

# Generate intelligence reports (Markdown and JSON)
python main.py report
```

---

## 📂 Project Structure

```text
.
├── main.py              # System orchestrator
├── analyzer.py          # LLM analysis and schema validation
├── reporter.py          # Report generation engine
├── collectors/          # Source-specific fetchers (RSS, GitHub, etc.)
├── engines/             # Scoring and analytical logic
├── filters/             # Content, duplicate, and quality filters
├── models/              # LLM interface (Ollama)
├── sources/             # Source configurations and feed lists
├── stats/               # Collection performance metrics
├── reports/             # Generated Markdown/JSON output files
└── utils.py             # Shared storage and string utilities
```

---

## 📈 Current Status (V1)

The system has successfully completed a V1 stabilization audit, ensuring a robust and reliable pipeline.

*   ✅ **Source Collectors**: Fully operational RSS, GitHub, arXiv, and HN integrations.
*   ✅ **LLM Analysis**: Stable connection to Ollama with retry logic and JSON schema enforcement.
*   ✅ **Engine Logic**: Aligned Trend, Signal, and Opportunity scoring.
*   ✅ **Package Architecture**: Standardized Python package structure with direct-import orchestration.
*   ✅ **Duplicate Detection**: Robust URL-based indexing and filtering.

---

## 🗺 Roadmap

*   **V2 Data Layer**: Migration from `articles.json` to SQLite for enhanced performance and concurrency.
*   **Async Ingestion**: Leveraging `asyncio` for high-throughput concurrent collection.
*   **Web Dashboard**: Streamlit or React-based visualization layer.
*   **Historical Analysis**: Tracking trend acceleration and decay over time.

---

## ⚖️ License

MIT License. See [LICENSE](LICENSE) for details.
