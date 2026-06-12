import json
from collections import Counter
from datetime import date
from pathlib import Path

from engines import trend_engine
from engines import signal_strength
from engines import opportunity_engine
from engines import recommendation_engine

from utils import load_articles
from stats.stats_manager import get_stats

PROJECT_ROOT = Path(__file__).resolve().parent

json_file = PROJECT_ROOT / "articles.json"

reports_dir = PROJECT_ROOT / "reports"

daily_reports_dir = reports_dir / "daily"


def ensure_report_directories():

    daily_reports_dir.mkdir(
        parents=True,
        exist_ok=True,
    )


def get_report_paths():

    today = date.today().isoformat()

    return (
        daily_reports_dir / f"{today}_report.md",
        daily_reports_dir / f"{today}_report.json",
    )


def get_source_counts(articles):

    counts = Counter()

    for article in articles:

        source_type = article.get(
            "source_type",
            "Unknown",
        )

        counts[source_type] += 1

    return dict(counts)


def format_top_trends(trends):

    if not trends:
        return "- No trends found."

    lines = []

    for trend in trends:

        lines.append(
            f"{trend.get('rank', '-')}. "
            f"{trend['topic']} | "
            f"Trend Score: {trend['trend_score']} | "
            f"Mentions: {trend['mentions']} | "
            f"Level: {trend['trend_level']} | "
            f"Confidence: {trend['confidence']}"
        )

    return "\n".join(lines)


def format_top_signals(signals):

    if not signals:
        return "- No signals found."

    lines = []

    for signal in signals:

        lines.append(
            f"{signal['topic']} | "
            f"Signal Strength: {signal['signal_strength']} | "
            f"Level: {signal['signal_level']} | "
            f"Sources: {signal['source_count']} | "
            f"Confidence: {signal['confidence']}"
        )

    return "\n".join(lines)


def format_top_opportunities(opportunities):

    if not opportunities:
        return "- No opportunities found."

    lines = []

    for item in opportunities:

        lines.append(
            f"{item.get('rank', '-')}. "
            f"{item['topic']} | "
            f"Opportunity Score: "
            f"{item['opportunity_score']} | "
            f"Level: {item['opportunity_level']} | "
            f"Confidence: {item['confidence']}"
        )

    return "\n".join(lines)


def format_recommendations(items):

    if not items:
        return "- None"

    lines = []

    for item in items:

        lines.append(
            f"- {item['topic']} " f"({item['recommendation']}) " f"- {item['reason']}"
        )

    return "\n".join(lines)


def build_report_data():

    articles = load_articles(json_file)

    analyzed_articles = [article for article in articles if article.get("analysis")]

    trends = trend_engine.analyze_trends(articles)

    signals = signal_strength.analyze_signal_strength(
        articles,
        trends,
    )

    accelerations = [
        {
            "topic": trend["topic"],
            "acceleration_score": 0,
        }
        for trend in trends
    ]

    opportunities = opportunity_engine.analyze_opportunities(
        trends,
        signals,
        accelerations,
    )

    recommendations = recommendation_engine.generate_recommendations(opportunities)

    return {
        "generated_at": date.today().isoformat(),
        "overview": {
            "total_articles": len(articles),
            "analyzed_articles": len(analyzed_articles),
            "source_counts": get_source_counts(articles),
        },
        "collection_funnel": get_stats(),
        "top_trends": trends[:10],
        "top_signals": signals[:10],
        "top_opportunities": opportunities[:10],
        "recommendations": recommendations,
    }


def build_markdown_report(report_data):

    source_counts = report_data["overview"]["source_counts"]

    source_lines = "\n".join([f"- {k}: {v}" for k, v in source_counts.items()])

    return f"""
# TREND INTELLIGENCE REPORT

Generated: {report_data["generated_at"]}

## Overview

- Total Articles:
  {report_data["overview"]["total_articles"]}

- Analyzed Articles:
  {report_data["overview"]["analyzed_articles"]}

### Source Counts

{source_lines}

## Top Trends

{format_top_trends(
    report_data["top_trends"]
)}

## Top Signals

{format_top_signals(
    report_data["top_signals"]
)}

## Top Opportunities

{format_top_opportunities(
    report_data["top_opportunities"]
)}

## Build Recommendations

{format_recommendations(
    report_data["recommendations"]["build"]
)}

## Learn Recommendations

{format_recommendations(
    report_data["recommendations"]["learn"]
)}

## Monitor Recommendations

{format_recommendations(
    report_data["recommendations"]["monitor"]
)}
"""


def write_report_files(report_data):

    ensure_report_directories()

    markdown_path, json_path = get_report_paths()

    markdown_path.write_text(
        build_markdown_report(report_data),
        encoding="utf-8",
    )

    json_path.write_text(
        json.dumps(
            report_data,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return (
        markdown_path,
        json_path,
    )


def generate_report():

    report_data = build_report_data()

    markdown_path, json_path = write_report_files(report_data)

    print(f"Markdown report: " f"{markdown_path}")

    print(f"JSON report: " f"{json_path}")


if __name__ == "__main__":
    generate_report()
