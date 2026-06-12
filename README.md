# 🚀 Trend Intelligence System

A personal intelligence platform that collects, analyzes, and organizes information from AI, cybersecurity, startup, and technology ecosystems.

The goal is to reduce information overload and transform raw information into structured intelligence, trend signals, and actionable insights.

## Features

### Data Collection

* RSS feed monitoring
* GitHub trend tracking
* arXiv research collection
* Hacker News monitoring

### Intelligence Layer

* Content extraction
* Duplicate detection
* LLM-powered analysis
* Topic normalization
* Trend scoring
* Opportunity detection
* Intelligence report generation

## Architecture

```text
Sources
(RSS, GitHub, arXiv, HN)
        ↓
Data Collection
        ↓
Deduplication
        ↓
Content Extraction
        ↓
LLM Analysis
        ↓
Trend & Signal Scoring
        ↓
Reports
```

## Project Structure

```text
.
├── main.py
├── analyzer.py
├── reporter.py
│
├── collectors/
│   ├── rss_collector.py
│   ├── github_collector.py
│   ├── arxiv_collector.py
│   └── hackernews_collector.py
│
├── engines/
│   ├── trend_engine.py
│   ├── signal_engine.py
│   └── opportunity_engine.py
│
├── reports/
├── stats/
└── utils.py
```

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/Trend_Intelligence.git

cd Trend_Intelligence

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / Mac
source .venv/bin/activate

pip install -r requirements.txt
```

## Model Setup

### Local Models (Ollama)

Install Ollama and pull the default model:

```bash
ollama pull qwen2.5:3b
ollama serve
```

### API-Based Models

Create a `.env` file:

```env
LLM_PROVIDER=gemini
API_KEY=your_api_key
MODEL_NAME=gemini-2.5-flash
```

Supported providers:

* Gemini
* OpenAI
* Anthropic
* Groq
* OpenRouter
* Together AI

## Environment Variables

```env
GITHUB_TOKEN=your_github_token

LLM_PROVIDER=gemini
API_KEY=your_api_key
MODEL_NAME=gemini-2.5-flash
```

## Usage

Run the complete pipeline:

```bash
python main.py full
```

Or execute individual stages:

```bash
python main.py collect
python main.py analyze
python main.py report
```

## Current Status

### V1 Stable

* Multi-source collection
* LLM analysis pipeline
* Trend scoring
* Opportunity detection
* Report generation

## Roadmap

### V2

* SQLite integration
* Improved caching
* Better deduplication

### V3

* Vector database integration
* Semantic search
* Knowledge retrieval

### V4

* Trend clustering
* Topic evolution tracking
* Signal acceleration detection

### V5

* Dashboard
* Interactive visualizations
* Automated alerts

## License

MIT License.

```
```
