from pathlib import Path
import sys


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[4]
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from reporter import build_report_data, format_recommendations


brief_file = Path(__file__).resolve().parent / "weekly_brief_output.md"


def format_topic_counts(topics):
    if not topics:
        return "- No data yet."

    return "\n".join(
        f"- {item['topic']}: {item.get('mentions', item.get('source_count', 0))}"
        for item in topics
    )


def format_opportunity_items(items):
    if not items:
        return "- No analyzed opportunities yet."

    lines = []

    for item in items:
        lines.append(
            "- "
            f"{item.get('topic', item.get('title', 'Untitled'))} "
            f"({item.get('opportunity_score', 0):.2f})"
        )

    return "\n".join(lines)


def generate_weekly_brief():
    report_data = build_report_data()
    recommendations = report_data["recommendations"]

    brief = f"""# Weekly Intelligence Brief

## Top Trends

{format_topic_counts(report_data["top_trends"])}

## Top Opportunities

{format_opportunity_items(report_data["top_opportunities"])}

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
