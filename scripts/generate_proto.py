"""Generate Python gRPC bindings from the protobuf contracts."""

from pathlib import Path

from grpc_tools import protoc

ROOT = Path(__file__).resolve().parent.parent
PROTO_DIR = ROOT / "proto"
OUTPUT_DIR = ROOT / "rpc" / "generated"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    proto_paths = sorted(PROTO_DIR.glob("*.proto"))
    result = protoc.main(
        [
            "grpc_tools.protoc",
            f"-I{PROTO_DIR}",
            f"--python_out={OUTPUT_DIR}",
            f"--grpc_python_out={OUTPUT_DIR}",
            *(str(path) for path in proto_paths),
        ]
    )
    if result:
        raise SystemExit(result)

    for proto_path in proto_paths:
        module_name = f"{proto_path.stem}_pb2"
        stub_path = OUTPUT_DIR / f"{module_name}_grpc.py"
        stub_path.write_text(
            stub_path.read_text().replace(
                f"import {module_name} as {proto_path.stem}__pb2",
                f"from . import {module_name} as {proto_path.stem}__pb2",
            )
        )


if __name__ == "__main__":
    main()
