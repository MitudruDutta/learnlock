"""Content extraction tools with unified dispatch."""

from urllib.parse import urlparse

from .article import extract_article
from .base import ContentExtractor
from .github import extract_github
from .pdf import extract_pdf
from .youtube import extract_youtube

_YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
}


def extract_content(source: str) -> dict:
    """Extract content using the appropriate tool.

    Supports: YouTube, GitHub, PDF (local or URL), and web articles.
    Returns {"error": str} if no extractor matches.
    """
    # YouTube
    hostname = (urlparse(source).hostname or "").lower().rstrip(".")
    if hostname in _YOUTUBE_HOSTS:
        return extract_youtube(source)

    # GitHub
    if "github.com" in hostname:
        return extract_github(source)

    # PDF (URL or local file)
    lowered = source.lower()
    if lowered.endswith(".pdf") or "/pdf/" in lowered:
        return extract_pdf(source)

    # Web article (any other URL)
    if source.startswith(("http://", "https://")):
        return extract_article(source)

    return {"error": f"Unsupported source: {source}"}


__all__ = [
    "ContentExtractor",
    "extract_content",
    "extract_youtube",
    "extract_article",
    "extract_pdf",
    "extract_github",
]
