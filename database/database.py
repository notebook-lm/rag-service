from contextlib import contextmanager
from collections.abc import Iterator, Sequence
from typing import Any

import psycopg
from psycopg import Cursor

from database.config import DATABASE_URL


class Database:
    """PostgreSQL client used by application services and repositories."""

    @contextmanager
    def transaction(self) -> Iterator[Cursor[Any]]:
        """Yield a cursor in a transaction that commits only on success."""
        with psycopg.connect(DATABASE_URL) as connection:
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
