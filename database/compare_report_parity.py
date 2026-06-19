"""SQLite report input validation after cutover.

Purpose:
    Preserve the Phase 4 script name as a compatibility entry point while
    validating the Phase 5 SQLite-only read path.

Architecture notes:
    This script no longer reads `articles.json`. It compares the repository
    article count with the reporter's SQLite-backed report input count.

Future extension guidance:
    Remove this script once cutover validation is absorbed into a test suite.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import reporter
from core.storage import SQLiteStorage
from database.repositories import PostRepository


def main():
    storage = SQLiteStorage()

    try:
        repository = PostRepository(storage)
        repository_count = repository.count_posts()
    finally:
        storage.close()

    report_data = reporter.build_report_data()
    report_count = report_data["overview"]["total_articles"]
    counts_match = repository_count == report_count

    print(f"Repository posts: {repository_count}")
    print(f"Reporter articles: {report_count}")
    print(f"Counts match: {counts_match}")

    return 0 if counts_match else 1


if __name__ == "__main__":
    raise SystemExit(main())
