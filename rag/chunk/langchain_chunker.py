"""LangChain recursive-character chunking implementation."""

from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.chunk.chunk_config import ChunkConfig
from rag.chunk.chunker import Chunker
from rag.document import RagDocument


class LangChainChunker(Chunker):
    """Split text with LangChain while exposing local RAG document models."""

    def __init__(self, config: ChunkConfig) -> None:
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
        )

    def chunk(self, text: str, metadata: dict[str, Any] | None = None) -> list[RagDocument]:
        documents = self.text_splitter.create_documents([text], metadatas=[metadata or {}])
        return [
            RagDocument(
                content=document.page_content,
                metadata={**document.metadata, "chunk_index": index},
            )
            for index, document in enumerate(documents)
        ]
