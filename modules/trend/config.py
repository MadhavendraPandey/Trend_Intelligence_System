from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

COLLECTOR_MODULES = [
    "core.collectors.rss_collector",
    "core.collectors.github_collector",
    # "core.collectors.reddit_collector",
    "core.collectors.hackernews_collector",
    "core.collectors.arxiv_collector",
]

COMMANDS = {
    "collect": "main_collector.py",
    "analyze": "analyzer.py",
    "report": "reporter.py",
}

FULL_SEQUENCE = [
    "collect",
    "analyze",
    "report",
]
