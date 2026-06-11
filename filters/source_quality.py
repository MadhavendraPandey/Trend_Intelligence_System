

# ==========================================================
# Domain Trust Scores
# ==========================================================

TRUSTED_DOMAINS = {

    # AI Labs
    "openai.com": 10,
    "anthropic.com": 10,
    "deepmind.google": 10,
    "huggingface.co": 9,

    # Research
    "arxiv.org": 10,

    # Cybersecurity
    "krebsonsecurity.com": 9,
    "bleepingcomputer.com": 8,
    "thehackernews.com": 8,
    "securityweek.com": 8,
    "darkreading.com": 8,
    "schneier.com": 9,

    # Startup / Business
    "ycombinator.com": 9,
    "techcrunch.com": 7,
    "venturebeat.com": 7,
    "saastr.com": 7,

    # Communities
    "github.com": 7,
    "news.ycombinator.com": 6,
    "reddit.com": 5,
}


# ==========================================================
# Source Type Baseline
# ==========================================================

SOURCE_BASELINES = {

    "arxiv": 9,

    "github": 7,

    "rss": 6,

    "hackernews": 6,

    "reddit": 5,
}


# ==========================================================
# Domain Quality
# ==========================================================

def get_domain_score(item):

    metadata = item.get("metadata", {})

    domain = (
        metadata.get("source_domain")
        or ""
    ).lower()

    if not domain:
        return 0

    return TRUSTED_DOMAINS.get(
        domain,
        0
    )


# ==========================================================
# Metadata Completeness
# ==========================================================

def get_metadata_score(item):

    metadata = item.get(
        "metadata",
        {}
    )

    source_type = (
        item.get(
            "source_type",
            ""
        )
        .lower()
    )

    score = 0

    # ------------------
    # RSS
    # ------------------

    if source_type == "rss":

        if metadata.get("author"):
            score += 1

        if metadata.get(
            "source_domain"
        ):
            score += 1

        if metadata.get(
            "published"
        ):
            score += 1

    # ------------------
    # GitHub
    # ------------------

    elif source_type == "github":

        if metadata.get(
            "language"
        ):
            score += 1

        if metadata.get(
            "topics"
        ):
            score += 1

        if metadata.get(
            "created_at"
        ):
            score += 1

        if metadata.get(
            "updated_at"
        ):
            score += 1

    # ------------------
    # Arxiv
    # ------------------

    elif source_type == "arxiv":

        if metadata.get(
            "authors"
        ):
            score += 1

        if metadata.get(
            "primary_category"
        ):
            score += 1

        if metadata.get(
            "published"
        ):
            score += 1

    # ------------------
    # Hacker News
    # ------------------

    elif source_type == "hackernews":

        if metadata.get(
            "author"
        ):
            score += 1

        if metadata.get(
            "created_at"
        ):
            score += 1

        if metadata.get(
            "external_url"
        ):
            score += 1

    # ------------------
    # Reddit
    # ------------------

    elif source_type == "reddit":

        if metadata.get(
            "author"
        ):
            score += 1

        if metadata.get(
            "subreddit"
        ):
            score += 1

        if metadata.get(
            "created_at"
        ):
            score += 1

    return score


# ==========================================================
# Main Source Quality Engine
# ==========================================================

def calculate_source_quality(item):

    source_type = (
        item.get(
            "source_type",
            ""
        )
        .lower()
    )

    baseline = SOURCE_BASELINES.get(
        source_type,
        0
    )

    domain_score = (
        get_domain_score(item)
    )

    metadata_score = (
        get_metadata_score(item)
    )

    total_score = (
        baseline
        + domain_score
        + metadata_score
    )

    return {

        "score":
            total_score,

        "breakdown": {

            "baseline":
                baseline,

            "domain_score":
                domain_score,

            "metadata_score":
                metadata_score,
        }
    }


# ==========================================================
# Attach Score To Item
# ==========================================================

def enrich_source_quality(item):

    result = (
        calculate_source_quality(
            item
        )
    )

    item[
        "source_quality_score"
    ] = result["score"]

    return item