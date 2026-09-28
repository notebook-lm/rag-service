"""Unit tests for the Hello World gRPC service."""

import unittest

from rpc.generated import hello_pb2
from rpc.services.hello_service import HelloService


class HelloServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_say_hello_returns_the_provided_name(self) -> None:
        response = await HelloService().SayHello(
            hello_pb2.HelloRequest(name="An"),
            context=None,
        )

        self.assertEqual(response.message, "Hello, An!")

    async def test_say_hello_defaults_blank_name_to_world(self) -> None:
        response = await HelloService().SayHello(
            hello_pb2.HelloRequest(name="   "),
            context=None,
        )

        self.assertEqual(response.message, "Hello, world!")


if __name__ == "__main__":
    unittest.main()
