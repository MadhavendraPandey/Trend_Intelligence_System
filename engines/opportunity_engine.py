  # Configuration
  
TREND_WEIGHT = 0.30
SIGNAL_WEIGHT = 0.30
ACCELERATION_WEIGHT = 0.40


  # Helpers



def build_lookup(records):

    return {record["topic"]: record for record in records}


  # Opportunity Score
  

def calculate_opportunity_score(
    trend_score,
    signal_strength,
    acceleration_score,
):

    return round(
        (
            trend_score * TREND_WEIGHT
            + signal_strength * SIGNAL_WEIGHT
            + acceleration_score * ACCELERATION_WEIGHT
        ),
        2,
    )


  # Classification
  

def classify_opportunity(score):

    if score >= 150:
        return "BREAKOUT"

    if score >= 100:
        return "HIGH_POTENTIAL"

    if score >= 60:
        return "WATCHLIST"

    return "LOW_PRIORITY"


  # Confidence
  

def calculate_confidence(
    trend_score,
    signal_strength,
    acceleration_score,
):

    non_zero_signals = sum(
        [
            trend_score > 0,
            signal_strength > 0,
            acceleration_score > 0,
        ]
    )

    if non_zero_signals == 3:
        return "HIGH"

    if non_zero_signals == 2:
        return "MEDIUM"

    return "LOW"


  # Explanation
  

def build_reason(
    trend_score,
    signal_strength,
    acceleration_score,
):

    strongest = max(
        [
            ("trend activity", trend_score),
            ("signal strength", signal_strength),
            ("acceleration", acceleration_score),
        ],
        key=lambda x: x[1],
    )

    return f"Driven primarily by {strongest[0]}"


  # Main Engine
  

def analyze_opportunities(
    trends,
    signals,
    accelerations,
):

    signal_lookup = build_lookup(signals)

    acceleration_lookup = build_lookup(accelerations)

    opportunities = []

    for trend in trends:
        topic = trend["topic"]

        signal = signal_lookup.get(
            topic,
            {},
        )

        acceleration = acceleration_lookup.get(
            topic,
            {},
        )

        trend_score = trend.get(
            "trend_score",
            0,
        )

        signal_strength = signal.get(
            "signal_strength",
            0,
        )

        acceleration_score = acceleration.get(
            "acceleration_score",
            0,
        )

        opportunity_score = calculate_opportunity_score(
            trend_score,
            signal_strength,
            acceleration_score,
        )

        opportunity_level = classify_opportunity(opportunity_score)

        confidence = calculate_confidence(
            trend_score,
            signal_strength,
            acceleration_score,
        )

        opportunities.append(
            {
                "domain": trend["domain"],
                "theme": trend["theme"],
                "topic": topic,
                "trend_score": trend_score,
                "signal_strength": signal_strength,
                "acceleration_score": acceleration_score,
                "opportunity_score": opportunity_score,
                "opportunity_level": opportunity_level,
                "confidence": confidence,
                "reason": build_reason(
                    trend_score,
                    signal_strength,
                    acceleration_score,
                ),
            }
        )

    opportunities = sorted(
        opportunities,
        key=lambda x: x["opportunity_score"],
        reverse=True,
    )

    for rank, item in enumerate(
        opportunities,
        start=1,
    ):
        item["rank"] = rank

    return opportunities
