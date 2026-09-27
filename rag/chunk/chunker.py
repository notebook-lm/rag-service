"""Abstract text chunking contract."""

from abc import ABC, abstractmethod
from typing import Any

from rag.document import RagDocument


class Chunker(ABC):
    """Split parsed text into RAG documents."""

    @abstractmethod
    def chunk(self, text: str, metadata: dict[str, Any] | None = None) -> list[RagDocument]:
        """Split text while carrying document metadata into each chunk."""
