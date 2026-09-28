"""Unit tests for gRPC context retrieval."""

import asyncio
import unittest

from rag.document import RagDocument
from rpc.generated import retrieval_pb2
from rpc.services.retrieval_service import RetrievalService


class RagSpy:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def search_async(
        self,
        query: str,
        filters: dict[str, object],
        limit: int = 5,
    ) -> list[RagDocument]:
        self.calls.append({"query": query, "filters": filters, "limit": limit})
        return [
            RagDocument(
                "A relevant chunk.",
                {"document_id": "document-1", "filename": "brief.pdf", "chunk_index": 2},
            ),
            RagDocument(
                "Another relevant chunk.",
                {"document_id": "document-2", "filename": "notes.txt", "chunk_index": 4},
            ),
        ]


class DelayedRagSpy(RagSpy):
    async def search_async(
        self,
        query: str,
        filters: dict[str, object],
        limit: int = 5,
    ) -> list[RagDocument]:
        await asyncio.sleep(0.05)
        return await super().search_async(query, filters, limit)


class RetrievalServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_retrieve_context_scopes_search_and_maps_chunks(self) -> None:
        rag = RagSpy()
        service = RetrievalService(rag)

        response = await service.RetrieveContext(
            retrieval_pb2.RetrieveContextRequest(
                query=" What are the terms? ",
                project_id=" project-1 ",
                document_ids=["document-1", " document-2 "],
                limit=3,
            ),
            context=None,
        )

        self.assertEqual(
            rag.calls,
            [
                {
                    "query": "What are the terms?",
                    "filters": {
                        "project_id": "project-1",
                        "document_id": {"$in": ["document-1", "document-2"]},
                    },
                    "limit": 3,
                }
            ],
        )
        self.assertEqual(response.chunks[0].document_id, "document-1")
        self.assertEqual(response.chunks[0].filename, "brief.pdf")
        self.assertEqual(response.chunks[0].chunk_index, 2)
        self.assertEqual(
            response.context,
            "A relevant chunk.\n\n---\n\nAnother relevant chunk.",
        )

    async def test_retrieve_context_uses_default_limit(self) -> None:
        rag = RagSpy()
        service = RetrievalService(rag)

        await service.RetrieveContext(
            retrieval_pb2.RetrieveContextRequest(
                query="question",
                project_id="project-1",
                document_ids=["document-1"],
            ),
            context=None,
        )

        self.assertEqual(rag.calls[0]["limit"], 5)

    async def test_retrieve_context_allows_concurrent_awaits(self) -> None:
        rag = DelayedRagSpy()
        service = RetrievalService(rag)
        request = retrieval_pb2.RetrieveContextRequest(
            query="question",
            project_id="project-1",
            document_ids=["document-1"],
        )

        first, second = await asyncio.gather(
            service.RetrieveContext(request, context=None),
            service.RetrieveContext(request, context=None),
        )

        self.assertEqual(len(rag.calls), 2)
        self.assertEqual(first.context, second.context)


if __name__ == "__main__":
    unittest.main()
