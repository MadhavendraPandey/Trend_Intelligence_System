# Trend Intelligence System Migration Report

## Final Repository Tree

```text
Trend_Intelligence_System/
├── config/
├── core/
│   ├── __init__.py
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── arxiv_collector.py
│   │   ├── github_collector.py
│   │   ├── hackernews_collector.py
│   │   ├── reddit_collector.py
│   │   └── rss_collector.py
│   ├── filters/
│   │   ├── __init__.py
│   │   ├── content_quality.py
│   │   ├── duplicate_filter.py
│   │   ├── interest_filter.py
│   │   ├── reddit_quality_filter.py
│   │   └── source_quality.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── qwen.py
│   ├── sources/
│   │   ├── __init__.py
│   │   ├── github_sources.py
│   │   ├── reddit_sources.py
│   │   └── rss_sources.py
│   ├── storage/
│   │   ├── __init__.py
│   │   └── sqlite_storage.py
│   └── utils/
│       ├── __init__.py
│       └── utils.py
├── docs/
│   └── source_schema.md
├── modules/
│   ├── __init__.py
│   ├── friction/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── runner.py
│   │   ├── engines/
│   │   │   └── __init__.py
│   │   └── reports/
│   │       └── __init__.py
│   └── trend/
│       ├── __init__.py
│       ├── config.py
│       ├── runner.py
│       ├── engines/
│       │   ├── __init__.py
│       │   ├── opportunity_engine.py
│       │   ├── recommendation_engine.py
│       │   ├── signal_engine.py
│       │   ├── topic_normalizer.py
│       │   └── trend_engine.py
│       └── reports/
├── reports/
│   ├── daily/
│   ├── monthly/
│   ├── weekly/
│   ├── weekly_brief.py
│   └── weekly_brief_output.md
├── stats/
│   ├── __init__.py
│   ├── collection_stats.json
│   └── stats_manager.py
├── website/
├── analyzer.py
├── articles.json
├── interests_goals.py
├── main.py
├── main_collector.py
├── README.md
├── reporter.py
├── requirements.txt
└── scheduler.py
```

## Folders Created

- `core/`
- `core/utils/`
- `modules/`
- `modules/trend/`
- `modules/trend/engines/`
- `modules/trend/reports/`
- `modules/friction/`
- `modules/friction/engines/`
- `modules/friction/reports/`
- `website/`
- `config/`

## Files Moved

- `collectors/*` -> `core/collectors/*`
- `filters/*` -> `core/filters/*`
- `models/*` -> `core/models/*`
- `sources/*` -> `core/sources/*`
- `storage/sqlite_storage.py` -> `core/storage/sqlite_storage.py`
- `utils.py` -> `core/utils/utils.py`
- `engines/trend_engine.py` -> `modules/trend/engines/trend_engine.py`
- `engines/topic_normalizer.py` -> `modules/trend/engines/topic_normalizer.py`
- `engines/opportunity_engine.py` -> `modules/trend/engines/opportunity_engine.py`
- `engines/recommendation_engine.py` -> `modules/trend/engines/recommendation_engine.py`

## Files Renamed

- `engines/signal_strength.py` -> `modules/trend/engines/signal_engine.py`

## Files Added

- `MIGRATION_REPORT.md`
- `core/__init__.py`
- `core/storage/__init__.py`
- `core/utils/__init__.py`
- `modules/__init__.py`
- `modules/trend/__init__.py`
- `modules/trend/config.py`
- `modules/trend/runner.py`
- `modules/trend/engines/__init__.py`
- `modules/friction/__init__.py`
- `modules/friction/config.py`
- `modules/friction/runner.py`
- `modules/friction/engines/__init__.py`
- `modules/friction/reports/__init__.py`

## Imports Updated

Examples:

- `from utils import load_articles` -> `from core.utils import load_articles`
- `from models.qwen import analyze` -> `from core.models.qwen import analyze`
- `from filters.duplicate_filter import build_url_index` -> `from core.filters.duplicate_filter import build_url_index`
- `from sources.github_sources import GITHUB_SOURCES` -> `from core.sources.github_sources import GITHUB_SOURCES`
- `from engines.topic_normalizer import normalize_topic` -> `from modules.trend.engines.topic_normalizer import normalize_topic`
- `from engines import signal_strength` -> `from modules.trend.engines import signal_engine`

## Entry Points Updated

- `main.py` now reads trend workflow settings from `modules/trend/config.py`.
- `main.py` accepts an omitted mode and defaults to `full`, so `python main.py` runs the current collect/analyze/report workflow.
- `main_collector.py` now runs collector modules from `core.collectors.*`.
- `modules/trend/runner.py` was added to execute the current Trend Intelligence pipeline.

## Verification

- Compile check passed:
  - `.venv\Scripts\python.exe -m compileall -q analyzer.py main.py main_collector.py reporter.py scheduler.py core modules reports stats`
- Smoke import passed:
  - imported `main`, `main_collector`, `analyzer`, `reporter`, and `modules.trend.runner`
- CLI parse check passed:
  - `.venv\Scripts\python.exe main.py --help`

The full pipeline was not executed because it would run live collectors and mutate data files.

## Migration Risks Detected

- `reports/weekly_brief.py` references APIs/modules that do not exist in the current repository:
  - `modules.trend.engines.trend_acceleration`
  - `get_top_topics` from `trend_engine`
  - `get_topic_opportunities` and `get_top_opportunities` from `opportunity_engine`
- `core/collectors/reddit_collector.py` imports `reddit_client`, but no `reddit_client.py` exists in the repository.
- The requested target tree lists `core/storage/json_storage.py`, but the existing project contains `sqlite_storage.py`. The migration preserved the existing storage file rather than renaming or inventing storage behavior.
- Generated data files are currently dirty in git and should be reviewed separately:
  - `reports/daily/2026-06-12_report.json`
  - `reports/daily/2026-06-12_report.md`
  - `stats/collection_stats.json`

## Files Requiring Manual Review

- `reports/weekly_brief.py`
- `core/collectors/reddit_collector.py`
- `core/storage/sqlite_storage.py`
- `reports/daily/2026-06-12_report.json`
- `reports/daily/2026-06-12_report.md`
- `stats/collection_stats.json`

Flow → One


