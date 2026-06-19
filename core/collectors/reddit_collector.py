import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is on sys.path before importing local modules
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.filters.duplicate_filter import build_url_index, is_duplicate
from core.filters.interest_filter import calculate_relevance
from core.filters.reddit_quality_filter import (
    calculate_engagement_score,
    is_high_quality_reddit_post,
)
from reddit_client import (
    fetch_subreddit_posts,
    fetch_top_comments,
    get_reddit_client,
)
from core.sources.reddit_sources import REDDIT_SOURCES
from stats.stats_manager import increment_stat
from core.utils import create_item, load_articles, save_articles

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# Configuration
json_file = PROJECT_ROOT / "articles.json"
SOURCE_TYPE = "reddit"
POSTS_PER_SUBREDDIT = 25
LISTING_TYPES = [
    "hot",
    "rising",
    "new",
]


def get_post_url(data):
    permalink = data.get("permalink", "")

    if permalink:
        return f"https://www.reddit.com{permalink}"

    return data.get("url", "")


def get_post_duplicate_key(post):
    data = post.get("data", {})

    return (
        get_post_url(data)
        or data.get("reddit_url")
        or data.get("url")
        or data.get("permalink")
        or data.get("id")
    )


def merge_posts(posts):
    merged_posts = []
    merged_by_key = {}
    seen_post_keys = set()
    duplicates = 0

    for post in posts:
        post_key = get_post_duplicate_key(post)

        if not post_key:
            continue

        if post_key in seen_post_keys:
            existing_post = merged_by_key[post_key]
            existing_data = existing_post.setdefault("data", {})
            duplicate_data = post.get("data", {})
            existing_listings = existing_data.setdefault("collection_listings", [])

            for listing_type in duplicate_data.get("collection_listings", []):
                if listing_type not in existing_listings:
                    existing_listings.append(listing_type)

            duplicates += 1
            continue

        seen_post_keys.add(post_key)
        merged_by_key[post_key] = post
        merged_posts.append(post)

    return merged_posts, duplicates


def build_filter_text(data, top_comments):
    comment_text = "\n".join(comment.get("body", "") for comment in top_comments)

    return f"""
Title:
{data.get("title", "")}

Body:
{data.get("selftext") or ""}

Subreddit:
{data.get("subreddit", "")}

Flair:
{data.get("link_flair_text") or ""}

Listing Types:
{", ".join(data.get("collection_listings", []))}

URL:
{get_post_url(data)}

Source URL:
{data.get("url", "")}

Score:
{data.get("score", 0)}

Comments:
{data.get("num_comments", 0)}

Top Comments:
{comment_text}
"""


def reddit_post_to_item(post, category, relevance, top_comments=None):
    data = post.get("data", {})
    title = data.get("title", "")
    body = data.get("selftext") or ""
    subreddit = data.get("subreddit", "")
    url = get_post_url(data)
    score = data.get("score", 0)
    num_comments = data.get("num_comments", 0)
    engagement_score = calculate_engagement_score(score, num_comments)
    top_comments = top_comments or []
    collection_listings = data.get("collection_listings", [])
    created_utc = data.get("created_utc")
    created_at = data.get("created_at")

    if not created_at and created_utc:
        created_at = datetime.fromtimestamp(created_utc, timezone.utc).isoformat()

    content = f"""
Title:
{title}

Body:
{body}

Subreddit:
{subreddit}

Score:
{score}

Comments:
{num_comments}

Engagement Score:
{engagement_score}
"""

    return create_item(
        source_type="reddit",
        category=category,
        title=title,
        content=content,
        url=url,
        metadata={...},
        filter_data={...},
    )


def collect_reddit_items():
    reddit = get_reddit_client()
    articles = load_articles(json_file)
    existing_urls = build_url_index(articles)
    total_seen = 0
    duplicates = 0
    quality_removed = 0
    filtered = 0
    stored = 0

    print(f"Loaded {len(existing_urls)} existing URLs")

    for category, source in REDDIT_SOURCES.items():
        print(f"\n[{category.upper()}]")

        for subreddit in source.get("subreddits", []):
            print(f"Reading r/{subreddit}")
            raw_posts = []

            for listing_type in LISTING_TYPES:
                listing_posts = fetch_subreddit_posts(
                    reddit, subreddit, listing_type, POSTS_PER_SUBREDDIT
                )

                for post in listing_posts:
                    data = post.setdefault("data", {})
                    data["collection_listings"] = [listing_type]

                raw_posts.extend(listing_posts)
                total_seen += len(listing_posts)

                for _ in listing_posts:
                    increment_stat(SOURCE_TYPE, "seen")

                print(f"{listing_type.title()} posts: {len(listing_posts)}")

            posts, merged_duplicates = merge_posts(raw_posts)
            duplicates += merged_duplicates

            for _ in range(merged_duplicates):
                increment_stat(SOURCE_TYPE, "duplicates_removed")

            print(f"Merged posts: {len(posts)}")

            for post in posts:
                data = post.get("data", {})
                title = data.get("title", "")
                url = get_post_url(data)

                if not url:
                    quality_removed += 1
                    increment_stat(SOURCE_TYPE, "quality_removed")
                    continue

                if is_duplicate(url, existing_urls):
                    duplicates += 1
                    increment_stat(SOURCE_TYPE, "duplicates_removed")
                    print("Duplicate skipped")
                    continue

                if not is_high_quality_reddit_post(data):
                    quality_removed += 1
                    increment_stat(SOURCE_TYPE, "quality_removed")
                    continue

                top_comments = []
                if data.get("score", 0) >= 50:
                    top_comments = fetch_top_comments(data.get("submission"), limit=3)

                filter_text = build_filter_text(data, top_comments)

                relevance = calculate_relevance(filter_text)

                if relevance["score"] == 0:
                    filtered += 1
                    increment_stat(SOURCE_TYPE, "irrelevant_removed")
                    continue

                item = reddit_post_to_item(post, category, relevance, top_comments)

                articles.append(item)
                existing_urls.add(url)
                stored += 1
                increment_stat(SOURCE_TYPE, "stored")
                print(f"Saved: {title}")

    save_articles(articles, json_file)

    print(f"\nFinished. Added {stored} Reddit items.")
    print(f"Seen: {total_seen}")
    print(f"Duplicates: {duplicates}")
    print(f"Quality Removed: {quality_removed}")
    print(f"Filtered: {filtered}")
    print(f"Stored: {stored}")


if __name__ == "__main__":
    collect_reddit_items()
