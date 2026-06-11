import sys
from collections import Counter
from pathlib import Path

import streamlit as st


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engines.opportunity_engine import (
    get_topic_opportunities,
    get_top_opportunities,
)
from engines.recommendation_engine import generate_recommendations
from engines.trend_engine import get_top_topics
from utils import load_articles


json_file = PROJECT_ROOT / "articles.json"


@st.cache_data
def load_dashboard_articles():
    return load_articles(json_file)


def get_source_type(article):
    return article.get("source_type") or ("rss" if article.get("source") else "unknown")


def render_overview(articles):
    analyzed = [
        article for article in articles
        if isinstance(article.get("analysis"), dict)
    ]
    with_filter_data = [
        article for article in articles
        if article.get("filter_data")
    ]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items", len(articles))
    col2.metric("Analyzed Items", len(analyzed))
    col3.metric("With Filter Data", len(with_filter_data))


def render_trends():
    st.subheader("Top Trends")
    st.dataframe(get_top_topics(limit=25), use_container_width=True)


def render_opportunities(articles):
    st.subheader("Topic Opportunities")
    st.dataframe(
        get_topic_opportunities(articles)[:25],
        use_container_width=True
    )

    st.subheader("Top Opportunity Items")
    rows = [
        {
            "title": item.get("title"),
            "source_type": get_source_type(item),
            "opportunity_score": item.get("opportunity_score"),
        }
        for item in get_top_opportunities(articles, limit=25)
    ]
    st.dataframe(rows, use_container_width=True)


def render_recommendations(articles):
    topic_opportunities = get_topic_opportunities(articles)
    top_topics = get_top_topics(limit=25)
    recommendations = generate_recommendations(
        topic_opportunities,
        top_topics
    )

    for section in ["build", "learn", "monitor"]:
        st.subheader(section.title())
        st.dataframe(
            recommendations[section],
            use_container_width=True
        )


def render_source_statistics(articles):
    source_counts = Counter(
        get_source_type(article)
        for article in articles
    )
    rows = [
        {
            "source_type": source_type,
            "count": count,
        }
        for source_type, count in source_counts.most_common()
    ]

    st.subheader("Source Statistics")
    st.dataframe(rows, use_container_width=True)


def main():
    st.set_page_config(
        page_title="Trend Intelligence Dashboard",
        layout="wide"
    )
    st.title("Trend Intelligence Dashboard")

    articles = load_dashboard_articles()
    page = st.sidebar.radio(
        "Page",
        [
            "Overview",
            "Trends",
            "Opportunities",
            "Recommendations",
            "Source Statistics",
        ]
    )

    if page == "Overview":
        render_overview(articles)
    elif page == "Trends":
        render_trends()
    elif page == "Opportunities":
        render_opportunities(articles)
    elif page == "Recommendations":
        render_recommendations(articles)
    elif page == "Source Statistics":
        render_source_statistics(articles)


if __name__ == "__main__":
    main()
