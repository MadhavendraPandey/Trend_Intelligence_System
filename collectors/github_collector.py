# Imports

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from filters.interest_filter import calculate_relevance
from filters.content_quality import is_high_quality
from sources.github_sources import GITHUB_SOURCES
from stats.stats_manager import increment_stat
from storage.sqlite_storage import connect, upsert_article, initialize_database
from utils import create_item

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# Configuration

SOURCE_TYPE = "github"

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
RESULTS_PER_TARGET = 30
DATE_WINDOW_DAYS = 30


# GitHub API


def build_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "trend-intelligence-github-collector",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    token = os.getenv("GITHUB_TOKEN")  # Github API Tocken
    if token:
        headers["Authorization"] = f"Bearer {token}"
    #
    return headers


def resolve_query(query):
    date_window = (
        (datetime.now(timezone.utc) - timedelta(days=DATE_WINDOW_DAYS))
        .date()
        .isoformat()
    )

    return query.replace("{date_window}", date_window)


def expand_query(query):
    resolved_query = resolve_query(query)
    tokens = resolved_query.split()

    if "OR" not in tokens:
        return [resolved_query]

    or_positions = [index for index, token in enumerate(tokens) if token == "OR"]
    operand_positions = set()

    for position in or_positions:
        if position > 0:
            operand_positions.add(position - 1)
        if position + 1 < len(tokens):
            operand_positions.add(position + 1)

    common_terms = [
        token
        for index, token in enumerate(tokens)
        if token != "OR" and index not in operand_positions
    ]

    queries = []
    for index in sorted(operand_positions):
        query_terms = [tokens[index], *common_terms]
        queries.append(" ".join(query_terms))

    return queries


def fetch_github_repositories(query, sort, order):
    params = urlencode(
        {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": RESULTS_PER_TARGET,
        }
    )
    request = Request(
        f"{GITHUB_SEARCH_URL}?{params}",
        headers=build_headers(),
        method="GET",
    )

    try:
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return payload.get("items", [])

    except HTTPError as error:
        message = error.read().decode("utf-8", errors="replace")
        print(f"GitHub API error {error.code}: {message}")
        return []

    except URLError as error:
        print(f"GitHub connection error: {error}")
        return []


def query_github_repositories(query, sort, order):
    repositories = []
    seen_urls = set()

    for expanded_query in expand_query(query):
        for repository in fetch_github_repositories(
            expanded_query,
            sort,
            order,
        ):
            url = repository.get("html_url")

            if url in seen_urls:
                continue

            repositories.append(repository)
            seen_urls.add(url)

    return repositories


# Schema Conversion


def repository_to_item(repository, category, target_name, relevance):
    url = repository.get("html_url", "")
    description = repository.get("description") or ""

    topics = ", ".join(repository.get("topics", []))

    content = f"""
Repository:
{repository.get("full_name", "")}

Description:
{description}

Topics: 
{topics}

Language:
{repository.get("language", "Unknown")}

Stars:
{repository.get("stargazers_count", 0)}
"""

    return create_item(
        source_type="github",
        category=category,
        title=repository.get("full_name", ""),
        content=content,
        url=url,
        metadata={
            "source_domain": "github.com",
            "stars": repository.get("stargazers_count", 0),
            "forks": repository.get("forks_count", 0),
            "watchers": repository.get("watchers_count", 0),
            "open_issues": repository.get("open_issues_count", 0),
            "language": repository.get("language"),
            "topics": repository.get("topics", []),
            "created_at": repository.get("created_at"),
            "updated_at": repository.get("updated_at"),
            "collection_target": target_name,
        },
        filter_data={
            "relevance_score": relevance["score"],
            "matched_topics": relevance["matched_topics"],
        },
    )


# Collection


def get_existing_links(connection):
    cursor = connection.execute("SELECT url FROM articles")
    return {row["url"] for row in cursor.fetchall()}


def is_duplicate(url, existing_links):
    return url in existing_links


def collect_github_items():
    initialize_database()
    connection = connect()
    existing_urls = get_existing_links(connection)

    total_new_items = 0
    total_seen = 0
    duplicates = 0
    filtered = 0

    print(f"Loaded {len(existing_urls)} existing URLs")

    for category, source in GITHUB_SOURCES.items():
        print(f"\n[{category.upper()}]")

        for target in source.get("targets", []):
            target_name = target.get("name", "unknown_target")
            print(f"Querying: {target_name}")

            repositories = query_github_repositories(
                target.get("query", ""),
                target.get("sort", "stars"),
                target.get("order", "desc"),
            )
            print(f"Repositories: {len(repositories)}")

            for repository in repositories:
                total_seen += 1
                increment_stat(SOURCE_TYPE, "seen")
                url = repository.get("html_url", "")

                if not url:
                    increment_stat(SOURCE_TYPE, "quality_removed")
                    continue

                if is_duplicate(url, existing_urls):
                    duplicates += 1
                    increment_stat(SOURCE_TYPE, "duplicates_removed")
                    print("Duplicate skipped")
                    continue

                filter_text = f"""
                {repository.get("name", "")}
                {repository.get("description", "")}
                {" ".join(repository.get("topics", []))}
                """

                if not is_high_quality(filter_text):
                    increment_stat(SOURCE_TYPE, "quality_removed")
                    continue

                relevance = calculate_relevance(filter_text)

                if relevance["score"] == 0:
                    filtered += 1
                    increment_stat(SOURCE_TYPE, "irrelevant_removed")
                    continue

                item = repository_to_item(
                    repository,
                    category,
                    target_name,
                    relevance,
                )

                upsert_article(item, connection)
                connection.commit()

                existing_urls.add(url)
                total_new_items += 1
                increment_stat(SOURCE_TYPE, "stored")
                print(f"Saved: {item['title']}")

    print(f"\nFinished. Added {total_new_items} new GitHub items.")
    print(f"Seen: {total_seen}")
    print(f"Duplicates: {duplicates}")
    print(f"Filtered: {filtered}")
    print(f"Stored: {total_new_items}")
    return 0


if __name__ == "__main__":
    collect_github_items()
