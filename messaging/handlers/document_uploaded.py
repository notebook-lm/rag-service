import json
import logging
from datetime import UTC, datetime
from uuid import uuid4

from confluent_kafka import Message

from database.database import Database
from database.entities.inbox import Inbox
from database.repositories.inbox_repository import InboxRepository
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
from messaging.messaging import Messaging
from rag.chunk.chunker import Chunker
from rag.parsers.document_parser_factory import DocumentParserFactory
from rag.parsers.unsupported_document_type_error import UnsupportedDocumentTypeError
from rag.rag import Rag
from storage.storage import Storage
from storage.storage_object import StorageObject

logger = logging.getLogger(__name__)


class DocumentUploadedHandler:
    def __init__(
        self,
        messaging: Messaging,
        database: Database,
        storage: Storage,
        parser_factory: DocumentParserFactory,
        chunker: Chunker,
        rag: Rag,
    ) -> None:
        self.messaging = messaging
        self.inbox_repository = InboxRepository(database)
        self.database = database
        self.storage = storage
        self.parser_factory = parser_factory
        self.chunker = chunker
        self.rag = rag

    def execute(self, message: Message) -> None:
        payload = message.value()
        document_uploaded_payload = json.loads(payload)
        event_id = document_uploaded_payload["eventId"]

        with self.database.transaction() as cursor:
            if self.inbox_repository.exists(cursor, event_id):
                logger.info("Skipping duplicate document.uploaded event %s", event_id)
                return

            self.inbox_repository.create(
                cursor,
                Inbox(
                    event_id=event_id,
                    event_type=document_uploaded_payload["eventType"],
                    topic=message.topic(),
                    partition=message.partition(),
                    offset=message.offset(),
                    payload=payload,
                ),
            )
            self._process(document_uploaded_payload, message)
            self.inbox_repository.mark_processed(cursor, event_id)

    def _process(self, document_uploaded_payload: dict[str, object], message: Message) -> None:
        document_uploaded_event = self._to_document_uploaded_event(document_uploaded_payload)

        logger.info("Document %s is now processing", document_uploaded_event.data.document_id)
        self._publish_processing(document_uploaded_event, message.key())

        try:
            storage_object = self.storage.get(document_uploaded_event.data.object_key)
            parser = self._get_parser(storage_object)
            text = parser.parse(storage_object.content)
        except Exception as error:
            logger.exception("Document %s parsing failed", document_uploaded_event.data.document_id)
            self._publish_parsed_failed(document_uploaded_event, error, message.key())
            return

        self._publish_parsed(document_uploaded_event, text, message.key())

        try:
            chunks = self.chunker.chunk(
                text,
                {
                    "document_id": document_uploaded_event.data.document_id,
                    "project_id": document_uploaded_event.data.project_id,
                    "user_id": document_uploaded_event.data.user_id,
                    "object_key": document_uploaded_event.data.object_key,
                    "filename": storage_object.metadata.filename,
                    "content_type": storage_object.metadata.content_type,
                    "size_bytes": storage_object.metadata.size_bytes,
                    "etag": storage_object.metadata.etag,
                    "last_modified": storage_object.metadata.last_modified.isoformat()
                    if storage_object.metadata.last_modified
                    else None,
                },
            )
            self.rag.add_documents(chunks)
        except Exception as error:
            logger.exception("Document %s indexing failed", document_uploaded_event.data.document_id)
            self._publish_processed_failed(document_uploaded_event, error, message.key())
            return

        logger.info(
            "Document %s indexed with %s chunks",
            document_uploaded_event.data.document_id,
            len(chunks),
        )
        self._publish_processed(document_uploaded_event, len(chunks), message.key())

    def _to_document_uploaded_event(
        self,
        document_uploaded_payload: dict[str, object],
    ) -> DocumentUploadedEvent:
        document_uploaded_data = document_uploaded_payload["data"]
        if not isinstance(document_uploaded_data, dict):
            raise ValueError("document.uploaded event data must be an object")

        return DocumentUploadedEvent(
            data=DocumentUploadedData(
                object_key=str(document_uploaded_data["objectKey"]),
                project_id=str(document_uploaded_data["projectId"]),
                user_id=str(document_uploaded_data["userId"]),
                size_bytes=int(document_uploaded_data["sizeBytes"]),
                document_id=str(document_uploaded_data["documentId"]),
                content_type=str(document_uploaded_data["contentType"]),
                original_filename=str(document_uploaded_data["originalFilename"]),
            ),
            event_id=str(document_uploaded_payload["eventId"]),
            event_type=str(document_uploaded_payload["eventType"]),
            occurred_at=str(document_uploaded_payload["occurredAt"]),
        )

    def _get_parser(self, storage_object: StorageObject):
        if storage_object.metadata.filename:
            try:
                return self.parser_factory.get_by_filename(storage_object.metadata.filename)
            except UnsupportedDocumentTypeError:
                pass

        if storage_object.metadata.content_type:
            try:
                return self.parser_factory.get_by_content_type(storage_object.metadata.content_type)
            except UnsupportedDocumentTypeError:
                pass

        raise UnsupportedDocumentTypeError("Unknown document type")

    def _event_context(self) -> tuple[str, str]:
        return str(uuid4()), datetime.now(UTC).isoformat()

    def _publish_parsed(
        self,
        event: DocumentUploadedEvent,
        content: str,
        key: bytes | str | None,
    ) -> None:
        event_id, occurred_at = self._event_context()
        parsed_event = DocumentParsedEvent(
            data=DocumentParsedData(
                document_id=event.data.document_id,
                project_id=event.data.project_id,
                user_id=event.data.user_id,
                content=content,
            ),
            event_id=event_id,
            occurred_at=occurred_at,
        )
        self.messaging.pub("document.parsed", parsed_event.toJson(), key)

    def _publish_parsed_failed(
        self,
        event: DocumentUploadedEvent,
        error: Exception,
        key: bytes | str | None,
    ) -> None:
        event_id, occurred_at = self._event_context()
        failed_event = DocumentParsedFailedEvent(
            data=DocumentParsedFailedData(
                document_id=event.data.document_id,
                project_id=event.data.project_id,
                user_id=event.data.user_id,
                error_code=type(error).__name__,
                error_message=str(error)[:500],
            ),
            event_id=event_id,
            occurred_at=occurred_at,
        )
        self.messaging.pub("document.parsed.failed", failed_event.toJson(), key)

    def _publish_processed_failed(
        self,
        event: DocumentUploadedEvent,
        error: Exception,
        key: bytes | str | None,
    ) -> None:
        event_id, occurred_at = self._event_context()
        failed_event = DocumentProcessedFailedEvent(
            data=DocumentProcessedFailedData(
                document_id=event.data.document_id,
                project_id=event.data.project_id,
                user_id=event.data.user_id,
                error_code=type(error).__name__,
                error_message=str(error)[:500],
            ),
            event_id=event_id,
            occurred_at=occurred_at,
        )
        self.messaging.pub("document.processed.failed", failed_event.toJson(), key)

    def _publish_processed(
        self,
        event: DocumentUploadedEvent,
        chunk_count: int,
        key: bytes | str | None,
    ) -> None:
        event_id, occurred_at = self._event_context()
        processed_event = DocumentProcessedEvent(
            data=DocumentProcessedData(
                document_id=event.data.document_id,
                project_id=event.data.project_id,
                user_id=event.data.user_id,
                chunk_count=chunk_count,
            ),
            event_id=event_id,
            event_type="document.processed",
            occurred_at=occurred_at,
        )
        self.messaging.pub("document.processed", processed_event.toJson(), key)

    def _publish_processing(
        self,
        event: DocumentUploadedEvent,
        key: bytes | str | None,
    ) -> None:
        event_id, occurred_at = self._event_context()
        processing_event = DocumentProcessingEvent(
            data=DocumentProcessingData(
                document_id=event.data.document_id,
                project_id=event.data.project_id,
                user_id=event.data.user_id,
            ),
            event_id=event_id,
            event_type="document.processing",
            occurred_at=occurred_at,
        )
        self.messaging.pub("document.processing", processing_event.toJson(), key)
