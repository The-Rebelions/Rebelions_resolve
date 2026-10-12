class CodebaseIndexerError(Exception):
    """Error raised by CodebaseIndexer for misuse or internal failures."""
    pass

from app.codebase.scanner import CodebaseScanner
from app.codebase.reader import CodeFileReader, CodeFileReaderError
from app.codebase.chunker import CodeChunker, CodeChunkerError
from app.codebase.retriever import CodebaseRetriever, CodeChunk, CodebaseRetrieverError
from app.codebase.symbols import CodeSymbolExtractor, CodeSymbolExtractionError

class CodebaseIndexer:
    """Index a project's code files into searchable chunks.

    Workflow:
        idx = CodebaseIndexer(project_root, chunk_size=200, overlap=20)
        idx.build()
        results = idx.search('query')
    """

    def __init__(self, project_root: str, chunk_size: int, overlap: int = 0):
        # Validate chunker parameters early.
        try:
            self._chunker = CodeChunker(chunk_size, overlap)
        except CodeChunkerError as exc:
            raise CodebaseIndexerError(str(exc))
        self._scanner = CodebaseScanner(project_root)
        self._reader = CodeFileReader(project_root)
        self._chunks = []
        self._symbols: list[dict] = []
        self._retriever = None
        self._symbol_extractor = CodeSymbolExtractor()

    def build(self) -> None:
        """Scan the project, read files, chunk their contents, and build the retriever.

        Files that cannot be read (missing, permission errors, etc.) are silently
        skipped so that indexing can continue for the rest of the project.
        """
        self._chunks = []
        self._symbols = []
        for rel_path in self._scanner.scan():
            try:
                content = self._reader.read(rel_path)
            except CodeFileReaderError:
                # Skip unreadable files.
                continue
            for chunk_text in self._chunker.chunk(content):
                self._chunks.append(CodeChunk(rel_path, chunk_text))
            # Extract symbols from Python files; ignore parse errors.
            if rel_path.endswith(".py"):
                try:
                    self._symbols.extend(
                        self._symbol_extractor.extract(rel_path, content)
                    )
                except CodeSymbolExtractionError:
                    pass
        # Build the retriever with the collected chunks.
        self._retriever = CodebaseRetriever(self._chunks)

    def search(self, query: str, top_k: int = 5):
        """Search the indexed chunks.

        Raises
        ------
        CodebaseIndexerError
            If ``build`` has not been called yet.
        """
        if self._retriever is None:
            raise CodebaseIndexerError("Index not built yet. Call build() before searching.")
        return self._retriever.search(query, top_k)

    def find_symbol(self, name: str) -> list[dict]:
        """Return all indexed symbols whose ``name`` matches *name* exactly.

        Parameters
        ----------
        name : str
            Exact symbol name to look up (case-sensitive).

        Returns
        -------
        list[dict]
            Matching symbol dicts, in the order they were indexed.  Empty list
            when no symbol matches or when ``build`` has not been called.
        """
        return [s for s in self._symbols if s["name"] == name]
