"""Collection statistics facade backed by SQLite.

Purpose:
    Preserve the existing `increment_stat` and `get_stats` API while removing
    runtime dependency on `stats/collection_stats.json`.

Architecture notes:
    Collectors call this module as before. Persistence is delegated to
    `SourceRunRepository`, keeping SQL inside repositories.

Future extension guidance:
    Replace this facade with explicit source run lifecycle calls once
    collectors are refactored around repository-backed source runs.
"""

from pathlib import Path

from core.storage import SQLiteStorage
from database.repositories import SourceRunRepository

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_FILE = PROJECT_ROOT / "database" / "intelligence_platform.sqlite"

METRICS = [
    "seen",
    "duplicates_removed",
    "quality_removed",
    "irrelevant_removed",
    "stored",
]

DEFAULT_SOURCES = [
    "rss",
    "github",
    "reddit",
    "hackernews",
    "arxiv",
]


def _repository():
    storage = SQLiteStorage(db_file=DEFAULT_DB_FILE)
    return storage, SourceRunRepository(storage)


def build_empty_source_stats():
    return {
        metric: 0
        for metric in METRICS
    }


def increment_stat(source, metric):
    if metric not in METRICS:
        raise ValueError(f"Unknown collection stat metric: {metric}")

    storage, repository = _repository()

    try:
        repository.increment_stat(source, metric)
    finally:
        storage.close()


def get_stats():
    storage, repository = _repository()

    try:
        return repository.get_stats(DEFAULT_SOURCES)
    finally:
        storage.close()
