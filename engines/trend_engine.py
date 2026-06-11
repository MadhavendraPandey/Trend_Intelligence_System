import json
from pathlib import Path

from engines.topic_normalizer import normalize_topics


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

json_file = PROJECT_ROOT / "articles.json"


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


def get_topic_counts():
    topic_counts = {}

    for item in load_items():
        filter_data = item.get("filter_data") or {}
        matched_topics = filter_data.get("matched_topics") or []
        matched_topics = normalize_topics(matched_topics)

        for topic in matched_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

    return [
        {
            "topic": topic,
            "count": count,
        }
        for topic, count in sorted(
            topic_counts.items(),
            key=lambda item: (-item[1], item[0])
        )
    ]


def get_top_topics(limit=20):
    return get_topic_counts()[:limit]


def get_top_relevance_topics(limit=20):
    topic_scores = {}

    for item in load_items():
        filter_data = item.get("filter_data") or {}
        matched_topics = filter_data.get("matched_topics") or []
        matched_topics = normalize_topics(matched_topics)
        relevance_score = filter_data.get("relevance_score") or 0

        for topic in matched_topics:
            topic_scores[topic] = topic_scores.get(topic, 0) + relevance_score

    return [
        {
            "topic": topic,
            "count": count,
        }
        for topic, count in sorted(
            topic_scores.items(),
            key=lambda item: (-item[1], item[0])
        )
    ][:limit]
