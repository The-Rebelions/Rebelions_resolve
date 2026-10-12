"""Extract Python symbols (functions, classes, methods) using the built-in ast module."""

import ast


class CodeSymbolExtractionError(Exception):
    """Raised when a Python source file cannot be parsed."""
    pass


class CodeSymbolExtractor:
    """Extract top-level and nested Python symbols from source text.

    Only ``.py`` file paths are processed; all other extensions return an empty
    list immediately.  Source code is never executed — the ``ast`` module is used
    for static parsing only.
    """

    def extract(self, file_path: str, text: str) -> list[dict]:
        """Parse *text* and return a list of symbol descriptors.

        Parameters
        ----------
        file_path : str
            Relative (or absolute) path of the source file.  Used to decide
            whether the file is a Python file and to populate the ``file_path``
            field of each returned symbol.
        text : str
            Full source code of the file.

        Returns
        -------
        list[dict]
            Each dict has the keys: ``name``, ``type``, ``file_path``,
            ``line_number``.  Empty list for non-Python files.

        Raises
        ------
        CodeSymbolExtractionError
            If *text* is a ``.py`` file but contains invalid Python syntax.
        """
        if not file_path.endswith(".py"):
            return []

        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            raise CodeSymbolExtractionError(
                f"Syntax error in {file_path!r}: {exc}"
            ) from exc

        symbols: list[dict] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                symbols.append(
                    {
                        "name": node.name,
                        "type": "class",
                        "file_path": file_path,
                        "line_number": node.lineno,
                    }
                )
                # Extract methods defined directly inside this class.
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        symbols.append(
                            {
                                "name": child.name,
                                "type": "method",
                                "file_path": file_path,
                                "line_number": child.lineno,
                            }
                        )
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Only emit top-level functions; methods are handled above.
                if not isinstance(
                    getattr(node, "_parent", None), ast.ClassDef
                ):
                    # Check whether the direct parent in the AST is a ClassDef.
                    # ast.walk does not expose parent information natively, so we
                    # use the parent-annotation pass below.
                    pass  # handled after parent annotation

        # Re-walk with explicit parent tracking to distinguish functions from methods.
        symbols = []
        self._annotate_parents(tree)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                symbols.append(
                    {
                        "name": node.name,
                        "type": "class",
                        "file_path": file_path,
                        "line_number": node.lineno,
                    }
                )
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        symbols.append(
                            {
                                "name": child.name,
                                "type": "method",
                                "file_path": file_path,
                                "line_number": child.lineno,
                            }
                        )
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                parent = getattr(node, "_parent", None)
                if not isinstance(parent, ast.ClassDef):
                    symbols.append(
                        {
                            "name": node.name,
                            "type": "function",
                            "file_path": file_path,
                            "line_number": node.lineno,
                        }
                    )

        return symbols

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _annotate_parents(tree: ast.AST) -> None:
        """Attach a ``_parent`` attribute to every node in *tree*."""
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child._parent = node  # type: ignore[attr-defined]
