import math
from datetime import datetime, timezone

from engines.opportunity_engine import calculate_opportunity_score, has_analysis
from engines.trend_acceleration import get_article_datetime
from filters.source_quality import get_source_quality


def get_source_type(article):
    if article.get("source_type"):
        return article.get("source_type")

    if article.get("source"):
        return "rss"

    return "unknown"


def calculate_recency_score(article):
    article_datetime = get_article_datetime(article)

    if not article_datetime:
        return 0

    age_days = (
        datetime.now(timezone.utc) - article_datetime
    ).days

    if age_days <= 1:
        return 10

    if age_days <= 7:
        return 8

    if age_days <= 30:
        return 6

    if age_days <= 90:
        return 3

    return 1


def calculate_github_star_score(article):
    metadata = article.get("metadata") or {}
    stars = metadata.get("stars", 0) or 0

    if stars <= 0:
        return 0

    return min(10, math.log10(stars + 1) * 2)


def calculate_signal_strength(article):
    filter_data = article.get("filter_data") or {}
    relevance_score = min(filter_data.get("relevance_score", 0) or 0, 10)

    opportunity_score = 0
    if has_analysis(article):
        opportunity_score = min(calculate_opportunity_score(article), 40) / 4

    source_quality = get_source_quality(get_source_type(article))
    github_star_score = calculate_github_star_score(article)
    recency_score = calculate_recency_score(article)

    signal_strength = (
        (relevance_score * 0.25)
        + (opportunity_score * 0.30)
        + (source_quality * 0.20)
        + (github_star_score * 0.10)
        + (recency_score * 0.15)
    ) * 10

    return round(min(100, max(0, signal_strength)), 2)


def rank_signals(articles):
    ranked_articles = []

    for article in articles:
        ranked_article = article.copy()
        ranked_article["signal_strength"] = calculate_signal_strength(article)
        ranked_articles.append(ranked_article)

    return sorted(
        ranked_articles,
        key=lambda item: item.get("signal_strength", 0),
        reverse=True
    )
