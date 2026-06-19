"""Migrate existing articles.json records into SQLite posts.

Purpose:
    Import the current JSON article store into the Phase 1/2 SQLite foundation
    without creating trends, complaints, evidence, or friction objects.

Architecture notes:
    This utility uses SourceRepository and PostRepository for database writes.
    It does not execute raw SQL for migration data access. SQLiteStorage owns
    schema initialization and migration application.

Future extension guidance:
    Keep this utility focused on JSON-to-post import. Later phases should add
    dedicated migration utilities for evidence, reports, or module-specific
    objects after their schemas are approved.
"""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.storage import SQLiteStorage
from database.repositories import PostRepository, SourceRepository

DEFAULT_JSON_FILE = PROJECT_ROOT / "articles.json"
DEFAULT_DB_FILE = PROJECT_ROOT / "database" / "intelligence_platform.sqlite"
DEFAULT_REPORT_FILE = PROJECT_ROOT / "JSON_MIGRATION_REPORT.md"


def load_articles(json_file):
    path = Path(json_file)

    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, list):
        raise ValueError("articles.json must contain a JSON array")

    return payload


def get_article_url(article):
    return article.get("url") or article.get("link")


def get_source_type(article):
    return article.get("source_type") or article.get("source") or "unknown"


def get_author(article):
    metadata = article.get("metadata") or {}
    return metadata.get("author")


def get_published_at(article):
    metadata = article.get("metadata") or {}
    return (
        article.get("published_at")
        or article.get("published")
        or article.get("date")
        or metadata.get("published_at")
        or metadata.get("published")
        or metadata.get("created_at")
        or metadata.get("updated_at")
    )


def get_captured_at(article):
    return article.get("collected_at") or article.get("captured_at")


def get_source_record_id(article):
    metadata = article.get("metadata") or {}
    return (
        article.get("id")
        or article.get("source_record_id")
        or metadata.get("story_id")
        or metadata.get("id")
        or metadata.get("full_name")
    )


def get_source(source_repository, source_type, source_cache):
    if source_type in source_cache:
        return source_cache[source_type]

    for source in source_repository.list_sources(limit=1000):
        if source["source_type"] == source_type and source["name"] == source_type:
            source_cache[source_type] = source
            return source

    source = source_repository.create_source(
        source_type=source_type,
        name=source_type,
        owner_module="trend",
    )
    source_cache[source_type] = source
    return source


def migrate_articles(json_file=DEFAULT_JSON_FILE, db_file=DEFAULT_DB_FILE):
    articles = load_articles(json_file)
    storage = SQLiteStorage(db_file=db_file)
    source_repository = SourceRepository(storage)
    post_repository = PostRepository(storage)

    source_cache = {}
    seen_urls = set()
    imported_records = 0
    duplicate_urls = 0
    skipped_records = 0
    failures = []

    for index, article in enumerate(articles):
        if not isinstance(article, dict):
            skipped_records += 1
            failures.append(
                {
                    "index": index,
                    "reason": "record is not a JSON object",
                }
            )
            continue

        url = get_article_url(article)

        if not url:
            skipped_records += 1
            failures.append(
                {
                    "index": index,
                    "reason": "missing url",
                    "title": article.get("title"),
                }
            )
            continue

        if url in seen_urls or post_repository.get_by_url(url):
            duplicate_urls += 1
            continue

        seen_urls.add(url)
        source_type = get_source_type(article)
        source = get_source(source_repository, source_type, source_cache)

        try:
            post_repository.create_post(
                source_id=source["id"],
                source_type=source_type,
                source_record_id=get_source_record_id(article),
                category=article.get("category"),
                title=article.get("title") or "Untitled",
                url=url,
                canonical_url=url,
                content=article.get("content"),
                author=get_author(article),
                published_at=get_published_at(article),
                captured_at=get_captured_at(article),
                raw_json=article,
                metadata_json=article.get("metadata") or {},
                analysis_json=article.get("analysis"),
                filter_data_json=article.get("filter_data") or {},
            )
            imported_records += 1

        except Exception as error:
            skipped_records += 1
            failures.append(
                {
                    "index": index,
                    "url": url,
                    "title": article.get("title"),
                    "reason": str(error),
                }
            )

    validation = validate_migration(
        articles=articles,
        db_file=db_file,
        imported_records=imported_records,
        duplicate_urls=duplicate_urls,
        skipped_records=skipped_records,
    )
    storage.close()

    return {
        "json_file": str(Path(json_file)),
        "db_file": str(Path(db_file)),
        "total_records": len(articles),
        "imported_records": imported_records,
        "duplicate_urls": duplicate_urls,
        "skipped_records": skipped_records,
        "failures": failures,
        "validation": validation,
    }


