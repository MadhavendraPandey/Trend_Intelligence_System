# ==========================================================
# Recommendation Types
# ==========================================================

BUILD = "BUILD"

LEARN = "LEARN"

MONITOR = "MONITOR"


# ==========================================================
# Thresholds
# ==========================================================

BUILD_THRESHOLD = 150

LEARN_THRESHOLD = 100

MONITOR_THRESHOLD = 60


# ==========================================================
# Helper
# ==========================================================


def build_recommendation(
    topic,
    recommendation,
    reason,
):

    return {
        "topic": topic,
        "recommendation": recommendation,
        "reason": reason,
    }


# ==========================================================
# Main Engine
# ==========================================================


def generate_recommendations(
    opportunities,
):

    build = []

    learn = []

    monitor = []

    for item in opportunities:

        topic = item["topic"]

        score = item["opportunity_score"]

        if score >= BUILD_THRESHOLD:

            build.append(
                build_recommendation(
                    topic,
                    BUILD,
                    "High opportunity score",
                )
            )

        elif score >= LEARN_THRESHOLD:

            learn.append(
                build_recommendation(
                    topic,
                    LEARN,
                    "Strong future potential",
                )
            )

        elif score >= MONITOR_THRESHOLD:

            monitor.append(
                build_recommendation(
                    topic,
                    MONITOR,
                    "Emerging trend worth tracking",
                )
            )

    return {
        "build": build,
        "learn": learn,
        "monitor": monitor,
    }
