from pathlib import Path


class FileToolError(Exception):
    """Raised when a file tool operation fails."""


class FileTool:
    def read_file(self, path: str) -> str:
        file_path = Path(path)

        if not file_path.exists():
            raise FileToolError("File does not exist.")

        if not file_path.is_file():
            raise FileToolError("Path is not a file.")

        try:
            return file_path.read_text(encoding="utf-8")
        except OSError as error:
            raise FileToolError(
                f"Failed to read file: {error}"
            ) from error