"""Unit tests for user ID propagation across RAG Kafka event models."""

import json
import unittest

from messaging.events.document_parsed import DocumentParsedData, DocumentParsedEvent
from messaging.events.document_parsed_failed import (
    DocumentParsedFailedData,
    DocumentParsedFailedEvent,
)
from messaging.events.document_processed import DocumentProcessedData, DocumentProcessedEvent
from messaging.events.document_processed_failed import (
    DocumentProcessedFailedData,
    DocumentProcessedFailedEvent,
)
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

        self.assertEqual(json.loads(event.toJson())["data"]["userId"], "user-1")

    def test_parsed_event_serializes_content(self) -> None:
        event = DocumentParsedEvent(
            data=DocumentParsedData("document-1", "project-1", "user-1", "Extracted notes"),
            event_id="event-1",
            occurred_at="2026-09-28T00:00:00Z",
        )

        payload = json.loads(event.toJson())

        self.assertEqual(payload["eventType"], "document.parsed")
        self.assertEqual(payload["data"]["content"], "Extracted notes")

    def test_parsed_failed_event_serializes_error_details(self) -> None:
        event = DocumentParsedFailedEvent(
            data=DocumentParsedFailedData(
                "document-1", "project-1", "user-1", "PdfStreamError", "Invalid PDF"
            ),
            event_id="event-1",
            occurred_at="2026-09-28T00:00:00Z",
        )

        payload = json.loads(event.toJson())

        self.assertEqual(payload["eventType"], "document.parsed.failed")
        self.assertEqual(payload["data"]["errorCode"], "PdfStreamError")

    def test_processing_event_has_no_status(self) -> None:
        event = DocumentProcessingEvent(
            data=DocumentProcessingData("document-1", "project-1", "user-1"),
            event_id="event-1",
            event_type="document.processing",
            occurred_at="2026-09-28T00:00:00Z",
        )

        payload = json.loads(event.toJson())

        self.assertEqual(payload["data"]["userId"], "user-1")
        self.assertNotIn("status", payload["data"])

    def test_processed_event_serializes_chunk_count(self) -> None:
        event = DocumentProcessedEvent(
            data=DocumentProcessedData("document-1", "project-1", "user-1", 3),
            event_id="event-1",
            event_type="document.processed",
            occurred_at="2026-09-28T00:00:00Z",
        )

        self.assertEqual(json.loads(event.toJson())["data"]["chunkCount"], 3)

    def test_processed_failed_event_serializes_error_details(self) -> None:
        event = DocumentProcessedFailedEvent(
            data=DocumentProcessedFailedData(
                "document-1", "project-1", "user-1", "ConnectionError", "Vector store unavailable"
            ),
            event_id="event-1",
            occurred_at="2026-09-28T00:00:00Z",
        )

        payload = json.loads(event.toJson())

        self.assertEqual(payload["eventType"], "document.processed.failed")
        self.assertEqual(payload["data"]["userId"], "user-1")


if __name__ == "__main__":
    unittest.main()
