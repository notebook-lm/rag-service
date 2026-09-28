"""Abstract embedding contract."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from langchain_core.embeddings import Embeddings


class Embedding(Embeddings, ABC):
    """Generate vectors for document text and retrieval queries."""

    @abstractmethod
    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed document text in input order."""

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Embed one query for retrieval."""

    @abstractmethod
    async def aembed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        """Asynchronously embed document text in input order."""

    @abstractmethod
    async def aembed_query(self, text: str) -> list[float]:
        """Asynchronously embed one query for retrieval."""
