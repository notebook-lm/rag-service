"""Abstract messaging contract."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class Messaging(ABC):
    """Message publishing and subscription operations used by the application."""

    @abstractmethod
    def start(self) -> None:
        """Start consuming subscribed topics."""

    @abstractmethod
    def pub(self, topic: str, value: bytes, key: bytes | str | None = None) -> None:
        """Publish a message."""

    @abstractmethod
    def sub(self, topic: str, callback: Callable[[Any], None]) -> None:
        """Register a callback for a topic."""

    @abstractmethod
    def stop(self, *_: Any) -> None:
        """Request consumer shutdown."""

    @abstractmethod
    def close(self) -> None:
        """Release messaging resources."""
