"""Shared utilities for the Intelligence Platform.

Purpose:
    Keep backward-compatible helper functions used by the existing Trend
    pipeline while routing active runtime storage through SQLite.

Architecture notes:
    `load_articles` and `save_articles` no longer read or write `articles.json`.
    They use repositories backed by SQLite. JSON support remains available only
    through explicit export helpers for backup/recovery workflows.

Future extension guidance:
    Replace these compatibility helpers with direct repository usage once
    collectors, analyzer, and reports are fully refactored.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from core.storage import JsonStorage, SQLiteStorage
from database.repositories import (
    AnalysisFailureRepository,
    PostRepository,
    SourceRepository,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_FILE = PROJECT_ROOT / "database" / "intelligence_platform.sqlite"


def _storage():
    return SQLiteStorage(db_file=DEFAULT_DB_FILE)


def _source_for_article(source_repository, article):
    source_type = article.get("source_type") or article.get("source") or "unknown"

    for source in source_repository.list_sources(limit=1000):
        if source["source_type"] == source_type and source["name"] == source_type:
            return source

    return source_repository.create_source(
        source_type=source_type,
        name=source_type,
        owner_module="trend",
    )


def _is_failure_path(path):
    return Path(path or "").name == "failed_articles.json"


def load_articles(json_file=None):
    """Load active article-shaped records from SQLite.

    The `json_file` argument is retained for backward compatibility. Passing
    `failed_articles.json` loads analyzer failure records from SQLite.
    """
    storage = _storage()

    try:
        if _is_failure_path(json_file):
            return AnalysisFailureRepository(storage).list_failures()

        return PostRepository(storage).articles()
    finally:
        storage.close()


def save_articles(articles, json_file=None):
    """Persist article-shaped records to SQLite.

    The `json_file` argument is retained for backward compatibility. Passing
    `failed_articles.json` stores analyzer failure records in SQLite.
    """
    last_error = None

    for attempt in range(5):
        storage = _storage()

        try:
            if _is_failure_path(json_file):
                AnalysisFailureRepository(storage).replace_failures(articles)
                return

            source_repository = SourceRepository(storage)
            post_repository = PostRepository(storage)

            for article in articles:
                if not isinstance(article, dict):
                    continue

                source = _source_for_article(source_repository, article)
                post_repository.upsert_article(article, source_id=source["id"])

            return

        except OSError as error:
            last_error = error
            time.sleep(0.5 * (attempt + 1))

        finally:
            storage.close()

    if last_error:
        raise last_error


def export_articles_to_json(json_file):
    """Export current SQLite posts to JSON for backup or recovery."""
    articles = load_articles()
    return JsonStorage().save(articles, json_file)


def clean_json_response(response):
    response = response.strip()

    if "```json" in response:
        response = response.replace("```json", "")

    if "```" in response:
        response = response.replace("```", "")

    start = response.find("{")
    end = response.rfind("}")

    if start != -1 and end != -1:
        response = response[start : end + 1]

    return response.strip()


def create_item(
    source_type,
    category,
    title,
    content,
    url,
    metadata=None,
    filter_data=None,
):
    return {
        "source_type": source_type,
        "category": category,
        "title": title,
        "content": content,
        "url": url,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "source_quality_score": None,
        "trend_score": None,
        "opportunity_score": None,
        "analysis": None,
        "filter_data": (filter_data or {}),
        "metadata": (metadata or {}),
    }