def validate_migration(
    articles,
    db_file,
    imported_records,
    duplicate_urls,
    skipped_records,
):
    storage = SQLiteStorage(db_file=db_file)
    connection = storage.initialize()
    sqlite_count = connection.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    unique_url_count = connection.execute(
        """
        SELECT COUNT(DISTINCT canonical_url)
        FROM posts
        WHERE canonical_url IS NOT NULL AND canonical_url != ''
        """
    ).fetchone()[0]
    raw_json_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM posts
        WHERE raw_json IS NOT NULL AND raw_json != ''
        """
    ).fetchone()[0]
    category_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM posts
        WHERE category IS NOT NULL AND category != ''
        """
    ).fetchone()[0]
    filter_data_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM posts
        WHERE filter_data_json IS NOT NULL AND filter_data_json != ''
        """
    ).fetchone()[0]

    expected_importable = len(
        {
            get_article_url(article)
            for article in articles
            if isinstance(article, dict) and get_article_url(article)
        }
    )
    expected_total_accounted = imported_records + duplicate_urls + skipped_records

    storage.close()

    return {
        "sqlite_post_count": sqlite_count,
        "unique_url_count": unique_url_count,
        "raw_json_count": raw_json_count,
        "category_count": category_count,
        "filter_data_count": filter_data_count,
        "expected_importable_unique_urls": expected_importable,
        "total_accounted_records": expected_total_accounted,
        "json_count_matches_accounted_records": expected_total_accounted == len(articles),
        "sqlite_count_matches_imported_records": sqlite_count == imported_records,
        "url_uniqueness_verified": sqlite_count == unique_url_count,
        "raw_json_preserved_for_all_imports": raw_json_count == imported_records,
    }


def write_report(result, report_file=DEFAULT_REPORT_FILE):
    validation = result["validation"]
    failures = result["failures"]

    failure_lines = []
    if failures:
        for failure in failures[:25]:
            failure_lines.append(
                f"- index={failure.get('index')} url={failure.get('url')} reason={failure.get('reason')}"
            )
        if len(failures) > 25:
            failure_lines.append(f"- ... {len(failures) - 25} additional failures omitted")
    else:
        failure_lines.append("- None")

    report = f"""# JSON Migration Report

## Summary

- JSON file: `{result["json_file"]}`
- SQLite database: `{result["db_file"]}`
- Total records: {result["total_records"]}
- Imported records: {result["imported_records"]}
- Duplicate URLs: {result["duplicate_urls"]}
- Skipped records: {result["skipped_records"]}
- Failures: {len(failures)}

## Validation Results

- SQLite post count: {validation["sqlite_post_count"]}
- Unique URL count: {validation["unique_url_count"]}
- Raw JSON rows: {validation["raw_json_count"]}
- Rows with category: {validation["category_count"]}
- Rows with filter data: {validation["filter_data_count"]}
- Expected importable unique URLs: {validation["expected_importable_unique_urls"]}
- Total accounted records equals JSON count: {validation["json_count_matches_accounted_records"]}
- SQLite count equals imported records: {validation["sqlite_count_matches_imported_records"]}
- URL uniqueness verified: {validation["url_uniqueness_verified"]}
- Raw JSON preserved for all imports: {validation["raw_json_preserved_for_all_imports"]}

## Preservation Notes

The migration stores existing article fields in `posts`:

- `source_type`
- `category`
- `title`
- `content`
- `url`
- `metadata_json`
- `analysis_json`
- `filter_data_json`
- `raw_json`

The full original JSON object is preserved in `raw_json`.

## Out Of Scope

This migration did not create:

- trends
- complaints
- evidence
- frictions
- friction candidates

## Failures

{chr(10).join(failure_lines)}
"""

    Path(report_file).write_text(report, encoding="utf-8")
    return report_file


def parse_args():
    parser = argparse.ArgumentParser(
        description="Migrate articles.json into SQLite posts"
    )
    parser.add_argument(
        "--json-file",
        default=str(DEFAULT_JSON_FILE),
        help="Path to articles.json",
    )
    parser.add_argument(
        "--db-file",
        default=str(DEFAULT_DB_FILE),
        help="Path to SQLite database",
    )
    parser.add_argument(
        "--report-file",
        default=str(DEFAULT_REPORT_FILE),
        help="Path to write JSON_MIGRATION_REPORT.md",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    result = migrate_articles(
        json_file=args.json_file,
        db_file=args.db_file,
    )
    report_file = write_report(result, args.report_file)

    print(f"Total records: {result['total_records']}")
    print(f"Imported records: {result['imported_records']}")
    print(f"Duplicate URLs: {result['duplicate_urls']}")
    print(f"Skipped records: {result['skipped_records']}")
    print(f"Failures: {len(result['failures'])}")
    print(f"Report: {report_file}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
