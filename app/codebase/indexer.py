import re

from app.codebase.scanner import CodebaseScanner
from app.codebase.reader import CodeFileReader, CodeFileReaderError
from app.codebase.chunker import CodeChunker, CodeChunkerError
from app.codebase.retriever import (
    CodebaseRetriever,
    CodeChunk,
)
from app.codebase.symbols import (
    CodeSymbolExtractor,
    CodeSymbolExtractionError,
)


class CodebaseIndexerError(Exception):
    """Error raised by CodebaseIndexer for misuse or internal failures."""


class CodebaseIndexer:
    """Index a project's code files into searchable chunks."""

    def __init__(self, project_root: str, chunk_size: int, overlap: int = 0):
        try:
            self._chunker = CodeChunker(chunk_size, overlap)
        except CodeChunkerError as exc:
            raise CodebaseIndexerError(str(exc)) from exc

        self._scanner = CodebaseScanner(project_root)
        self._reader = CodeFileReader(project_root)
        self._chunks = []
        self._symbols: list[dict] = []
        self._retriever = None
        self._symbol_extractor = CodeSymbolExtractor()

    def build(self) -> None:
        """Scan, read, chunk, and index the project."""
        self._chunks = []
        self._symbols = []

        for rel_path in self._scanner.scan():
            try:
                content = self._reader.read(rel_path)
            except CodeFileReaderError:
                continue

            for chunk_text in self._chunker.chunk(content):
                self._chunks.append(CodeChunk(rel_path, chunk_text))

            if rel_path.endswith(".py"):
                try:
                    symbols = self._symbol_extractor.extract(
                        rel_path,
                        content,
                    )
                    self._symbols.extend(symbols)
                except CodeSymbolExtractionError:
                    continue

        self._retriever = CodebaseRetriever(self._chunks)

    def search(self, query: str, top_k: int = 5):
        """Search chunks with exact-symbol matches prioritized."""
        if self._retriever is None:
            raise CodebaseIndexerError(
                "Index not built yet. Call build() before searching."
            )

        if top_k <= 0:
            raise CodebaseIndexerError(
                "top_k must be greater than zero."
            )

        query_tokens = set(
            re.findall(r"[A-Za-z_][A-Za-z0-9_]*", query)
        )

        exact_symbols = {
            symbol["name"]
            for symbol in self._symbols
            if symbol["name"] in query_tokens
        }

        results = []
        seen = set()

        # Prioritize chunks that actually contain the exact symbol.
        if exact_symbols:
            for chunk in self._chunks:
                if any(
                    re.search(
                        rf"\b{re.escape(symbol)}\b",
                        chunk.text,
                    )
                    for symbol in exact_symbols
                ):
                    chunk_id = id(chunk)

                    if chunk_id not in seen:
                        seen.add(chunk_id)
                        results.append(chunk)

                        if len(results) >= top_k:
                            return results

        # Fall back to the existing keyword retrieval.
        for chunk in self._retriever.search(query, top_k):
            chunk_id = id(chunk)

            if chunk_id not in seen:
                seen.add(chunk_id)
                results.append(chunk)

                if len(results) >= top_k:
                    break

        return results

    def find_symbol(self, name: str) -> list[dict]:
        """Return indexed symbols matching the exact name."""
        return [
            symbol
            for symbol in self._symbols
            if symbol["name"] == name
        ]