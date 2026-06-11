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


def load_articles():
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


def get_analysis_score(article, field_name):
    analysis = article.get("analysis") or {}
    field = analysis.get(field_name) or {}

    return field.get("score", 0) or 0


def has_analysis(article):
    return isinstance(article.get("analysis"), dict)


def calculate_opportunity_score(article):
    novelty = get_analysis_score(article, "novelty")
    actionability = get_analysis_score(article, "actionability")
    learning_value = get_analysis_score(article, "learning_value")
    monetization_potential = get_analysis_score(
        article,
        "monetization_potential"
    )
    required_cost = get_analysis_score(article, "required_cost") or 1

    return (
        novelty
        + actionability
        + learning_value
        + monetization_potential
    ) / required_cost


def get_opportunities(articles):
    opportunities = []

    for article in articles:
        if not has_analysis(article):
            continue

        opportunity = article.copy()
        opportunity["opportunity_score"] = calculate_opportunity_score(article)
        opportunities.append(opportunity)

    return opportunities


def get_top_opportunities(articles, limit=20):
    opportunities = get_opportunities(articles)

    return sorted(
        opportunities,
        key=lambda article: article.get("opportunity_score", 0),
        reverse=True
    )[:limit]


def get_topic_opportunities(articles):
    topic_scores = {}

    for article in get_opportunities(articles):
        filter_data = article.get("filter_data") or {}
        matched_topics = filter_data.get("matched_topics") or []
        matched_topics = normalize_topics(matched_topics)
        opportunity_score = article.get("opportunity_score", 0)

        for topic in matched_topics:
            topic_scores[topic] = (
                topic_scores.get(topic, 0)
                + opportunity_score
            )

    return [
        {
            "topic": topic,
            "score": score,
        }
        for topic, score in sorted(
            topic_scores.items(),
            key=lambda item: (-item[1], item[0])
        )
    ]
