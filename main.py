import logging
import threading

from kafka.handlers.document_uploaded import DocumentUploadedHandler
from kafka.kafka import KafkaClient

logger = logging.getLogger(__name__)
kafka = KafkaClient()

def setup_kafka() -> None:
    logger.info("Kafka initializing")

    document_uploaded_handler = DocumentUploadedHandler(kafka)

    kafka.sub("document.uploaded", document_uploaded_handler.execute)

    threading.Thread(target=kafka.start, name="kafka-consumer", daemon=True).start()

    logger.info("Kafka initialized")

def main() -> None:
    logger.info("Application started")
    setup_kafka()

if __name__ == "__main__":
    main()
