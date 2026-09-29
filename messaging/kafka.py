import logging
import signal
import threading
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from types import FrameType

from confluent_kafka import Consumer, KafkaError, Message, Producer, TopicPartition

from database.database import Database
from messaging.kafka_config import KafkaConfig
from messaging.messaging import Messaging

logger = logging.getLogger(__name__)


class Kafka(Messaging):
    def __init__(
        self,
        config: KafkaConfig,
        database: Database,
        worker_concurrency: int = 1,
        max_in_flight: int = 1,
    ) -> None:
        self.running = True
        self.handlers: dict[str, Callable[[Message], None]] = {}
        self.database = database
        self.max_in_flight = max_in_flight
        self.executor = ThreadPoolExecutor(
            max_workers=worker_concurrency,
            thread_name_prefix="kafka-worker",
        )
        self.in_flight: dict[tuple[str, int], list[tuple[Message, Future[None]]]] = {}
        self.paused: set[tuple[str, int]] = set()
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
                self._complete_work()
                self._apply_backpressure()
                message = self.consumer.poll(0.2)
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
                self._dispatch(message, callback)
        finally:
            self._drain_work()
            self.close()

    def _dispatch(self, message: Message, callback: Callable[[Message], None]) -> None:
        partition_key = (message.topic(), message.partition())
        future = self.executor.submit(callback, message)
        self.in_flight.setdefault(partition_key, []).append((message, future))

    def _complete_work(self) -> None:
        for partition_key, work in list(self.in_flight.items()):
            while work and work[0][1].done():
                message, future = work[0]
                try:
                    future.result()
                except Exception:
                    logger.exception(
                        "Could not process Kafka message from topic %s", message.topic()
                    )
                    self._pause_partition(message)
                    break
                self.consumer.commit(message=message, asynchronous=False)
                work.pop(0)

            if not work:
                self.in_flight.pop(partition_key, None)

    def _apply_backpressure(self) -> None:
        if self._in_flight_count() >= self.max_in_flight:
            assignments = self.consumer.assignment()
            to_pause = [
                assignment
                for assignment in assignments
                if (assignment.topic, assignment.partition) not in self.paused
            ]
            if to_pause:
                self.consumer.pause(to_pause)
                self.paused.update((item.topic, item.partition) for item in to_pause)
            return

        if self.paused:
            assignments = self.consumer.assignment()
            to_resume = [
                assignment
                for assignment in assignments
                if (assignment.topic, assignment.partition) in self.paused
            ]
            if to_resume:
                self.consumer.resume(to_resume)
                self.paused.difference_update((item.topic, item.partition) for item in to_resume)

    def _pause_partition(self, message: Message) -> None:
        partition = TopicPartition(message.topic(), message.partition())
        self.consumer.pause([partition])
        self.paused.add((message.topic(), message.partition()))

    def _in_flight_count(self) -> int:
        return sum(len(work) for work in self.in_flight.values())

    def _drain_work(self) -> None:
        while self._in_flight_count():
            for work in self.in_flight.values():
                for _, future in work:
                    future.result()
            self._complete_work()

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
        self.executor.shutdown(wait=True, cancel_futures=False)
        self.producer.flush(10)
        self.consumer.close()
        logger.info("Kafka consumer stopped")
