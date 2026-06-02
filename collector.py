import feedparser
import csv
from pathlib import Path

feeds = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://techcrunch.com/category/startups/feed/",
    "https://huggingface.co/blog/feed.xml"
]

csv_file = Path("articles.csv")

existing_links = set()

if Path(csv_file).exists():

    with open(csv_file, "r", encoding="utf-8") as article_file:

        reader = csv.reader(article_file)

        next(reader, None)

        for item in reader:

            if len(item) >= 2:
                existing_links.add(item[1])

print(f"Loaded {len(existing_links)} existing links")

file_exists = Path(csv_file).exists()


with open(
    csv_file,
    "a",
    newline="",
    encoding="utf-8"
) as article_file:

    writer = csv.writer(article_file)

    if not file_exists:
        writer.writerow([
            "Title",
            "Link",
            "Date",
            "Author"
        ])

    total_new_articles = 0

    for feed_url in feeds:
        print(f"\nReading: {feed_url}")
        feed = feedparser.parse(feed_url)
        feed_new_articles = 0

        for article in feed.entries:

            title = article.get("title", "Unknown")
            link = article.get("link", "Unknown")
            date = article.get("published", "Unknown")
            author = article.get("author", "Unknown")

            if link in existing_links:
                continue

            writer.writerow([
                title,
                link,
                date,
                author
            ])

            existing_links.add(link)

            feed_new_articles += 1
            total_new_articles += 1

        print(
            f"Added {feed_new_articles} new articles "
            f"from this feed"
        )

print(
    f"\nFinished. Added {total_new_articles} "
    f"new articles in total."
)


