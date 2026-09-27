import json
import logging

from confluent_kafka import Message

from database.postgres import Postgres
from database.entities.inbox import Inbox
from database.repositories.inbox_repository import InboxRepository
from messaging.events.document_processing import DocumentProcessingData, DocumentProcessingEvent
from messaging.events.document_uploaded import DocumentUploadedData, DocumentUploadedEvent
from messaging.kafka import KafkaClient

logger = logging.getLogger(__name__)


class DocumentUploadedHandler:
    def __init__(self, kafka_client: KafkaClient, postgres: Postgres) -> None:
        self.kafka_client = kafka_client
        self.inbox_repository = InboxRepository(postgres)
        self.postgres = postgres

    def execute(self, message: Message) -> None:
        payload = message.value()
        document_uploaded_payload = json.loads(payload)
        event_id = document_uploaded_payload["eventId"]

        with self.postgres.transaction() as cursor:
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
        document_processing_event = DocumentProcessingEvent(
            data=DocumentProcessingData(
                document_id=document_uploaded_event.data.document_id,
                project_id=document_uploaded_event.data.project_id,
                status="PROCESSING",
            ),
            event_id=document_uploaded_event.event_id,
            event_type="document.processing",
            occurred_at=document_uploaded_event.occurred_at,
        )

        logger.info("Document %s is now processing", document_uploaded_event.data.document_id)
        self.kafka_client.pub(
            "document.processing", document_processing_event.toJson(), message.key()
        )
