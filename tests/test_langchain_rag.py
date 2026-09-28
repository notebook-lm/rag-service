"""Unit tests for PGVector metadata-filtered retrieval."""

import unittest

from langchain_core.documents import Document

from rag.langchain_rag import LangChainRag


class VectorStoreSpy:
    """Captures similarity-search arguments without a database connection."""

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def similarity_search(self, query: str, **kwargs: object) -> list[Document]:
        self.calls.append({"query": query, **kwargs})
        return [Document(page_content="matching chunk", metadata={"chunk_index": 3})]


class LangChainRagSearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rag = LangChainRag.__new__(LangChainRag)
        self.rag.vector_store = VectorStoreSpy()

    def test_search_forwards_project_filter(self) -> None:
        filters = {"project_id": "project-1"}
        documents = self.rag.search("question", filters, limit=7)

        self.assertEqual(
            self.rag.vector_store.calls,
            [{"query": "question", "k": 7, "filter": {"project_id": "project-1"}}],
        )
        self.assertEqual(filters, {"project_id": "project-1"})
        self.assertEqual(documents[0].content, "matching chunk")
        self.assertEqual(documents[0].metadata, {"chunk_index": 3})

    def test_search_forwards_project_and_document_ids_filter(self) -> None:
        self.rag.search(
            "question",
            {
                "project_id": "project-1",
                "document_id": {"$in": ["document-42", "document-43"]},
            },
        )

        self.assertEqual(
            self.rag.vector_store.calls,
            [
                {
                    "query": "question",
                    "k": 5,
                    "filter": {
                        "project_id": "project-1",
                        "document_id": {"$in": ["document-42", "document-43"]},
                    },
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
