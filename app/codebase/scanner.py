import os

# Supported file extensions for code and text files
supported_extensions = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".json",
    ".yaml", ".yml", ".md", ".txt", ".sql", ".java", ".c", ".cpp", ".h",
}

class CodebaseScanner:
    """Recursively scans a project directory for code and text files.

    The scanner stays within the given ``project_root`` and returns file
    paths relative to that root. It ignores common artefact directories and
    binary files, and only returns files whose extension is in
    ``supported_extensions``.
    """

    def __init__(self, project_root: str):
        self.project_root = os.path.abspath(project_root)
        self.ignore_dirs = {".git", ".venv", "models", "__pycache__"}

    def _is_binary(self, file_path: str) -> bool:
        """Detect binary files by checking for a null byte in the first KB."""
        try:
            with open(file_path, "rb") as f:
                return b"\0" in f.read(1024)
        except Exception:
            return True

    def scan(self) -> list[str]:
        """Return a deterministic, sorted list of relative file paths.

        Only files with extensions in ``supported_extensions`` and that are
        not detected as binary are included.
        """
        results: list[str] = []
        for root, dirs, files in os.walk(self.project_root):
            # Exclude ignored directories and hidden dirs
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs and not d.startswith('.')]
            for file in files:
                _, ext = os.path.splitext(file)
                if ext.lower() in supported_extensions:
                    full_path = os.path.join(root, file)
                    if not self._is_binary(full_path):
                        rel_path = os.path.relpath(full_path, self.project_root)
                        results.append(rel_path)
        return sorted(results)
