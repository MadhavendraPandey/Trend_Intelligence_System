from engines.recommendation_engine import generate_recommendations


def get_known_topics(interests):
    topics = set()

    for topic_list in interests.values():
        for topic in topic_list:
            topics.add(topic)

    return topics


def build_ignore_recommendations(
    trends,
    opportunities,
    selected_topics
):
    opportunity_topics = {
        item.get("topic")
        for item in opportunities
    }
    trend_topics = {
        item.get("topic")
        for item in trends
    }
    all_topics = opportunity_topics | trend_topics

    ignore_topics = sorted(
        topic for topic in all_topics
        if topic and topic not in selected_topics
    )

    return [
        {
            "topic": topic,
            "recommendation": "IGNORE",
            "reason": "Low strategic fit or weak opportunity signal"
        }
        for topic in ignore_topics
    ]


def get_strategy(
    interests,
    goals,
    trends,
    opportunities
):
    recommendations = generate_recommendations(
        opportunities,
        trends
    )
    selected_topics = {
        item["topic"]
        for group in recommendations.values()
        for item in group
    }

    return {
        "what_to_learn": recommendations["learn"],
        "what_to_build": recommendations["build"],
        "what_to_monitor": recommendations["monitor"],
        "what_to_ignore": build_ignore_recommendations(
            trends,
            opportunities,
            selected_topics
        ),
        "context": {
            "interest_count": len(get_known_topics(interests)),
            "goal_count": len(goals),
        }
    }
