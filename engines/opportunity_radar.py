import json
from pathlib import Path

from engines.opportunity_engine import get_topic_opportunities
from engines.signal_strength import rank_signals
from engines.topic_normalizer import normalize_topics
from engines.trend_acceleration import (
    DEFAULT_GROWTH_WINDOW_DAYS,
    calculate_growth_rate,
    get_article_datetime,
)
from datetime import datetime, timedelta, timezone


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


def get_topic_signal_strength(articles):
    topic_totals = {}
    topic_counts = {}

    for article in rank_signals(articles):
        filter_data = article.get("filter_data") or {}
        matched_topics = normalize_topics(
            filter_data.get("matched_topics") or []
        )

        for topic in matched_topics:
            topic_totals[topic] = (
                topic_totals.get(topic, 0)
                + article.get("signal_strength", 0)
            )
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

    return {
        topic: topic_totals[topic] / topic_counts[topic]
        for topic in topic_totals
    }


def get_topic_growth_rates(articles):
    now = datetime.now(timezone.utc)
    window = timedelta(days=DEFAULT_GROWTH_WINDOW_DAYS)
    current_start = now - window
    previous_start = now - (window * 2)
    previous_end = current_start
    current_counts = {}
    previous_counts = {}

    for article in articles:
        article_datetime = get_article_datetime(article)

        if not article_datetime:
            continue

        filter_data = article.get("filter_data") or {}
        matched_topics = normalize_topics(
            filter_data.get("matched_topics") or []
        )

        if current_start <= article_datetime < now:
            target_counts = current_counts
        elif previous_start <= article_datetime < previous_end:
            target_counts = previous_counts
        else:
            continue

        for topic in matched_topics:
            target_counts[topic] = target_counts.get(topic, 0) + 1

    topics = set(current_counts) | set(previous_counts)

    return {
        topic: calculate_growth_rate(
            previous_counts.get(topic, 0),
            current_counts.get(topic, 0)
        )
        for topic in topics
    }


def get_opportunity_radar(articles=None, limit=20):
    articles = articles or load_articles()
    topic_opportunities = {
        item["topic"]: item["score"]
        for item in get_topic_opportunities(articles)
    }
    topic_growth = get_topic_growth_rates(articles)
    topic_signals = get_topic_signal_strength(articles)
    topics = set(topic_opportunities) | set(topic_growth) | set(topic_signals)

    radar = []

    for topic in topics:
        opportunity_score = topic_opportunities.get(topic, 0)
        growth_rate = topic_growth.get(topic, 0)
        signal_strength = topic_signals.get(topic, 0)
        radar_score = (
            opportunity_score
            + max(0, growth_rate)
            + signal_strength
        )

        radar.append({
            "topic": topic,
            "score": round(radar_score, 2),
            "opportunity_score": round(opportunity_score, 2),
            "growth_rate": round(growth_rate, 2),
            "signal_strength": round(signal_strength, 2),
        })

    return sorted(
        radar,
        key=lambda item: (-item["score"], item["topic"])
    )[:limit]
