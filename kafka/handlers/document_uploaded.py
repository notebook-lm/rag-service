import json
import logging

from confluent_kafka import Message

from kafka.events.document_processing import DocumentProcessingData, DocumentProcessingEvent
from kafka.events.document_uploaded import DocumentUploadedData, DocumentUploadedEvent
from kafka.kafka import KafkaClient

logger = logging.getLogger(__name__)

class DocumentUploadedHandler:
    def __init__(self, kafka: KafkaClient) -> None:
        self.kafka = kafka

    def execute(self, message: Message) -> None:
        logger.info(
            "Document uploaded event received: %s",
            message,
        )

        documentUploadedPayload = json.loads(message.value())
        documentUploadedData = documentUploadedPayload["data"]

        documentUploadedEvent = DocumentUploadedEvent(
            data=DocumentUploadedData(
                object_key=documentUploadedData["objectKey"],
                project_id=documentUploadedData["projectId"],
                size_bytes=documentUploadedData["sizeBytes"],
                document_id=documentUploadedData["documentId"],
                content_type=documentUploadedData["contentType"],
                original_filename=documentUploadedData["originalFilename"],
            ),
            event_id=documentUploadedPayload["eventId"],
            event_type=documentUploadedPayload["eventType"],
            occurred_at=documentUploadedPayload["occurredAt"],
        )
        documentProcessingEvent = DocumentProcessingEvent(
            data=DocumentProcessingData(
                document_id=documentUploadedEvent.data.document_id,
                project_id=documentUploadedEvent.data.project_id,
                status="PROCESSING",
            ),
            event_id=documentUploadedEvent.event_id,
            event_type="document.processing",
            occurred_at=documentUploadedEvent.occurred_at,
        )

        logger.info(
            "Document %s is now processing",
            documentUploadedEvent.data.document_id,
        )
        self.kafka.pub("document.processing", documentProcessingEvent.toJson(), message.key())
