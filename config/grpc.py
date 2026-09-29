"""gRPC server environment configuration."""

import os

GRPC_PORT = int(os.getenv("GRPC_PORT", "50051"))
