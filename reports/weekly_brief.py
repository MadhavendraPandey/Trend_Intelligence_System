from pathlib import Path
import sys


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from engines.opportunity_engine import (
    get_topic_opportunities,
    get_top_opportunities,
)
from engines.recommendation_engine import generate_recommendations
from engines.trend_acceleration import get_fastest_growing_topics
from engines.trend_engine import get_top_topics
from utils import load_articles


json_file = PROJECT_ROOT / "articles.json"
brief_file = PROJECT_ROOT / "reports" / "weekly_brief_output.md"


def format_topic_counts(topics):
    if not topics:
        return "- No data yet."

    return "\n".join(
        f"- {item['topic']}: {item.get('count', item.get('score', 0))}"
        for item in topics
    )


def format_growth_topics(topics):
    if not topics:
        return "- No growth data yet."

    return "\n".join(
        f"- {item['topic']}: {item['growth_rate']:.2f}%"
        for item in topics
    )


def format_opportunity_items(items):
    if not items:
        return "- No analyzed opportunities yet."

    lines = []

    for item in items:
        lines.append(
            "- "
            f"{item.get('title', 'Untitled')} "
            f"({item.get('opportunity_score', 0):.2f})"
        )

    return "\n".join(lines)


def format_recommendations(items):
    if not items:
        return "- No recommendations yet."

    return "\n".join(
        f"- {item['topic']}: {item['reason']}"
        for item in items
    )


def generate_weekly_brief():
    articles = load_articles(json_file)
    top_trends = get_top_topics(limit=10)
    fastest_growing = get_fastest_growing_topics(limit=10)
    topic_opportunities = get_topic_opportunities(articles)
    top_opportunities = get_top_opportunities(articles, limit=10)
    recommendations = generate_recommendations(
        topic_opportunities,
        top_trends
    )

    brief = f"""# Weekly Intelligence Brief

## Top Trends

{format_topic_counts(top_trends)}

## Fastest Growing Topics

{format_growth_topics(fastest_growing)}

## Top Opportunities

{format_opportunity_items(top_opportunities)}

## Build Recommendations

{format_recommendations(recommendations["build"])}

## Learn Recommendations

{format_recommendations(recommendations["learn"])}

## Monitor Recommendations

{format_recommendations(recommendations["monitor"])}
"""

    brief_file.parent.mkdir(parents=True, exist_ok=True)
    brief_file.write_text(brief, encoding="utf-8")

    return brief


if __name__ == "__main__":
    print(generate_weekly_brief())
    print(f"\nSaved weekly brief to {brief_file}")
