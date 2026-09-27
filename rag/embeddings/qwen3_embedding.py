"""Qwen3 embedding implementation through an OpenAI-compatible endpoint."""

from collections.abc import Sequence

from openai import OpenAI

from rag.embeddings.embedding import Embedding
from rag.embeddings.qwen3_embedding_config import Qwen3EmbeddingConfig


class Qwen3Embedding(Embedding):
    """Generate Qwen3 embeddings through an OpenAI-compatible API."""

    def __init__(self, config: Qwen3EmbeddingConfig) -> None:
        self.config = config
        self.client = OpenAI(base_url=config.base_url, api_key="tei")

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.config.model,
            input=list(texts),
        )
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.config.model,
            input=f"Instruct: {self.config.query_instruction}\nQuery: {text}",
        )
        return response.data[0].embedding
