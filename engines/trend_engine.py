from collections import defaultdict

from engines.topic_normalizer import (
    normalize_text,
)

# ==========================================================
# Configuration
# ==========================================================

MENTION_WEIGHT = 1
SOURCE_WEIGHT = 10
CATEGORY_WEIGHT = 5


# ==========================================================
# Helpers
# ==========================================================


def build_trends(items):

    trends = {}

    for item in items:
        content = item.get(
            "content",
            "",
        )

        source_type = item.get(
            "source_type",
            "unknown",
        )

        category = item.get(
            "category",
            "unknown",
        )

        matches = normalize_text(content)

        for match in matches:
            topic = match["topic"]

            if topic not in trends:
                trends[topic] = {
                    "domain": match["domain"],
                    "theme": match["theme"],
                    "topic": topic,
                    "mentions": 0,
                    "sources": set(),
                    "categories": set(),
                    "entities": defaultdict(int),
                }

            trends[topic]["mentions"] += 1

            trends[topic]["sources"].add(source_type)

            trends[topic]["categories"].add(category)

            trends[topic]["entities"][match["matched_entity"]] += 1

    return trends


# ==========================================================
# Scoring
# ==========================================================


def calculate_trend_score(
    mentions,
    source_count,
    category_count,
):

    return round(
        (mentions * MENTION_WEIGHT)
        + (source_count * SOURCE_WEIGHT)
        + (category_count * CATEGORY_WEIGHT),
        2,
    )


# ==========================================================
# Classification
# ==========================================================


def classify_trend(trend_score):

    if trend_score >= 100:
        return "DOMINANT"

    if trend_score >= 60:
        return "STRONG"

    if trend_score >= 30:
        return "EMERGING"

    return "WEAK"


# ==========================================================
# Confidence
# ==========================================================


def calculate_confidence(
    source_count,
    category_count,
):

    if source_count >= 4 and category_count >= 3:
        return "HIGH"

    if source_count >= 2 and category_count >= 2:
        return "MEDIUM"

    return "LOW"


# ==========================================================
# Ranking
# ==========================================================


def rank_trends(trends):

    results = []

    for topic, data in trends.items():
        mentions = data["mentions"]

        source_count = len(data["sources"])

        category_count = len(data["categories"])

        trend_score = calculate_trend_score(
            mentions,
            source_count,
            category_count,
        )

        top_entities = sorted(
            data["entities"].items(),
            key=lambda x: x[1],
            reverse=True,
        )[:10]

        results.append(
            {
                "domain": data["domain"],
                "theme": data["theme"],
                "topic": topic,
                "mentions": mentions,
                "source_count": source_count,
                "category_count": category_count,
                "source_types": sorted(list(data["sources"])),
                "categories": sorted(list(data["categories"])),
                "top_entities": [entity for entity, _ in top_entities],
                "trend_score": trend_score,
                "trend_level": classify_trend(trend_score),
                "confidence": calculate_confidence(
                    source_count,
                    category_count,
                ),
            }
        )

    results = sorted(
        results,
        key=lambda x: x["trend_score"],
        reverse=True,
    )

    for rank, trend in enumerate(
        results,
        start=1,
    ):
        trend["rank"] = rank

    return results


# ==========================================================
# Main Engine
# ==========================================================


def analyze_trends(items):

    trends = build_trends(items)

    return rank_trends(trends)
