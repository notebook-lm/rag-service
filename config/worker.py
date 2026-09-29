"""Bounded worker settings for Kafka-driven RAG document processing."""

import os

RAG_WORKER_CONCURRENCY = int(os.getenv("RAG_WORKER_CONCURRENCY", "2"))
RAG_MAX_IN_FLIGHT = int(os.getenv("RAG_MAX_IN_FLIGHT", "4"))

if RAG_WORKER_CONCURRENCY < 1:
    raise ValueError("RAG_WORKER_CONCURRENCY must be at least 1")

if RAG_MAX_IN_FLIGHT < RAG_WORKER_CONCURRENCY:
    raise ValueError("RAG_MAX_IN_FLIGHT must be at least RAG_WORKER_CONCURRENCY")
