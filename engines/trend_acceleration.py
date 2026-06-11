import json
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from engines.topic_normalizer import normalize_topics


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

json_file = PROJECT_ROOT / "articles.json"
DEFAULT_GROWTH_WINDOW_DAYS = 7


def load_items():
    if not json_file.exists():
        return []

    with open(
        json_file,
        "r",
        encoding="utf-8"
    ) as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []


def parse_datetime(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError):
        pass

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (AttributeError, ValueError):
        return None


def get_article_datetime(article):
    metadata = article.get("metadata") or {}

    for field_name in [
        "date",
        "published_at",
        "created_at",
        "updated_at",
        "pushed_at",
    ]:
        parsed = parse_datetime(article.get(field_name))
        if parsed:
            return parsed

        parsed = parse_datetime(metadata.get(field_name))
        if parsed:
            return parsed

    return None


def get_topic_counts_by_timeframe(days):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    topic_counts = {}

    for article in load_items():
        article_datetime = get_article_datetime(article)

        if not article_datetime or article_datetime < cutoff:
            continue

        filter_data = article.get("filter_data") or {}
        matched_topics = normalize_topics(
            filter_data.get("matched_topics") or []
        )

        for topic in matched_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

    return topic_counts


def calculate_growth_rate(previous_count, current_count):
    if previous_count == 0:
        if current_count == 0:
            return 0.0

        return float(current_count * 100)

    return ((current_count - previous_count) / previous_count) * 100


def get_topic_counts_between(start_datetime, end_datetime):
    topic_counts = {}

    for article in load_items():
        article_datetime = get_article_datetime(article)

        if not article_datetime:
            continue

        if article_datetime < start_datetime or article_datetime >= end_datetime:
            continue

        filter_data = article.get("filter_data") or {}
        matched_topics = normalize_topics(
            filter_data.get("matched_topics") or []
        )

        for topic in matched_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

    return topic_counts


def get_fastest_growing_topics(limit=20):
    now = datetime.now(timezone.utc)
    window = timedelta(days=DEFAULT_GROWTH_WINDOW_DAYS)

    current_counts = get_topic_counts_between(now - window, now)
    previous_counts = get_topic_counts_between(now - (window * 2), now - window)
    topics = set(current_counts) | set(previous_counts)

    growth_results = []

    for topic in topics:
        growth_results.append({
            "topic": topic,
            "growth_rate": calculate_growth_rate(
                previous_counts.get(topic, 0),
                current_counts.get(topic, 0)
            )
        })

    return sorted(
        growth_results,
        key=lambda item: (-item["growth_rate"], item["topic"])
    )[:limit]
