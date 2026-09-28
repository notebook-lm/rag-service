"""Hello World gRPC service implementation."""

from rpc.generated import hello_pb2, hello_pb2_grpc


class HelloService(hello_pb2_grpc.HelloServiceServicer):
    """Returns a friendly greeting for a caller-provided name."""

    async def SayHello(self, request, context):
        name = request.name.strip() or "world"
        return hello_pb2.HelloResponse(message=f"Hello, {name}!")
