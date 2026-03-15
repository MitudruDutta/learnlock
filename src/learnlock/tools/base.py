"""Content extractor protocol — the interface every source plugin implements."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ContentExtractor(Protocol):
    """Protocol for content extraction plugins.

    Every extractor must:
    - Declare which URL/path patterns it handles via `can_handle`
    - Return a consistent dict shape from `extract`
    """

    name: str

    def can_handle(self, source: str) -> bool:
        """Return True if this extractor can process the given URL or path."""
        ...

    def extract(self, source: str) -> dict:
        """Extract content from source.

        Returns on success:
            {"title": str, "content": str, "url": str, "source_type": str}
            May include extra keys like "segments" for YouTube.

        Returns on failure:
            {"error": str}
        """
        ...
