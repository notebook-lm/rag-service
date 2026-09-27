"""RAG vector-store environment configuration."""

import os

RAG_DATABASE_URL = os.getenv(
    "RAG_DATABASE_URL", "postgresql://rag_service:rag_service@postgres:5432/rag_service"
)
RAG_COLLECTION_NAME = os.getenv("RAG_COLLECTION_NAME", "rag_documents")
