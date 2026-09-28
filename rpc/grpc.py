"""gRPC implementation of the RPC server contract."""

import asyncio
import logging
from collections.abc import Callable
from typing import Any

import grpc

from rpc.rpc import Rpc

logger = logging.getLogger(__name__)


class Grpc(Rpc):
    """Runs registered gRPC services on an asyncio server."""

    def __init__(self, port: int = 50051) -> None:
        self.port = port
        self.services: list[tuple[object, Callable[..., Any]]] = []

    def add_service(self, service: object, registrar: Callable[..., Any]) -> None:
        self.services.append((service, registrar))

    def start(self) -> None:
        asyncio.run(self._serve())

    async def _serve(self) -> None:
        server = grpc.aio.server()
        for service, registrar in self.services:
            registrar(service, server)

        server.add_insecure_port(f"[::]:{self.port}")
        await server.start()
        logger.info("gRPC server listening on port %s", self.port)
        await server.wait_for_termination()
