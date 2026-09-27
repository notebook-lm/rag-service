"""Qwen3 embedding environment configuration."""

import os

QWEN3_EMBEDDING_BASE_URL = os.getenv(
    "QWEN3_EMBEDDING_BASE_URL", "http://embedding:11434/v1"
)
QWEN3_EMBEDDING_MODEL = os.getenv("QWEN3_EMBEDDING_MODEL", "qwen3-embedding:0.6b")
QWEN3_EMBEDDING_DIMENSIONS = int(os.getenv("QWEN3_EMBEDDING_DIMENSIONS", "1024"))
QWEN3_EMBEDDING_QUERY_INSTRUCTION = (
    "Given a web search query, retrieve relevant passages that answer the query"
)
