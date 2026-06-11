# Imports

from urllib.parse import urlparse
from pathlib import Path
import feedparser
import trafilatura

from filters.duplicate_filter import (
    build_url_index,
    is_duplicate,
)
from filters.interest_filter import (
    calculate_relevance,
)
from filters.content_quality import (
    is_high_quality,
)
from sources.rss_sources import FEEDS
from stats.stats_manager import (
    increment_stat,
)
from storage.sqlite_storage import (
    connect,
    upsert_article,
    initialize_database,
)
from utils import (
    create_item,
)

# ==========================================================
# Configuration
# ==========================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_TYPE = "rss"

def get_existing_links(connection):
    cursor = connection.execute("SELECT url FROM articles")
    return {row["url"] for row in cursor.fetchall()}


def is_duplicate(url, existing_links):
    return url in existing_links


# ==========================================================
# Extraction
# ==========================================================


def collect_rss_items():
    initialize_database()
    connection = connect()
    existing_links = get_existing_links(connection)

    print(f"Loaded {len(existing_links)} existing articles")

    total_seen = 0
    total_new_articles = 0
    filtered = 0

    for category, feed_urls in FEEDS.items():
        for feed_url in feed_urls:
            print(f"\n[{category.upper()}] Reading: {feed_url}")

            parsed_feed = feedparser.parse(feed_url)

            print(f"Entries: {len(parsed_feed.entries)}")

            if parsed_feed.bozo:
                print(f"Feed Error: {parsed_feed.bozo_exception}")

            if not parsed_feed.entries:
                print("No articles found")

                continue

            for article in parsed_feed.entries:
                total_seen += 1

                increment_stat(SOURCE_TYPE, "seen")

                title = article.get("title", "")

                link = article.get("link", "")

                date = article.get("published", "Unknown")

                author = article.get("author", "Unknown")

                summary = article.get("summary", "")

                tags = " ".join(tag.get("term", "") for tag in article.get("tags", []))

                # ==================================================
                # Duplicate Check
                # ==================================================

                if is_duplicate(link, existing_links):
                    increment_stat(SOURCE_TYPE, "duplicates_removed")

                    print("Duplicate skipped")

                    continue

                # ==================================================
                # Relevance Check
                # ==================================================

                filter_text = f"""
                {title}
                {summary}
                {tags}
                """

                relevance = calculate_relevance(filter_text)

                if relevance["score"] == 0:
                    filtered += 1

                    increment_stat(SOURCE_TYPE, "irrelevant_removed")

                    print("Filtered: no interest match")

                    continue

                # ==================================================
                # Content Extraction
                # ==================================================

                try:
                    content = extract_article(link)

                except Exception as e:
                    increment_stat(SOURCE_TYPE, "quality_removed")

                    print(f"Extraction failed: {e}")

                    continue

                if not content:
                    increment_stat(SOURCE_TYPE, "quality_removed")

                    print(f"No content extracted:\n{link}")

                    continue

                # ==================================================
                # Content Quality
                # ==================================================

                if not is_high_quality(content):
                    increment_stat(SOURCE_TYPE, "quality_removed")

                    print("Filtered: low quality content")

                    continue

                # ==================================================
                # Metadata
                # ==================================================

                source_domain = urlparse(link).netloc.replace("www.", "").lower()

                # ==================================================
                # Storage
                # ==================================================

                article_data = create_item(
                    source_type="rss",
                    category=category,
                    title=title,
                    content=content[:5000],
                    url=link,
                    metadata={
                        "author": author,
                        "published": date,
                        "feed_url": feed_url,
                        "source_domain": source_domain,
                        "content_length": len(content),
                        "summary_length": len(summary),
                        "tags": tags.split(),
                    },
                    filter_data={
                        "relevance_score": relevance["score"],
                        "matched_topics": relevance["matched_topics"],
                    },
                )

                upsert_article(article_data, connection)
                connection.commit()

                existing_links.add(link)

                total_new_articles += 1

                increment_stat(SOURCE_TYPE, "stored")

                print(f"Saved: {title}")

    # ==========================================================
    # Summary
    # ==========================================================

    print(f"\nFinished. Added {total_new_articles} new articles.")

    print(f"Seen: {total_seen}")

    print(f"Filtered: {filtered}")

    print(f"Stored: {total_new_articles}")
    return 0


def extract_article(url):

    downloaded = trafilatura.fetch_url(url)

    if not downloaded:
        return None

    return trafilatura.extract(downloaded)


if __name__ == "__main__":
    collect_rss_items()
