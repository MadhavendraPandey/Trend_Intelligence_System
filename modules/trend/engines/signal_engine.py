  # Source Weights
  
SOURCE_WEIGHTS = {
    "arxiv": 10,
    "github": 8,
    "hackernews": 7,
    "rss": 6,
    "reddit": 4,
}

  # Helpers
  

def get_source_weight(source_type):

    return SOURCE_WEIGHTS.get(
        source_type.lower(),
        1,
    )


  # Build Signal Data
  

def build_signal_data(
    items,
    trends,
):

    topic_signals = {}

    for trend in trends:
        topic_signals[trend["topic"]] = {
            "domain": trend["domain"],
            "theme": trend["theme"],
            "sources": set(),
            "source_score": 0,
            "engagement": 0,
            "research_present": False,
            "github_repos": 0,
            "hn_posts": 0,
            "articles": 0,
        }

    for item in items:
        filter_data = item.get("filter_data", {})

        matched_topics = filter_data.get("matched_topics", [])

        source_type = item.get("source_type", "")

        metadata = item.get("metadata", {})

        for topic in matched_topics:
            if topic not in topic_signals:
                continue

            signal = topic_signals[topic]

            signal["sources"].add(source_type)

            signal["source_score"] += get_source_weight(source_type)

            signal["articles"] += 1

            if source_type == "arxiv":
                signal["research_present"] = True

            if source_type == "github":
                signal["github_repos"] += 1

                signal["engagement"] += min(metadata.get("stars", 0), 5000) * 0.01

            if source_type == "hackernews":
                signal["hn_posts"] += 1

                signal["engagement"] += metadata.get("score", 0) * 0.1

                signal["engagement"] += metadata.get("comments", 0) * 0.05

    return topic_signals


  # Signal Strength
  

def calculate_signal_strength(signal):

    source_diversity = len(signal["sources"])

    source_score = signal["source_score"]

    engagement = signal["engagement"]

    research_bonus = 20 if (signal["research_present"]) else 0

    return round(
        source_score + (source_diversity * 15) + research_bonus + engagement,
        2,
    )


  # Classification
  

def classify_signal(strength):

    if strength >= 120:
        return "VERY_STRONG"

    if strength >= 80:
        return "STRONG"

    if strength >= 40:
        return "MODERATE"

    return "WEAK"


  # Confidence
  

def calculate_confidence(signal):

    diversity = len(signal["sources"])

    if diversity >= 4 and signal["research_present"]:
        return "HIGH"

    if diversity >= 2:
        return "MEDIUM"

    return "LOW"


  # Explanation
  

def build_reason(signal):

    reasons = []

    if signal["research_present"]:
        reasons.append("research backing")

    if len(signal["sources"]) >= 3:
        reasons.append("multi-source coverage")

    if signal["engagement"] > 20:
        reasons.append("strong community engagement")

    if not reasons:
        reasons.append("limited validation")

    return ", ".join(reasons)


  # Main Engine
  

def analyze_signal_strength(
    items,
    trends,
):

    topic_signals = build_signal_data(
        items,
        trends,
    )

    results = []

    for topic, signal in topic_signals.items():
        strength = calculate_signal_strength(signal)

        results.append(
            {
                "domain": signal["domain"],
                "theme": signal["theme"],
                "topic": topic,
                "source_count": len(signal["sources"]),
                "sources": sorted(list(signal["sources"])),
                "articles": signal["articles"],
                "github_repos": signal["github_repos"],
                "hn_posts": signal["hn_posts"],
                "research_present": signal["research_present"],
                "signal_strength": strength,
                "signal_level": classify_signal(strength),
                "confidence": calculate_confidence(signal),
                "reason": build_reason(signal),
            }
        )

    results = sorted(
        results,
        key=lambda x: x["signal_strength"],
        reverse=True,
    )

    for rank, item in enumerate(
        results,
        start=1,
    ):
        item["rank"] = rank

    return results
