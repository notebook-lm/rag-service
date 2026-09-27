"""Abstract document-to-text parser contract."""

from abc import ABC, abstractmethod


class Parser(ABC):
    """Turn raw document bytes into plain text."""

    @abstractmethod
    def parse(self, content: bytes) -> str:
        """Extract text from raw document bytes."""
