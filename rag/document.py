"""Library-independent RAG document model."""

from typing import Any


class RagDocument:
    """A text unit stored and returned by a RAG implementation."""

    def __init__(self, content: str, metadata: dict[str, Any] | None = None) -> None:
        self.content = content
        self.metadata = metadata or {}
