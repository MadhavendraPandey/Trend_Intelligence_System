# Imports

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

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
from stats.stats_manager import increment_stat
from utils import load_articles, save_articles,create_item

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# Configuration

json_file = PROJECT_ROOT / "articles.json"
SOURCE_TYPE = "arxiv"
ARXIV_API_URL = "https://export.arxiv.org/api/query"
RESULTS_PER_TARGET = 25

ARXIV_TARGETS = {
    "ai": {
        "category": "ai",
        "query": "cat:cs.AI",
    },
    "agents": {
        "category": "agent_frameworks",
        "query": "all:agents",
    },
    "cybersecurity": {
        "category": "cybersecurity",
        "query": "cat:cs.CR",
    },
    "llms": {
        "category": "ai",
        "query": "all:LLM",
    },
}

ATOM_NAMESPACE = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}



def fetch_arxiv_entries(query):
    params = urlencode({
        "search_query": query,
        "start": 0,
        "max_results": RESULTS_PER_TARGET,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })
    request = Request(
        f"{ARXIV_API_URL}?{params}",
        headers={
            "User-Agent": "trend-intelligence-arxiv-collector",
        },
        method="GET",
    )

    try:
        with urlopen(request, timeout=30) as response:
            xml_data = response.read()

    except HTTPError as error:
        message = error.read().decode("utf-8", errors="replace")
        print(f"Arxiv API error {error.code}: {message}")
        return []

    except URLError as error:
        print(f"Arxiv connection error: {error}")
        return []

    root = ET.fromstring(xml_data)
    return root.findall("atom:entry", ATOM_NAMESPACE)


def get_text(entry, path):
    element = entry.find(path, ATOM_NAMESPACE)

    if element is None or element.text is None:
        return ""

    return " ".join(element.text.split())


def get_authors(entry):
    authors = []

    for author in entry.findall("atom:author", ATOM_NAMESPACE):
        name = author.find("atom:name", ATOM_NAMESPACE)

        if name is not None and name.text:
            authors.append(name.text)

    return authors

def get_primary_category(entry):
    category = entry.find(
        "arxiv:primary_category",
        ATOM_NAMESPACE
    )

    if category is None:
        return ""

    return category.attrib.get(
        "term",
        ""
    )

def arxiv_entry_to_item(
    entry,
    category,
    target_name
):
    title = get_text(
        entry,
        "atom:title"
    )

    abstract = get_text(
        entry,
        "atom:summary"
    )

    url = get_text(
        entry,
        "atom:id"
    )

    authors = get_authors(
        entry
    )

    published = get_text(
        entry,
        "atom:published"
    )

    primary_category = (
        get_primary_category(
            entry
        )
    )

    filter_text = f"""
    {title}
    {abstract}
    {' '.join(authors)}
    {primary_category}
    """

    relevance = calculate_relevance(
        filter_text
    )

    content = f"""
Title:
{title}

Abstract:
{abstract}

Authors:
{", ".join(authors)}

Published:
{published}

Primary Category:
{primary_category}
"""

    return create_item(
        source_type="arxiv",

        category=category,

        title=title,

        content=content,

        url=url,

        metadata={

            "abstract":
                abstract,

            "source_domain": 
                "arxiv.org",

            "authors":
                authors,

            "author_count":
                len(authors),

            "published":
                published,

            "primary_category":
                primary_category,

            "collection_target":
                target_name,
        },

        filter_data={

            "relevance_score":
                relevance["score"],

            "matched_topics":
                relevance[
                    "matched_topics"
                ],
        },
    )


def collect_arxiv_items():
    articles = load_articles(json_file)
    existing_urls = build_url_index(articles)
    total_seen = 0
    duplicates = 0
    quality_removed = 0
    filtered = 0
    stored = 0

    print(f"Loaded {len(existing_urls)} existing URLs")

    for target_name, target in ARXIV_TARGETS.items():
        print(f"\n[{target_name.upper()}]")
        entries = fetch_arxiv_entries(target["query"])
        print(f"Papers: {len(entries)}")

        for entry in entries:
            total_seen += 1
            increment_stat(SOURCE_TYPE, "seen")
            item = arxiv_entry_to_item(
                entry,
                target["category"],
                target_name
            )
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

    print(f"\nFinished. Added {stored} Arxiv items.")
    print(f"Seen: {total_seen}")
    print(f"Duplicates: {duplicates}")
    print(f"Quality Removed: {quality_removed}")
    print(f"Filtered: {filtered}")
    print(f"Stored: {stored}")


if __name__ == "__main__":
    collect_arxiv_items()
