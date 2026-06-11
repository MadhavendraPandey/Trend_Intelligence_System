# Trend Intelligence System: Architecture Review & Migration Plan

## 1. Current Architecture Assessment

### Strengths
- **Modular Pipeline**: Clear separation between collection, filtering, analysis, and reporting.
- **Topic Normalization**: Robust hierarchy for mapping diverse content to structured topics.
- **LLM Integration**: Uses Qwen 2.5:3b for deep semantic analysis of articles.
- **Scoring Logic**: Multi-dimensional scoring (trend, signal, opportunity) provides a sophisticated view of data.

### Weaknesses
- **State Management**: Heavy reliance on `articles.json` causes concurrency issues and limits scalability.
- **Import Hacks**: Use of `sys.path.insert` and `subprocess.run` instead of proper package structures.
- **Broken Reporter**: The reporter is misaligned with the current engine outputs.
- **Lack of History**: No mechanism to track trend changes over time, making "Trend Acceleration" impossible.
- **Single-Threaded Collectors**: Performance bottleneck when fetching from many sources.

### Technical Debt & Scaling Bottlenecks
- **JSON Storage**: Becomes slow as the dataset grows; prone to corruption during concurrent writes.
- **Hardcoded Configs**: Source lists and topic hierarchies are embedded in code.
- **Fault Tolerance**: Limited retry logic and error handling in collectors.

---

## 2. Package Structure

Ideal structure utilizing Python's package system:

```text
trend_intelligence/
├── collectors/          # Data fetchers (RSS, GitHub, Arxiv, etc.)
│   ├── __init__.py
│   ├── base.py          # BaseCollector interface
│   ├── rss_collector.py
│   └── ...
├── engines/             # Analytical logic
│   ├── __init__.py
│   ├── trend_engine.py
│   ├── signal_strength.py
│   ├── trend_acceleration.py
│   └── ...
├── filters/             # Pre-analysis content filters
├── models/              # LLM wrappers
├── reports/             # Generated outputs (Daily/Weekly)
├── sources/             # Source definitions (Config-based)
├── stats/               # Collection metrics
├── storage/             # Data persistence layer
│   ├── __init__.py
│   ├── sqlite_storage.py
│   └── snapshot_manager.py
├── main.py              # Orchestrator
├── analyzer.py          # LLM processing script
├── reporter.py          # Report generator
└── utils.py             # Shared utilities
```

---

## 3. Data Layer

**Recommendation: SQLite**

### Why?
- **Relational Integrity**: Handles the links between Articles, Analysis, Topics, and Signals.
- **Concurrency**: Better handles simultaneous read/writes than JSON.
- **Historical Queries**: Essential for "Trend Acceleration" to compare T vs T-1.
- **Simplicity**: Zero-config, single file, yet production-grade for this scale.

---

## 4. Collector Layer

### Recommendations
- **BaseCollector**: Implement a class-based structure for collectors to share retry logic, rate limiting, and stats tracking.
- **Concurrency**: Use `ThreadPoolExecutor` or `asyncio` for HTTP requests to significantly speed up collection.
- **Fault Tolerance**: Implement exponential backoff for API errors.
- **Batching**: Database writes should be batched per category to optimize IO.

---

## 5. Analysis Layer

### Review
- **Model**: Qwen 2.5:3b is efficient for local use.
- **Schema**: Current schema is good but should move towards **Pydantic** for strict validation.
- **Processing**: Implement a "Priority Queue" based on source quality and relevance score to analyze high-value items first.

---

## 6. Engine Layer

### Current Flaws
- Engines operate on lists of dictionaries in memory; they should be refactored to accept query-able objects or directly interface with the storage layer for large datasets.
- **Trend Acceleration** is currently a stub because it lacks historical data.

### Proposed Architecture
- **Data-Driven Engines**: Engines should fetch data from SQLite based on time windows.
- **Stateless Analysis**: Engines calculate metrics and return them to the orchestrator/reporter.

---

## 7. Historical Snapshots

### Design
- **Table**: `snapshots` (id, timestamp, engine_type, snapshot_data_json).
- **Storage**: Store the aggregated results of Trend and Signal engines daily.
- **Retention**: Keep daily snapshots for 30 days, weekly for 12 months.
- **Purpose**: Power the `Trend Acceleration` engine by providing a baseline for comparison.

---

## 8. Reporter Redesign

### Design
The new reporter will unify the engine outputs into a comprehensive dashboard.

**Report Structure:**
1.  **Executive Summary**: High-level system health and top 3 "Breakout" opportunities.
2.  **Trend Landscape**: Top trends with acceleration markers (↑, ↓, →).
3.  **Opportunity Radar**: Matrix of Signal Strength vs. Actionability.
4.  **Strategic Recommendations**: Categorized as Build, Learn, or Monitor.
5.  **Data Funnel**: Visualization of the collection stats.

---

## 9. Production Roadmap

### V1: Foundation (Current Goal)
- Migrate to SQLite.
- Fix package structure/imports.
- Implement basic snapshots.
- Fix Reporter-Engine alignment.

### V2: Performance & Quality
- Async collectors.
- Pydantic validation for LLM outputs.
- Enhanced topic hierarchy.

### V3: Intelligence
- Multi-model analysis (using larger models for high-priority items).
- Sentiment analysis on HN/Reddit comments.
- Advanced anomaly detection.

### V4: Platform
- Web Dashboard (Streamlit or FastAPI/React).
- Alerting system (Slack/Email).
- API for external integrations.

---

## 10. Technical Debt Audit

1.  **Articles.json**: Must be deprecated immediately.
2.  **Sys.path hacks**: Violates PEP 8 and makes the project hard to install.
3.  **Lack of Tests**: No unit tests for scoring logic or filters.
4.  **Error Handling**: Collectors often crash on malformed RSS feeds.
5.  **Ollama Dependency**: Hardcoded URL/Model; should be configurable.
