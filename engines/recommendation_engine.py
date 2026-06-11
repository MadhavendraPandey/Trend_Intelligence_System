from interests_goals import GOALS, INTERESTS
from engines.opportunity_engine import get_topic_opportunities
from engines.topic_normalizer import normalize_topic
from engines.trend_engine import get_top_topics


LEARN = "LEARN"
BUILD = "BUILD"
MONITOR = "MONITOR"
IGNORE = "IGNORE"

BUILD_THRESHOLD = 800
LEARN_THRESHOLD = 500


def build_recommendation(topic, recommendation, reason):
    return {
        "topic": topic,
        "recommendation": recommendation,
        "reason": reason,
    }


def get_topic_score(topic_result):
    return topic_result.get("score", 0) or 0


def get_topic_name(topic_result):
    return normalize_topic(topic_result.get("topic", ""))


def get_build_recommendations(topic_opportunities):
    recommendations = []

    for topic_result in topic_opportunities:
        score = get_topic_score(topic_result)

        if score >= BUILD_THRESHOLD:
            recommendations.append(
                build_recommendation(
                    get_topic_name(topic_result),
                    BUILD,
                    "High opportunity score"
                )
            )

    return recommendations


def get_learning_recommendations(topic_opportunities):
    recommendations = []

    for topic_result in topic_opportunities:
        score = get_topic_score(topic_result)

        if LEARN_THRESHOLD <= score < BUILD_THRESHOLD:
            recommendations.append(
                build_recommendation(
                    get_topic_name(topic_result),
                    LEARN,
                    "Strong capability gain potential"
                )
            )

    return recommendations


def get_monitor_recommendations(
    top_topics,
    excluded_topics=None
):
    excluded_topics = excluded_topics or set()
    recommendations = []

    for topic_result in top_topics:
        topic = get_topic_name(topic_result)

        if not topic:
            continue

        if topic in excluded_topics:
            continue

        recommendations.append(
            build_recommendation(
                topic,
                MONITOR,
                "Growing trend"
            )
        )

    return recommendations


def get_recommended_topics(*recommendation_groups):
    topics = set()

    for group in recommendation_groups:
        for recommendation in group:
            topic = recommendation.get("topic")

            if topic:
                topics.add(topic)

    return topics


def generate_recommendations(
    topic_opportunities,
    top_topics
):
    build = get_build_recommendations(topic_opportunities)
    learn = get_learning_recommendations(topic_opportunities)
    excluded_topics = get_recommended_topics(build, learn)
    monitor = get_monitor_recommendations(
        top_topics,
        excluded_topics
    )

    return {
        "build": build,
        "learn": learn,
        "monitor": monitor,
    }
