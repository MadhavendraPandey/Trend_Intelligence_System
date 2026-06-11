# Imports

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

import feedparser
import trafilatura
from urllib.parse import urlparse
PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from filters.duplicate_filter import build_url_index, is_duplicate
from filters.interest_filter import calculate_relevance
from filters.content_quality import is_high_quality
from sources.rss_sources import FEEDS
from stats.stats_manager import increment_stat
from utils import load_articles, save_articles, create_item

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# Content Extraction

def extract_article(url):
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return None
    return trafilatura.extract(downloaded)


# JSON Storage

json_file = PROJECT_ROOT / "articles.json"
SOURCE_TYPE = "rss"
articles = load_articles(json_file)


# Build Deduplication Set

existing_links = build_url_index(articles)

print(f"Loaded {len(existing_links)} "f"existing articles")


# Process Feeds

total_new_articles = 0
total_seen = 0
filtered = 0
for category, feed_urls in FEEDS.items():

    for feed_url in feed_urls:
        print(f"\n[{category.upper()}] "f"Reading: {feed_url}")
        parsed_feed = feedparser.parse(feed_url)
        print(f"Entries: "f"{len(parsed_feed.entries)}")
        if parsed_feed.bozo:
            print(f"Feed Error: "f"{parsed_feed.bozo_exception}")
        if not parsed_feed.entries:
            print("No articles found")
            continue

        # Limit to 1 article while testing
        for article in parsed_feed.entries: # just for testing, remove [:1] to process all articles at once
            total_seen += 1
            increment_stat(SOURCE_TYPE, "seen")
            title = article.get("title","Unknown")
            link = article.get("link","Unknown")
            date = article.get("published","Unknown")
            author = article.get("author","Unknown")

            # Skip Duplicates
            if is_duplicate(link, existing_links):
                increment_stat(SOURCE_TYPE, "duplicates_removed")
                print("Duplicate skipped")
                continue

            # Extract Content
            try:
                content = extract_article(link)
            except Exception as e:
                increment_stat(SOURCE_TYPE, "quality_removed")
                print(f"Extraction failed: {e}")
                continue

            if not content:
                increment_stat(SOURCE_TYPE, "quality_removed")
                print(f"No content extracted:\n"
                    f"{link}")
                continue

            if not is_high_quality(content):
                increment_stat(SOURCE_TYPE, "quality_removed")
                print("Filtered: low quality content")
                continue

            filter_text = f"""
            {title}
            {content}
            """
            relevance = calculate_relevance(filter_text)

            if relevance["score"] == 0:
                filtered += 1
                increment_stat(SOURCE_TYPE, "irrelevant_removed")
                print("Filtered: no interest match")
                continue


            source_domain = (
                        urlparse(link)
                        .netloc
                        .replace("www.", "")
                        .lower()
                    )
            # Store Article
            article_data = create_item(
                source_type="rss",
                category=category,
                title=title,
                content=content[:10000],
                url=link,
                metadata={
                    "author": author,
                    "published": date,
                    "feed_url": feed_url,
                    "source_domain": source_domain,
                    "content_length": len(content),
                },
                filter_data={
                    "relevance_score":
                        relevance["score"],
                    "matched_topics":
                        relevance["matched_topics"],
                },
            )

            articles.append(article_data)
            existing_links.add(link)
            total_new_articles += 1
            increment_stat(SOURCE_TYPE, "stored")
            print(f"Saved: {title}")

save_articles(articles,json_file)
print(f"\nFinished. Added "f"{total_new_articles} "f"new articles.")
print(f"Total articles: "f"{len(articles)}")
print(f"Seen: {total_seen}")
print(f"Filtered: {filtered}")
print(f"Stored: {total_new_articles}")
