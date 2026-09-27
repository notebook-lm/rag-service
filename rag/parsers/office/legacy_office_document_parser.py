"""Parser for legacy Office files converted with LibreOffice."""

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from rag.parsers.parser import Parser


class LegacyOfficeDocumentParser(Parser):
    """Convert a legacy Office file before delegating text extraction."""

    def __init__(self, source_extension: str, target_extension: str, parser: Parser) -> None:
        self.source_extension = source_extension
        self.target_extension = target_extension
        self.parser = parser

    def parse(self, content: bytes) -> str:
        with TemporaryDirectory() as directory:
            source_path = Path(directory, f"document.{self.source_extension}")
            source_path.write_bytes(content)
            subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to",
                    self.target_extension,
                    "--outdir",
                    directory,
                    str(source_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            target_path = source_path.with_suffix(f".{self.target_extension}")
            if not target_path.exists():
                raise RuntimeError(f"LibreOffice did not produce {target_path.name}")
            return self.parser.parse(target_path.read_bytes())
