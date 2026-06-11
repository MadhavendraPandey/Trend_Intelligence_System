import json
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

STATS_FILE = PROJECT_ROOT / "stats" / "collection_stats.json"

METRICS = [
    "seen",
    "duplicates_removed",
    "quality_removed",
    "irrelevant_removed",
    "stored",
]

DEFAULT_SOURCES = [
    "rss",
    "github",
    "reddit",
    "hackernews",
    "arxiv",
]


def build_empty_source_stats():
    return {
        metric: 0
        for metric in METRICS
    }


def ensure_stats_file():
    STATS_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not STATS_FILE.exists():
        save_stats({})


def normalize_stats(stats):
    normalized_stats = {}

    for source in DEFAULT_SOURCES:
        normalized_stats[source] = build_empty_source_stats()

    for source, source_stats in (stats or {}).items():
        normalized_stats.setdefault(source, build_empty_source_stats())
        normalized_stats[source].update(source_stats or {})

    return normalized_stats


def load_stats():
    ensure_stats_file()

    try:
        with STATS_FILE.open("r", encoding="utf-8") as file:
            return normalize_stats(json.load(file))

    except json.JSONDecodeError:
        stats = normalize_stats({})
        save_stats(stats)
        return stats


def save_stats(stats):
    STATS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with STATS_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            normalize_stats(stats),
            file,
            indent=4,
            ensure_ascii=False
        )


def increment_stat(source, metric):
    if metric not in METRICS:
        raise ValueError(f"Unknown collection stat metric: {metric}")

    stats = load_stats()
    source_stats = stats.setdefault(source, build_empty_source_stats())
    source_stats[metric] += 1
    save_stats(stats)


def get_stats():
    return load_stats()
