import json
from collections import Counter
from datetime import date
from pathlib import Path

from engines import trend_engine
from engines import signal_strength
from engines import trend_acceleration
from engines import opportunity_engine
from engines import recommendation_engine

PROJECT_ROOT = Path(__file__).resolve().parent
json_file = PROJECT_ROOT / "articles.json"
reports_dir = PROJECT_ROOT / "reports"
daily_reports_dir = reports_dir / "daily"
weekly_reports_dir = reports_dir / "weekly"
monthly_reports_dir = reports_dir / "monthly"

# Keep engine reads aligned with the reporter's project database path.
trend_engine.json_file = json_file
opportunity_engine.json_file = json_file


def ensure_report_directories():
    for directory in [
        daily_reports_dir,
        weekly_reports_dir,
        monthly_reports_dir,
    ]:
        directory.mkdir(parents=True, exist_ok=True)


def get_report_paths():
    today = date.today().isoformat()

    return (
        daily_reports_dir / f"{today}_report.md",
        daily_reports_dir / f"{today}_report.json",
    )


def get_source_type(article):
    if article.get("source_type"):
        return article.get("source_type")

    if article.get("source"):
        return "rss"

    return "unknown"


def get_analyzed_items(articles):
    return [
        article for article in articles if isinstance(article.get("analysis"), dict)
    ]


def get_filter_data_items(articles):
    return [article for article in articles if article.get("filter_data")]


def get_source_counts(articles):
    source_counts = Counter()

    for article in articles:
        source_counts[get_source_type(article)] += 1

    return dict(source_counts.most_common())


def format_score(score):
    if isinstance(score, float):
        return f"{score:.2f}"

    return str(score)


def get_score_detail(analysis, field_name):
    detail = analysis.get(field_name) or {}

    return {
        "score": detail.get("score", 0) or 0,
        "reason": detail.get("reason", ""),
    }


def build_item_intelligence(article):
    analysis = article.get("analysis") or {}

    if not isinstance(analysis, dict):
        return {}

    return {
        "overview": analysis.get("overview", ""),
        "classification": analysis.get("classification") or {},
        "top_interests": analysis.get("top_interests") or [],
        "top_goals": analysis.get("top_goals") or [],
        "novelty": get_score_detail(analysis, "novelty"),
        "actionability": get_score_detail(analysis, "actionability"),
        "learning_value": get_score_detail(analysis, "learning_value"),
        "monetization_potential": get_score_detail(analysis, "monetization_potential"),
        "required_cost": get_score_detail(analysis, "required_cost"),
        "key_points": analysis.get("key_points") or [],
        "why_it_matters": analysis.get("why_it_matters", ""),
    }


def build_report_data():
    from utils import load_articles
    from stats.stats_manager import get_stats
    articles = load_articles(json_file)

    analyzed_items = get_analyzed_items(articles)

    filter_data_items = get_filter_data_items(articles)

    source_counts = get_source_counts(articles)

    total_items = len(articles)

    analyzed_count = len(analyzed_items)

    coverage = (analyzed_count / total_items) * 100 if total_items else 0

    # =====================================
    # Engines
    # =====================================

    trends = trend_engine.analyze_trends(articles)

    signals = signal_strength.analyze_signal_strength(
        articles,
        trends,
    )

    # No historical snapshots yet

    accelerations = []

    for trend in trends:

        accelerations.append(
            {
                "domain": trend["domain"],
                "theme": trend["theme"],
                "topic": trend["topic"],
                "acceleration_score": 0,
            }
        )

    opportunities = opportunity_engine.analyze_opportunities(
        trends,
        signals,
        accelerations,
    )

    recommendations = recommendation_engine.generate_recommendations(opportunities)

    # Filter analyzed items that are relevant to top opportunities
    top_opportunity_topics = [o["topic"] for o in opportunities[:10]]
    top_opportunity_items = []
    for item in analyzed_items:
        item_topics = item.get("filter_data", {}).get("matched_topics", [])
        if any(topic in top_opportunity_topics for topic in item_topics):
            # Attach opportunity score for the primary topic
            main_topic = next((t for t in item_topics if t in top_opportunity_topics), None)
            opp = next((o for o in opportunities if o["topic"] == main_topic), None)
            item["opportunity_score"] = opp["opportunity_score"] if opp else 0
            top_opportunity_items.append(item)

    top_opportunity_items = sorted(top_opportunity_items, key=lambda x: x.get("opportunity_score", 0), reverse=True)[:10]

    return {
        "header": "TREND INTELLIGENCE REPORT",
        "generated_at": date.today().isoformat(),
        "overview": {
            "total_items": total_items,
            "analyzed_items": analyzed_count,
            "items_with_filter_data": len(filter_data_items),
            "source_counts": source_counts,
        },
        "collection_funnel": get_stats(),
        "top_trends": trends[:10],
        "top_signals": signals[:10],
        "top_opportunity_topics": opportunities[:10],
        "top_opportunity_items": top_opportunity_items,
        "recommendations": recommendations,
        "system_health": {
            "collected_items": total_items,
            "analyzed_items": analyzed_count,
            "coverage_percent": round(
                coverage,
                2,
            ),
        },
    }


