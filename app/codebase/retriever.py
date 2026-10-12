class CodebaseRetrieverError(Exception):
    """Custom exception for CodebaseRetriever configuration errors."""
    pass


class CodeChunk:
    """Simple container for a code chunk.

    Attributes
    ----------
    path: str
        Relative file path of the chunk.
    text: str
        The text content of the chunk.
    """

    def __init__(self, path: str, text: str):
        self.path = path
        self.text = text

    def __repr__(self):
        return f"CodeChunk(path={self.path!r}, text={self.text!r})"


class CodebaseRetriever:
    """Retrieve most relevant code chunks for a query.

    The retrieval is based on a simple case‑insensitive keyword match. Each
    query term contributes one point to a chunk's score if the term appears in the
    chunk's text. Results are ordered by descending score and, for equal scores,
    by the original order of the chunks (deterministic).
    """

    def __init__(self, chunks):
        # Expect an iterable of CodeChunk objects.
        self._chunks = list(chunks)

    def _score_chunk(self, chunk, terms):
        """Return the number of query terms present in ``chunk.text``.

        Matching is case‑insensitive and each term contributes at most one point.
        """
        text_lc = chunk.text.lower()
        return sum(1 for term in terms if term in text_lc)

    def search(self, query: str, top_k: int = 5):
        """Return the most relevant chunks for ``query``.

        Parameters
        ----------
        query: str
            The search query.
        top_k: int, optional
            Maximum number of results to return. Must be > 0.
        """
        if not isinstance(top_k, int) or top_k <= 0:
            raise CodebaseRetrieverError("top_k must be a positive integer")

        # Split query into non‑empty terms, ignoring punctuation via simple split.
        terms = [t for t in query.lower().split() if t]
        if not terms:
            return []

        scored = []
        for idx, chunk in enumerate(self._chunks):
            score = self._score_chunk(chunk, terms)
            if score > 0:
                scored.append((score, idx, chunk))

        # Sort by descending score, then by original index for deterministic order.
        scored.sort(key=lambda x: (-x[0], x[1]))
        return [chunk for _, _, chunk in scored[:top_k]]
