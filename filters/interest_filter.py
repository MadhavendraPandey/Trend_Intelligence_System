import re

from interests_goals import INTERESTS
from engines.topic_normalizer import normalize_topic

# Precomputed Topic Configuration

TOPIC_MAP = {}

for topic, config in INTERESTS.items():

    aliases = config.get("aliases", [])
    weight = config.get("weight", 1)

    compiled_patterns = []

    for alias in aliases:
        compiled_patterns.append(re.compile(rf"\b{re.escape(alias.lower())}\b"))

    TOPIC_MAP[topic] = {
        "weight": weight,
        "aliases": aliases,
        "patterns": compiled_patterns,
    }


# Topic Detection


def detect_topics(text):

    text = (text or "").lower()

    matched_topics = []
    topic_scores = {}
    topic_match_counts = {}

    for topic, config in TOPIC_MAP.items():

        weight = config["weight"]
        patterns = config["patterns"]

        total_matches = 0

        for pattern in patterns:

            matches = len(pattern.findall(text))

            total_matches += matches

        if total_matches == 0:
            continue

        normalized_topic = normalize_topic(topic)

        if normalized_topic not in matched_topics:
            matched_topics.append(normalized_topic)

        topic_scores[normalized_topic] = weight

        topic_match_counts[normalized_topic] = total_matches

    return (
        matched_topics,
        topic_scores,
        topic_match_counts,
    )


# Relevance Calculation


def calculate_relevance(text):

    (
        matched_topics,
        topic_scores,
        topic_match_counts,
    ) = detect_topics(text)

    relevance_score = sum(topic_scores.values())

    return {
        # Backward compatibility
        "score": relevance_score,
        # Explicit naming
        "relevance_score": relevance_score,
        "matched_topics": matched_topics,
        "topic_scores": topic_scores,
        "topic_match_counts": topic_match_counts,
        "topic_count": len(matched_topics),
        "is_relevant": relevance_score > 0,
    }


# Boolean Relevance Check


def is_relevant(text, minimum_score=1):
    relevance = calculate_relevance(text)
    return relevance["relevance_score"] >= minimum_score