def markdown_list(items, empty_message):
    if not items:
        return f"- {empty_message}"

    return "\n".join(items)


def format_top_trends(topics):
    return markdown_list(
        [
            f"{index}. {item['topic']} - {item.get('mentions', 0)} mentions (Score: {item.get('trend_score', 0)})"
            for index, item in enumerate(topics, start=1)
        ],
        "No topics found.",
    )


def format_topic_scores(topics):
    return markdown_list(
        [
            f"{index}. {item['topic']} - {format_score(item.get('opportunity_score', 0))}"
            for index, item in enumerate(topics, start=1)
        ],
        "No opportunity topics found.",
    )


def format_opportunity_items(items):
    if not items:
        return "- No analyzed opportunity items found."

    lines = []

    for index, item in enumerate(items, start=1):
        analysis = item.get("analysis") or {}
        key_points = analysis.get("key_points") or []

        lines.append(
            f"{index}. {item['title']}\n"
            f"   - Source Type: {item['source_type']}\n"
            f"   - Opportunity Score: "
            f"{format_score(item.get('opportunity_score', 0))}\n"
            f"   - URL: {item.get('url') or 'No URL'}"
        )

        if analysis.get("summary"):
            lines.append(f"   - Summary: {analysis['summary']}")

        importance = analysis.get("importance") or {}
        if importance.get("reason"):
            lines.append(f"   - Importance Reason: {importance['reason']}")

        if key_points:
            lines.append("   - Key Points:")
            lines.extend(f"     - {point}" for point in key_points)

    return "\n".join(lines)


def format_recommendations(recommendations):
    if not recommendations:
        return "- No recommendations found."

    lines = []

    for index, item in enumerate(recommendations, start=1):
        lines.append(
            f"{index}. {item['topic']}\n"
            f"   - Recommendation: {item['recommendation']}\n"
            f"   - Reason: {item['reason']}"
        )

    return "\n".join(lines)


def format_collection_funnel(collection_funnel):
    if not collection_funnel:
        return "- No collection statistics found."

    lines = [
        "| Source | Seen | Duplicates Removed | Quality Removed | "
        "Irrelevant Removed | Stored |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    for source, stats in sorted(collection_funnel.items()):
        lines.append(
            f"| {source} "
            f"| {stats.get('seen', 0)} "
            f"| {stats.get('duplicates_removed', 0)} "
            f"| {stats.get('quality_removed', 0)} "
            f"| {stats.get('irrelevant_removed', 0)} "
            f"| {stats.get('stored', 0)} |"
        )

    return "\n".join(lines)


def build_markdown_report(report_data):
    overview = report_data["overview"]
    source_counts = overview["source_counts"]
    source_count_lines = (
        "\n".join(
            f"- {source_type}: {count}" for source_type, count in source_counts.items()
        )
        if source_counts
        else "- none: 0"
    )

    return f"""# {report_data["header"]}

Generated: {report_data["generated_at"]}

## Overview

- Total Items: {overview["total_items"]}
- Analyzed Items: {overview["analyzed_items"]}
- Items With Filter Data: {overview["items_with_filter_data"]}

### Source Counts

{source_count_lines}

## Collection Funnel

{format_collection_funnel(report_data["collection_funnel"])}

## Top Trends

{format_top_trends(report_data["top_trends"])}

## Top Opportunity Topics

{format_topic_scores(report_data["top_opportunity_topics"])}

## Top Opportunity Items

{format_opportunity_items(report_data["top_opportunity_items"])}

## Build Recommendations

{format_recommendations(report_data["recommendations"]["build"])}

## Learn Recommendations

{format_recommendations(report_data["recommendations"]["learn"])}

## Monitor Recommendations

{format_recommendations(report_data["recommendations"]["monitor"])}

## System Health

- Collected Items: {report_data["system_health"]["collected_items"]}
- Analyzed Items: {report_data["system_health"]["analyzed_items"]}
- Coverage %: {report_data["system_health"]["coverage_percent"]:.2f}
"""


def write_report_files(report_data):
    ensure_report_directories()
    markdown_path, json_path = get_report_paths()

    markdown_path.write_text(build_markdown_report(report_data), encoding="utf-8")
    json_path.write_text(
        json.dumps(report_data, indent=4, ensure_ascii=False), encoding="utf-8"
    )

    return markdown_path, json_path


def generate_report():
    report_data = build_report_data()
    markdown_path, json_path = write_report_files(report_data)

    print("Report generated")
    print(f"Markdown file: {markdown_path}")
    print(f"JSON file: {json_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(generate_report())
