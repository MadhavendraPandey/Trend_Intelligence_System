EXTRACTION_FAILURE_MESSAGES = [
    "extraction failed",
    "no content extracted",
    "content extraction failed",
    "failed to extract",
]

BLOCKED_PAGE_PATTERNS = [
    "404",
    "403 forbidden",
    "page not found",
    "access denied",
    "enable javascript",
    "verification required",
    "cloudflare",
    "under construction",
    "coming soon",
]


def is_extraction_failure(content):

    normalized_content = (
        content or ""
    ).strip().lower()

    if not normalized_content:
        return True

    return any(
        message in normalized_content
        for message in
        EXTRACTION_FAILURE_MESSAGES
    )


def contains_blocked_pattern(content):

    normalized_content = (
        content or ""
    ).strip().lower()

    return any(
        pattern in normalized_content
        for pattern in
        BLOCKED_PAGE_PATTERNS
    )


def is_high_quality(content):

    if is_extraction_failure(content):
        return False

    if contains_blocked_pattern(content):
        return False

    return True