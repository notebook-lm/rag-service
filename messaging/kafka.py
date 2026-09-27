import logging
import signal
import threading
from collections.abc import Callable
from types import FrameType

from confluent_kafka import Consumer, KafkaError, Message, Producer

from database.database import Database
from messaging.kafka_config import KafkaConfig
from messaging.messaging import Messaging

logger = logging.getLogger(__name__)


class Kafka(Messaging):
    def __init__(self, config: KafkaConfig, database: Database) -> None:
        self.running: bool = True
        self.handlers: dict[str, Callable[[Message], None]] = {}
        self.database = database
        self.consumer = Consumer(
            {
                "bootstrap.servers": config.bootstrap_servers,
                "group.id": config.consumer_group,
                "auto.offset.reset": "earliest",
                "enable.auto.commit": False,
            }
        )
        self.producer = Producer({"bootstrap.servers": config.bootstrap_servers})

    def start(self) -> None:
        if not self.handlers:
            raise RuntimeError("No Kafka topic callbacks have been registered")

        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, self.stop)
            signal.signal(signal.SIGTERM, self.stop)

        self.consumer.subscribe(list(self.handlers))
        logger.info("Kafka consumer started for topics %s", list(self.handlers))

        try:
            while self.running:
                message = self.consumer.poll(1.0)
                if message is None:
                    continue

                if message.error():
                    if message.error().code() != KafkaError._PARTITION_EOF:
                        logger.error("Kafka consumer error: %s", message.error())
                    continue

                callback = self.handlers.get(message.topic())
                if callback is None:
                    logger.warning("No Kafka callback registered for topic %s", message.topic())
                    continue

                try:
                    callback(message)
                    self.consumer.commit(message=message, asynchronous=False)
                except Exception:
                    logger.exception("Could not process Kafka message from topic %s", message.topic())
        finally:
            self.close()

    def pub(self, topic: str, value: bytes, key: bytes | str | None = None) -> None:
        self.producer.produce(topic, value=value, key=key)
        if self.producer.flush(10):
            raise RuntimeError("Could not publish message to %s" % topic)

    def sub(self, topic: str, callback: Callable[[Message], None]) -> None:
        if not callable(callback):
            raise TypeError("Kafka callback must be callable")

        self.handlers[topic] = callback
        logger.info("Registered Kafka callback for topic %s", topic)

    def stop(self, _signum: int | None = None, _frame: FrameType | None = None) -> None:
        self.running = False

    def close(self) -> None:
        self.producer.flush(10)
        self.consumer.close()
        logger.info("Kafka consumer stopped")
