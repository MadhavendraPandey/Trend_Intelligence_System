TOPIC_NORMALIZATION_MAP = {
    "AI Agents": [
        "AI Agent",
        "AI Agents",
        "Agentic AI",
        "Agentic Agents",
        "Agentic Workflows",
        "Autonomous Agent",
        "Autonomous Agents",
        "AI Agent Frameworks",
        "Agent Frameworks",
    ],
    "Cybersecurity": [
        "Cyber Security",
        "Cybersecurity",
        "Cyber-Security",
        "Information Security",
        "InfoSec",
    ],
    "Local LLMs": [
        "Local LLM",
        "Local LLMs",
        "On-Device LLMs",
        "Offline LLMs",
    ],
    "Security Automation": [
        "Security Automation",
        "Cybersecurity Automation",
        "Automated Security",
        "Detection Automation",
    ],
    "Developer Tools": [
        "Developer Tool",
        "Developer Tools",
        "Dev Tools",
        "DevTools",
        "Developer Productivity",
    ],
}


def build_variant_lookup():
    variant_lookup = {}

    for canonical_topic, variants in TOPIC_NORMALIZATION_MAP.items():
        variant_lookup[canonical_topic.lower()] = canonical_topic

        for variant in variants:
            variant_lookup[variant.lower()] = canonical_topic

    return variant_lookup


def normalize_topic(topic):
    if not topic:
        return topic

    cleaned_topic = topic.strip()
    variant_lookup = build_variant_lookup()

    return variant_lookup.get(
        cleaned_topic.lower(),
        cleaned_topic
    )


def normalize_topics(topic_list):
    normalized_topics = []
    seen_topics = set()

    for topic in topic_list:
        normalized_topic = normalize_topic(topic)

        if not normalized_topic:
            continue

        if normalized_topic in seen_topics:
            continue

        normalized_topics.append(normalized_topic)
        seen_topics.add(normalized_topic)

    return normalized_topics
