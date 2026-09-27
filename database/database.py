"""Abstract database contract."""

from abc import ABC, abstractmethod
from collections.abc import Iterator, Sequence
from typing import Any


class Database(ABC):
    """Persistence operations required by repositories and handlers."""

    @abstractmethod
    def transaction(self) -> Iterator[Any]:
        """Yield a cursor enclosed in a transaction."""

    @abstractmethod
    def execute(
        self,
        cursor: Any,
        query: str,
        parameters: Sequence[Any] | None = None,
    ) -> None:
        """Execute a statement without returning data."""

    @abstractmethod
    def fetch_one(
        self,
        cursor: Any,
        query: str,
        parameters: Sequence[Any] | None = None,
    ) -> tuple[Any, ...] | None:
        """Execute a statement and return one row."""
