import textwrap

from app.codebase.indexer import CodebaseIndexer, CodebaseIndexerError
from app.codebase.retriever import CodeChunk


class CodebaseContextProviderError(Exception):
    """Custom exception for CodebaseContextProvider errors."""
    pass


class CodebaseContextProvider:
    """Provide a concise textual context for a query using an indexed codebase.

    Parameters
    ----------
    indexer : CodebaseIndexer
        A ``CodebaseIndexer`` instance on which ``build()`` has already been called.
    """

    def __init__(self, indexer: CodebaseIndexer):
        if not isinstance(indexer, CodebaseIndexer):
            raise CodebaseContextProviderError(
                "indexer must be a CodebaseIndexer instance"
            )
        self._indexer = indexer

    def get_context(self, query: str, top_k: int = 5) -> str:
        """Return a formatted context string for *query*.

        Each relevant chunk is rendered as::

            File: <relative_path>

            <chunk_text>

        Multiple chunks are separated by a blank line.
        Returns an empty string when no relevant chunks are found.

        Parameters
        ----------
        query : str
            The search query.
        top_k : int, optional
            Maximum number of chunks to include. Must be > 0. Defaults to 5.

        Raises
        ------
        CodebaseContextProviderError
            On invalid arguments or if the underlying indexer raises an error.
        """
        if not isinstance(query, str):
            raise CodebaseContextProviderError("query must be a string")
        if not isinstance(top_k, int) or top_k <= 0:
            raise CodebaseContextProviderError(
                "top_k must be a positive integer"
            )

        try:
            chunks = self._indexer.search(query, top_k)
        except Exception as exc:
            raise CodebaseContextProviderError(str(exc)) from exc

        if not chunks:
            return ""

        parts = []
        for chunk in chunks:
            if not isinstance(chunk, CodeChunk):
                continue
            header = f"File: {chunk.path}"
            body = textwrap.dedent(chunk.text).strip("\n")
            parts.append(f"{header}\n\n{body}")

        return "\n\n".join(parts)
