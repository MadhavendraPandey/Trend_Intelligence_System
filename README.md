# Trend Intelligence System

A personal intelligence platform designed to reduce information overload and identify emerging developments in AI, cybersecurity, startups, and technology.

The goal is to automatically collect information from multiple sources, extract the important signals, generate structured analysis, and build a searchable knowledge base for future trend detection.

---

## Problem

Every day hundreds of articles, research papers, startup announcements, and security reports are published.

Manually tracking them is slow, inconsistent, and difficult to scale.

This project aims to automate the intelligence gathering process by creating a pipeline that:

* Collects information from trusted sources
* Extracts article content
* Removes duplicates
* Uses AI to analyze articles
* Stores structured intelligence for future trend analysis

---

## Current Capabilities

### RSS Feed Ingestion

Collects articles from multiple sources including:

* The Hacker News
* Bleeping Computer
* TechCrunch Startups
* Hugging Face Blog

### Content Extraction

Downloads article pages and extracts the main content using Trafilatura.

### Deduplication

Prevents previously processed articles from being analyzed multiple times.

### AI-Powered Analysis

Uses Gemini to generate structured intelligence including:

* Overview
* Tags
* Importance Score
* Key Points
* Why It Matters

### JSON Knowledge Storage

Stores articles and analysis in a structured JSON format for future processing.

---

## Current Pipeline

RSS Sources
↓
Feed Parsing
↓
Content Extraction
↓
Deduplication
↓
AI Analysis
↓
Structured JSON Storage

---

## Example Intelligence Output

```json
{
  "overview": "...",
  "tags": [
    "AI",
    "Cybersecurity"
  ],
  "importance": 4,
  "key_points": [
    "...",
    "...",
    "..."
  ],
  "why_it_matters": "..."
}
```

---

## Technology Stack

* Python
* Feedparser
* Trafilatura
* Gemini API
* JSON
* python-dotenv

---

## Installation

```bash
git clone <repository-url>

cd Trend_Intelligence_System

pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

Run:

```bash
python collector.py
```

---

## Roadmap

### Version 3

* Better project structure
* Logging
* Error handling
* Feed management improvements

### Version 4

* Topic classification
* Trend clustering
* Signal scoring

### Version 5

* Vector database
* Semantic search
* Knowledge retrieval

### Version 6

* Trend detection engine
* Weekly intelligence reports
* Automated alerts

### Version 7

* Dashboard and visualization layer

---

## Project Status

Active development.

This project is being built incrementally as a practical exercise in data engineering, automation, AI systems, cybersecurity intelligence collection, and trend analysis.
