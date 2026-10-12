class CodeFileReaderError(Exception):
    """Custom exception for CodeFileReader errors."""
    pass


class CodeFileReader:
    """Utility to safely read text/code files within a project workspace.

    Attributes
    ----------
    project_root : str
        The absolute or relative path to the root of the project workspace.
    """

    def __init__(self, project_root: str):
        import os
        self.project_root = os.path.abspath(project_root)

    def _resolve_path(self, relative_path: str) -> str:
        """Resolve *relative_path* against the project root.

        Ensures the final resolved path is inside ``self.project_root``.
        Raises ``CodeFileReaderError`` if the path attempts traversal outside.
        """
        import os
        candidate = os.path.abspath(os.path.join(self.project_root, relative_path))
        if not candidate.startswith(self.project_root + os.sep):
            raise CodeFileReaderError(f"Path traversal outside project root is not allowed: {relative_path}")
        return candidate

    def read(self, relative_path: str) -> str:
        """Read the contents of a file located at *relative_path*.

        Parameters
        ----------
        relative_path : str
            Path to the file relative to the project root.

        Returns
        -------
        str
            File contents decoded as UTF‑8.

        Raises
        ------
        CodeFileReaderError
            If the path is invalid, points to a directory, the file does not exist,
            or the file cannot be read as UTF‑8.
        """
        import os
        try:
            target_path = self._resolve_path(relative_path)
        except Exception as e:
            raise CodeFileReaderError(str(e))

        if not os.path.exists(target_path):
            raise CodeFileReaderError(f"File does not exist: {relative_path}")
        if os.path.isdir(target_path):
            raise CodeFileReaderError(f"Path is a directory, not a file: {relative_path}")
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            raise CodeFileReaderError(f"File is not valid UTF-8 text: {relative_path}")
        except OSError as ose:
            raise CodeFileReaderError(f"Failed to read file {relative_path}: {ose}")
