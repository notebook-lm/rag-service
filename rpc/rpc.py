"""Abstract RPC server contract."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class Rpc(ABC):
    """RPC server lifecycle and service registration operations."""

    @abstractmethod
    def add_service(self, service: object, registrar: Callable[..., Any]) -> None:
        """Register a service implementation with the server."""

    @abstractmethod
    def start(self) -> None:
        """Start serving registered RPC services."""
