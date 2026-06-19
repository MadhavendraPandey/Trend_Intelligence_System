# Imports

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from core.filters.content_quality import is_high_quality
from core.filters.duplicate_filter import build_url_index, is_duplicate
from core.filters.interest_filter import calculate_relevance
from stats.stats_manager import increment_stat
from core.utils import create_item, load_articles, save_articles

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# Configuration

json_file = PROJECT_ROOT / "articles.json"
SOURCE_TYPE = "hackernews"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date"
TOP_STORY_LIMIT = 30
SEARCH_LIMIT = 30

HN_TARGETS = {
    "top_stories": {
        "category": "technology",
        "kind": "top_stories",
        "query": None,
    },
    "ai": {
        "category": "ai",
        "kind": "search",
        "query": "AI",
    },
    "security": {
        "category": "cybersecurity",
        "kind": "search",
        "query": "security",
    },
    "startups": {
        "category": "startups",
        "kind": "search",
        "query": "startup",
    },
}


def fetch_json(url):
    request = Request(
        url,
        headers={
            "User-Agent": "trend-intelligence-hackernews-collector",
        },
        method="GET",
    )

    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    except HTTPError as error:
        message = error.read().decode("utf-8", errors="replace")
        print(f"Hacker News API error {error.code}: {message}")
        return None

    except URLError as error:
        print(f"Hacker News connection error: {error}")
        return None


def fetch_top_story_items():
    story_ids = fetch_json(HN_TOP_STORIES_URL) or []
    items = []

    for item_id in story_ids[:TOP_STORY_LIMIT]:
        item = fetch_json(HN_ITEM_URL.format(item_id=item_id))
        if item:
            items.append(item)

    return items


def fetch_search_items(query):
    params = urlencode(
        {
            "query": query,
            "tags": "story",
            "hitsPerPage": SEARCH_LIMIT,
        }
    )
    payload = fetch_json(f"{HN_SEARCH_URL}?{params}") or {}

    return payload.get("hits", [])


def normalize_hn_item(
    raw_item,
    category,
    target_name,
):
    item_id = raw_item.get("id") or raw_item.get("objectID")

    title = raw_item.get("title") or raw_item.get("story_title") or ""

    author = raw_item.get("by") or raw_item.get("author") or "unknown"

    external_url = raw_item.get("url") or raw_item.get("story_url")
    source_domain = "news.ycombinator.com"

    if external_url:
        source_domain = urlparse(external_url).netloc.replace("www.", "").lower()

    hn_url = f"https://news.ycombinator.com/item?id={item_id}"

    url = external_url or hn_url

    score = raw_item.get("score") or raw_item.get("points") or 0

    comments = raw_item.get("descendants")

    if comments is None:
        comments = raw_item.get("num_comments", 0)

    created_at = raw_item.get("created_at")

    if not created_at and raw_item.get("time"):
        created_at = datetime.fromtimestamp(raw_item["time"], timezone.utc).isoformat()

    content = f"""
Title:
{title}

URL:
{url}

Score:
{score}

Comments:
{comments}

Author:
{author}
"""

    filter_text = f"""
{title}
{url}
{author}
{target_name}
"""

    relevance = calculate_relevance(filter_text)

    return create_item(
        source_type="hackernews",
        category=category,
        title=title,
        content=content,
        url=url,
        metadata={
            "source_domain": source_domain,
            "story_id": item_id,
            "author": author,
            "score": score,
            "comments": comments,
            "created_at": created_at,
            "collection_target": target_name,
            "hn_url": hn_url,
            "external_url": external_url,
        },
        filter_data={
            "relevance_score": relevance["score"],
            "matched_topics": relevance["matched_topics"],
        },
    )


def collect_hackernews_items():
    articles = load_articles(json_file)
    existing_urls = build_url_index(articles)
    total_seen = 0
    duplicates = 0
    quality_removed = 0
    filtered = 0
    stored = 0

    print(f"Loaded {len(existing_urls)} existing URLs")

    for target_name, target in HN_TARGETS.items():
        print(f"\n[{target_name.upper()}]")

        if target["kind"] == "top_stories":
            raw_items = fetch_top_story_items()
        else:
            raw_items = fetch_search_items(target["query"])

        print(f"Stories: {len(raw_items)}")

        for raw_item in raw_items:
            total_seen += 1
            increment_stat(SOURCE_TYPE, "seen")
            item = normalize_hn_item(raw_item, target["category"], target_name)
            url = item.get("url")

            if not url:
                quality_removed += 1
                increment_stat(SOURCE_TYPE, "quality_removed")
                continue

            if is_duplicate(url, existing_urls):
                duplicates += 1
                increment_stat(SOURCE_TYPE, "duplicates_removed")
                print("Duplicate skipped")
                continue

            if not is_high_quality(item.get("content", "")):
                quality_removed += 1
                increment_stat(SOURCE_TYPE, "quality_removed")
                continue

            if item["filter_data"]["relevance_score"] == 0:
                filtered += 1
                increment_stat(SOURCE_TYPE, "irrelevant_removed")
                continue

            articles.append(item)
            existing_urls.add(url)
            stored += 1
            increment_stat(SOURCE_TYPE, "stored")
            print(f"Saved: {item['title']}")

    save_articles(articles, json_file)

    print(f"\nFinished. Added {stored} Hacker News items.")
    print(f"Seen: {total_seen}")
    print(f"Duplicates: {duplicates}")
    print(f"Quality Removed: {quality_removed}")
    print(f"Filtered: {filtered}")
    print(f"Stored: {stored}")


if __name__ == "__main__":
    collect_hackernews_items()
