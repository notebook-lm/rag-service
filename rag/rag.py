"""Abstract RAG contract."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from rag.document import RagDocument


class Rag(ABC):
    """Document indexing and semantic search operations."""

    @abstractmethod
    def add_document(self, document: RagDocument) -> list[str]:
        """Add one document to the RAG index."""

    @abstractmethod
    def add_documents(self, documents: Sequence[RagDocument]) -> list[str]:
        """Add multiple documents to the RAG index."""

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[RagDocument]:
        """Return documents relevant to a query."""
