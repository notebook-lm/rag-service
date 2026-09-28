"""Unit tests for user ID propagation across RAG Kafka event models."""

import json
import unittest

from messaging.events.document_processed import DocumentProcessedData, DocumentProcessedEvent
from messaging.events.document_processing import DocumentProcessingData, DocumentProcessingEvent
from messaging.events.document_uploaded import DocumentUploadedData, DocumentUploadedEvent


class DocumentEventUserIdTests(unittest.TestCase):
    def test_uploaded_event_serializes_user_id(self) -> None:
        event = DocumentUploadedEvent(
            data=DocumentUploadedData(
                object_key="projects/project-1/documents/document-1",
                project_id="project-1",
                user_id="user-1",
                size_bytes=42,
                document_id="document-1",
                content_type="text/plain",
                original_filename="notes.txt",
            ),
            event_id="event-1",
            event_type="document.uploaded",
            occurred_at="2026-09-28T00:00:00Z",
        )

        payload = json.loads(event.toJson())

        self.assertEqual(payload["data"]["userId"], "user-1")

    def test_processing_event_serializes_user_id(self) -> None:
        event = DocumentProcessingEvent(
            data=DocumentProcessingData(
                document_id="document-1",
                project_id="project-1",
                user_id="user-1",
                status="PROCESSING",
            ),
            event_id="event-1",
            event_type="document.processing",
            occurred_at="2026-09-28T00:00:00Z",
        )

        payload = json.loads(event.toJson())

        self.assertEqual(payload["data"]["userId"], "user-1")

    def test_processed_event_serializes_user_id(self) -> None:
        event = DocumentProcessedEvent(
            data=DocumentProcessedData(
                document_id="document-1",
                project_id="project-1",
                user_id="user-1",
                chunk_count=3,
            ),
            event_id="event-1",
            event_type="document.processed",
            occurred_at="2026-09-28T00:00:00Z",
        )

        payload = json.loads(event.toJson())

        self.assertEqual(payload["data"]["userId"], "user-1")


if __name__ == "__main__":
    unittest.main()
