"""Qwen3 embedding environment configuration."""

import os

QWEN3_EMBEDDING_BASE_URL = os.getenv("QWEN3_EMBEDDING_BASE_URL", "http://embedding:80/v1")
QWEN3_EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"
QWEN3_EMBEDDING_DIMENSIONS = int(os.getenv("QWEN3_EMBEDDING_DIMENSIONS", "1024"))
QWEN3_EMBEDDING_QUERY_INSTRUCTION = (
    "Given a web search query, retrieve relevant passages that answer the query"
)
