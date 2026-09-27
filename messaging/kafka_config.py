"""Kafka client configuration."""


class KafkaConfig:
    def __init__(self, bootstrap_servers: str, consumer_group: str) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.consumer_group = consumer_group
