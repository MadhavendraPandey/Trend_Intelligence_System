import json   
from pathlib import Path
import feedparser
import trafilatura
from google import genai
from dotenv import load_dotenv
import os
from feeds import FEEDS

load_dotenv()


# Gemini Client

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env file"
    )

client = genai.Client(
    api_key=api_key
)


# Summarization

def summarize_article(content):

    prompt = f"""
You are a trend intelligence analyst.

Return ONLY valid JSON.

Do not use markdown.
Do not use code fences.
Do not add explanations.
Do not add any text before or after the JSON.

Schema:

{{
  "overview": "...",
  "tags": ["...", "..."],
  "importance": 1,
  "key_points": [
    "...",
    "...",
    "..."
  ],
  "why_it_matters": "..."
}}

Article:

{content}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text



# Content Extraction

def extract_article(url):

    downloaded = trafilatura.fetch_url(url)

    if not downloaded:
        return None

    return trafilatura.extract(downloaded)


# JSON Storage

json_file = Path("articles.json")


# Load existing articles if file exists

if json_file.exists():

    with open(json_file, "r", encoding="utf-8") as file:
        try:
            articles = json.load(file)
        except json.JSONDecodeError:
            articles = []

else:

    articles = []

# Build Deduplication Set

existing_links = set()

for article in articles:
    existing_links.add(
        article.get("link",""))

print(f"Loaded {len(existing_links)} existing articles")

# Process Feeds
total_new_articles = 0

for category, feed_urls in FEEDS.items():
    for feed_url in feed_urls:
        print(
            f"\n[{category.upper()}] "
            f"Reading: {feed_url}"
        )

        parsed_feed = feedparser.parse(feed_url)
        if not parsed_feed.entries:
            print("No articles found")
            continue

        feed_new_articles = 0

        # Limit to 1 article while testing to avoid hitting API limits and speed up processing. Remove [:1] to process all articles.
        for article in parsed_feed.entries[:1]:

            title = article.get("title", "Unknown")
            link = article.get("link", "Unknown")
            date = article.get("published", "Unknown")
            author = article.get("author", "Unknown")

            # Skip duplicates

            if link in existing_links:

                print("Duplicate skipped")

                continue

            # Extract content
            try:
                content = extract_article(link)
            except Exception as e:
                print(f"Extraction failed: {e}")
                continue
            if not content:
                print("No content extracted")
                continue

            full_content = content

        # Generate summary

            try:

                summary = summarize_article(content[:2000]) #Limit: 2000 characters for summarization to reduce cost and speed up processing.
                summary = summary.strip()

                if summary.startswith("```json"):
                    summary = summary.replace("```json", "", 1)

                if summary.endswith("```"):
                    summary = summary[:-3]

                summary = summary.strip()
                analysis = json.loads(summary)

            except Exception as e:

                print(f"Summary error: {e}")

                continue

            # Print results

            print("\n" + "=" * 70)

            print(f"TITLE:\n{title}")

            print(f"\nCONTENT LENGTH: {len(content)}")

            print("\nSUMMARY:\n")

            print(summary)

            print("=" * 70)

            # Store article

            article_data = {
                "title": title,
                "link": link,
                "date": date,
                "source": feed_url,
                "author": author,
                "category": category,
                "content": full_content[:10000],
                "analysis": analysis
            }

            articles.append(article_data)

            existing_links.add(link)

            feed_new_articles += 1
            total_new_articles += 1

        print(
            f"Added {feed_new_articles} new articles "
            f"from this feed"
        )


# Save Updated JSON

with open(
    json_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        articles,
        file,
        indent=4,
        ensure_ascii=False
    )


print(
    f"\nFinished. Added {total_new_articles} "
    f"new articles in total."
)

