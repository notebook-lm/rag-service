import json
import logging

from confluent_kafka import Message

from database.database import Database
from database.entities.inbox import Inbox
from database.repositories.inbox_repository import InboxRepository
from messaging.events.document_processed import DocumentProcessedData, DocumentProcessedEvent
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
        document_uploaded_data = document_uploaded_payload["data"]
        if not isinstance(document_uploaded_data, dict):
            raise ValueError("document.uploaded event data must be an object")

        document_uploaded_event = DocumentUploadedEvent(
            data=DocumentUploadedData(
                object_key=str(document_uploaded_data["objectKey"]),
                project_id=str(document_uploaded_data["projectId"]),
                size_bytes=int(document_uploaded_data["sizeBytes"]),
                document_id=str(document_uploaded_data["documentId"]),
                content_type=str(document_uploaded_data["contentType"]),
                original_filename=str(document_uploaded_data["originalFilename"]),
            ),
            event_id=str(document_uploaded_payload["eventId"]),
            event_type=str(document_uploaded_payload["eventType"]),
            occurred_at=str(document_uploaded_payload["occurredAt"]),
        )

        logger.info("Document %s is now processing", document_uploaded_event.data.document_id)
        self._publish_processing(document_uploaded_event, "PROCESSING", message.key())

        storage_object = self.storage.get(document_uploaded_event.data.object_key)
        parser = self._get_parser(storage_object)
        text = parser.parse(storage_object.content)
        chunks = self.chunker.chunk(
            text,
            {
                "document_id": document_uploaded_event.data.document_id,
                "project_id": document_uploaded_event.data.project_id,
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

        logger.info(
            "Document %s indexed with %s chunks",
            document_uploaded_event.data.document_id,
            len(chunks),
        )
        self._publish_processed(document_uploaded_event, len(chunks), message.key())
        self._publish_processing(document_uploaded_event, "COMPLETED", message.key())

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

    def _publish_processed(
        self,
        event: DocumentUploadedEvent,
        chunk_count: int,
        key: bytes | str | None,
    ) -> None:
        processed_event = DocumentProcessedEvent(
            data=DocumentProcessedData(
                document_id=event.data.document_id,
                project_id=event.data.project_id,
                chunk_count=chunk_count,
            ),
            event_id=event.event_id,
            event_type="document.processed",
            occurred_at=event.occurred_at,
        )
        self.messaging.pub("document.processed", processed_event.toJson(), key)

    def _publish_processing(
        self,
        event: DocumentUploadedEvent,
        status: str,
        key: bytes | str | None,
    ) -> None:
        processing_event = DocumentProcessingEvent(
            data=DocumentProcessingData(
                document_id=event.data.document_id,
                project_id=event.data.project_id,
                status=status,
            ),
            event_id=event.event_id,
            event_type="document.processing",
            occurred_at=event.occurred_at,
        )
        self.messaging.pub("document.processing", processing_event.toJson(), key)
