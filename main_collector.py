import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

from collectors.rss_collector import collect_rss_items
from collectors.github_collector import collect_github_items
from collectors.hackernews_collector import collect_hackernews_items
from collectors.arxiv_collector import collect_arxiv_items
# from collectors.reddit_collector import collect_reddit_items

COLLECTORS = [
    ("rss", collect_rss_items),
    ("github", collect_github_items),
    ("hackernews", collect_hackernews_items),
    ("arxiv", collect_arxiv_items),
]


def run_all_collectors():
    failures = []

    for name, collector_func in COLLECTORS:
        print()
        print("=" * 70)
        print(f"Running {name}_collector")
        print("=" * 70)

        try:
            return_code = collector_func()
            if return_code != 0:
                failures.append(name)
        except Exception as e:
            print(f"{name}_collector failed with error: {e}")
            failures.append(name)

    print()
    print("=" * 70)
    print("Collection complete")
    print("=" * 70)

    if failures:
        print("Failed collectors:")
        for collector_name in failures:
            print(f"- {collector_name}")
        return 1

    print("All collectors completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_all_collectors())
