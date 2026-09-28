"""LangChain-backed RAG implementation."""

import asyncio
from collections.abc import Sequence

from langchain_core.documents import Document
from langchain_postgres import PGVector

from rag.document import RagDocument
from rag.embeddings.embedding import Embedding
from rag.rag import Rag
from rag.rag_config import RagConfig


class LangChainRag(Rag):
    """RAG implementation backed by LangChain PGVector."""

    def __init__(self, config: RagConfig, embedding: Embedding) -> None:
        self.config = config
        self.embedding = embedding
        self.vector_store = PGVector(
            embeddings=embedding,
            connection=config.connection,
            collection_name=config.collection_name,
            use_jsonb=True,
        )

    def add_document(self, document: RagDocument) -> list[str]:
        return self.add_documents([document])

    def add_documents(self, documents: Sequence[RagDocument]) -> list[str]:
        return self.vector_store.add_documents(
            [Document(page_content=document.content, metadata=document.metadata) for document in documents]
        )

    def search(
        self,
        query: str,
        filters: dict[str, object],
        limit: int = 5,
    ) -> list[RagDocument]:
        metadata_filter = dict(filters)
        return [
            RagDocument(content=document.page_content, metadata=document.metadata)
            for document in self.vector_store.similarity_search(
                query,
                k=limit,
                filter=metadata_filter,
            )
        ]

    async def search_async(
        self,
        query: str,
        filters: dict[str, object],
        limit: int = 5,
    ) -> list[RagDocument]:
        """Run the blocking PGVector search outside the caller's event loop."""
        return await asyncio.to_thread(self.search, query, filters, limit)
