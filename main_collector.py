import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

COLLECTORS = [
    "rss_collector.py",
    "github_collector.py",
    # "reddit_collector.py",
    "hackernews_collector.py",
    "arxiv_collector.py",
]


def run_collector(collector_name):
    collector_path = PROJECT_ROOT / "collectors" / collector_name

    print()
    print("=" * 70)
    print(f"Running {collector_name}")
    print("=" * 70)

    result = subprocess.run(
        [
            sys.executable,
            str(collector_path),
        ],
        cwd=PROJECT_ROOT,
        check=False,
    )

    if result.returncode != 0:
        print(f"{collector_name} failed with exit code {result.returncode}")

    return result.returncode


def run_all_collectors():
    failures = []

    for collector_name in COLLECTORS:
        return_code = run_collector(collector_name)

        if return_code != 0:
            failures.append(collector_name)

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
