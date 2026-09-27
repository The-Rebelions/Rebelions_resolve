from pathlib import Path

from app.tools.permissions import PermissionPolicy


class FileToolError(Exception):
    """Raised when a file tool operation fails."""


class FileTool:
    def __init__(self, project_root: str, permissions: PermissionPolicy):
        self.project_root = Path(project_root).resolve()
        self.permissions = permissions

    def read_file(self, path: str) -> str:
        self.permissions.check_file_read()

        file_path = (self.project_root / path).resolve()

        if not file_path.is_relative_to(self.project_root):
            raise FileToolError(
                "Access denied: path is outside the project directory."
            )

        if not file_path.exists():
            raise FileToolError("File does not exist.")

        if not file_path.is_file():
            raise FileToolError("Path is not a file.")

        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise FileToolError(
                "File is not valid UTF-8 text."
            ) from error
        except OSError as error:
            raise FileToolError(
                f"Failed to read file: {error}"
            ) from error
            
    def write_file(self, path: str, content: str) -> None:
        self.permissions.check_file_write()

        file_path = (self.project_root / path).resolve()

        if not file_path.is_relative_to(self.project_root):
            raise FileToolError(
                "Access denied: path is outside the project directory."
            )

        if file_path.exists() and not file_path.is_file():
            raise FileToolError("Path is not a file.")

        try:
            file_path.write_text(content, encoding="utf-8")
        except OSError as error:
            raise FileToolError(
                f"Failed to write file: {error}"
            ) from error    