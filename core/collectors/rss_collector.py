import sys
from urllib.parse import urlparse
from pathlib import Path
import feedparser
import trafilatura

from core.filters.duplicate_filter import (
    build_url_index,
    is_duplicate,
)
from core.filters.interest_filter import (
    calculate_relevance,
)
from core.filters.content_quality import (
    is_high_quality,
)
from core.sources.rss_sources import FEEDS
from stats.stats_manager import (
    increment_stat,
)
from core.utils import (
    load_articles,
    save_articles,
    create_item,
)

# Configurati
PROJECT_ROOT = Path(__file__).resolve().parents[2]
json_file = PROJECT_ROOT / "articles.json"

SOURCE_TYPE = "rss"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

articles = load_articles(json_file)

existing_links = build_url_index(articles)

print(f"Loaded {len(existing_links)} existing articles")


# Extraction


def extract_article(url):

    downloaded = trafilatura.fetch_url(url)

    if not downloaded:
        return None

    return trafilatura.extract(downloaded)


# Collection

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

            # Duplicate Check

            if is_duplicate(link, existing_links):
                increment_stat(SOURCE_TYPE, "duplicates_removed")

                print("Duplicate skipped")

                continue

            # Relevance Check

            filter_text = f"""
            {title}
            {summary}
            {tags}
            """

            relevance = calculate_relevance(filter_text)

            if relevance["score"] == 0:
                filtered += 1

                increment_stat(SOURCE_TYPE, "irrelevant_removed")

                print(f"Filtered: no interest match -> {title} ")

                continue

            # Content Extraction

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

            # Content Quality

            if not is_high_quality(content):
                increment_stat(SOURCE_TYPE, "quality_removed")

                print("Filtered: low quality content")

                continue

            # Metadata

            source_domain = urlparse(link).netloc.replace("www.", "").lower()

            # Storage

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

            articles.append(article_data)

            existing_links.add(link)

            total_new_articles += 1

            increment_stat(SOURCE_TYPE, "stored")

            print(f"Saved: {title}")


# Save

save_articles(articles, json_file)

print(f"\nFinished. Added {total_new_articles} new articles.")

print(f"Total articles: {len(articles)}")

print(f"Seen: {total_seen}")

print(f"Filtered: {filtered}")

print(f"Stored: {total_new_articles}")
