from contextlib import contextmanager
from collections.abc import Iterator, Sequence
from typing import Any

import psycopg
from psycopg import Cursor

from database.postgres_config import PostgresConfig


class Postgres:
    """PostgreSQL client used by application services and repositories."""

    def __init__(self, config: PostgresConfig) -> None:
        self.config = config

    @contextmanager
    def transaction(self) -> Iterator[Cursor[Any]]:
        """Yield a cursor in a transaction that commits only on success."""
        with psycopg.connect(self.config.postgres_url) as connection:
            with connection.transaction(), connection.cursor() as cursor:
                yield cursor

    def execute(
        self,
        cursor: Cursor[Any],
        query: str,
        parameters: Sequence[Any] | None = None,
    ) -> None:
        cursor.execute(query, parameters)

    def fetch_one(
        self,
        cursor: Cursor[Any],
        query: str,
        parameters: Sequence[Any] | None = None,
    ) -> tuple[Any, ...] | None:
        cursor.execute(query, parameters)
        return cursor.fetchone()
