"""Generate Python gRPC bindings from the protobuf contracts."""

from pathlib import Path

from grpc_tools import protoc

ROOT = Path(__file__).resolve().parent.parent
PROTO_DIR = ROOT / "proto"
OUTPUT_DIR = ROOT / "rpc" / "generated"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result = protoc.main(
        [
            "grpc_tools.protoc",
            f"-I{PROTO_DIR}",
            f"--python_out={OUTPUT_DIR}",
            f"--grpc_python_out={OUTPUT_DIR}",
            *(str(path) for path in PROTO_DIR.glob("*.proto")),
        ]
    )
    if result:
        raise SystemExit(result)

    stub_path = OUTPUT_DIR / "hello_pb2_grpc.py"
    stub_path.write_text(
        stub_path.read_text().replace(
            "import hello_pb2 as hello__pb2",
            "from . import hello_pb2 as hello__pb2",
        )
    )


if __name__ == "__main__":
    main()
