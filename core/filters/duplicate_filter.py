from urllib.parse import urlparse


def normalize_url(url):
    parsed = urlparse(url)

    return (
        f"{parsed.scheme.lower()}://"
        f"{parsed.netloc.lower()}"
        f"{parsed.path}"
    )


def build_url_index(items):
    urls = set()

    for item in items or []:
        url = item.get("url") or item.get("link")

        if url:
            urls.add(normalize_url(url))

    return urls


def is_duplicate(url, existing_urls):
    if not url:
        return False

    return normalize_url(url) in existing_urls


