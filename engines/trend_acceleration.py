
# ==========================================================
# Configuration
# ==========================================================

TREND_GROWTH_WEIGHT = 0.70
SIGNAL_GROWTH_WEIGHT = 0.30


# ==========================================================
# Helpers
# ==========================================================


def build_lookup(records):

    return {record["topic"]: record for record in records}


# ==========================================================
# Growth Calculation
# ==========================================================


def calculate_growth(
    current_value,
    previous_value,
):

    if previous_value <= 0:
        if current_value > 0:
            return 100.0

        return 0.0

    growth = ((current_value - previous_value) / previous_value) * 100

    return round(growth, 2)


# ==========================================================
# Acceleration Score
# ==========================================================


def calculate_acceleration_score(
    trend_growth,
    signal_growth,
):

    return round(
        (trend_growth * TREND_GROWTH_WEIGHT) + (signal_growth * SIGNAL_GROWTH_WEIGHT),
        2,
    )


# ==========================================================
# Classification
# ==========================================================


def classify_acceleration(score):

    if score >= 100:
        return "EXPLODING"

    if score >= 50:
        return "RAPID"

    if score >= 20:
        return "GROWING"

    if score > 0:
        return "STABLE"

    return "DECLINING"


# ==========================================================
# Confidence
# ==========================================================


def calculate_confidence(
    current_trend_score,
    current_signal_strength,
):

    if current_trend_score >= 100 and current_signal_strength >= 80:
        return "HIGH"

    if current_trend_score >= 40 and current_signal_strength >= 30:
        return "MEDIUM"

    return "LOW"


# ==========================================================
# Explanation
# ==========================================================


def build_reason(
    trend_growth,
    signal_growth,
):

    if trend_growth > signal_growth:
        return "Momentum driven primarily by trend growth"

    if signal_growth > trend_growth:
        return "Momentum driven primarily by signal growth"

    return "Trend and signal growth are increasing together"


# ==========================================================
# Main Engine
# ==========================================================


def analyze_acceleration(
    current_trends,
    previous_trends,
    current_signals,
    previous_signals,
):

    trend_lookup = build_lookup(previous_trends)

    signal_lookup = build_lookup(previous_signals)

    current_signal_lookup = build_lookup(current_signals)

    results = []

    for current in current_trends:
        topic = current["topic"]

        previous = trend_lookup.get(
            topic,
            {},
        )

        current_trend_score = current.get(
            "trend_score",
            0,
        )

        previous_trend_score = previous.get(
            "trend_score",
            0,
        )

        trend_growth = calculate_growth(
            current_trend_score,
            previous_trend_score,
        )

        current_signal = current_signal_lookup.get(
            topic,
            {},
        )

        previous_signal = signal_lookup.get(
            topic,
            {},
        )

        current_signal_strength = current_signal.get(
            "signal_strength",
            0,
        )

        previous_signal_strength = previous_signal.get(
            "signal_strength",
            0,
        )

        signal_growth = calculate_growth(
            current_signal_strength,
            previous_signal_strength,
        )

        acceleration_score = calculate_acceleration_score(
            trend_growth,
            signal_growth,
        )

        results.append(
            {
                "domain": current["domain"],
                "theme": current["theme"],
                "topic": topic,
                "trend_growth": trend_growth,
                "signal_growth": signal_growth,
                "acceleration_score": acceleration_score,
                "acceleration_level": classify_acceleration(acceleration_score),
                "confidence": calculate_confidence(
                    current_trend_score,
                    current_signal_strength,
                ),
                "reason": build_reason(
                    trend_growth,
                    signal_growth,
                ),
            }
        )

    results = sorted(
        results,
        key=lambda x: x["acceleration_score"],
        reverse=True,
    )

    for rank, item in enumerate(
        results,
        start=1,
    ):
        item["rank"] = rank

    return results
