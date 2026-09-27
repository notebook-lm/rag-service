"""Postgres client configuration."""


class PostgresConfig:
    def __init__(self, postgres_url: str) -> None:
        self.postgres_url = postgres_url
