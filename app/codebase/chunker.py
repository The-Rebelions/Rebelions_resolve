class CodeChunkerError(Exception):
    """Custom exception for CodeChunker configuration errors."""


class CodeChunker:
    """Simple character-based text chunker."""

    def __init__(self, chunk_size: int, overlap: int = 0):
        if not isinstance(chunk_size, int) or chunk_size <= 0:
            raise CodeChunkerError(
                "chunk_size must be a positive integer"
            )

        if (
            not isinstance(overlap, int)
            or overlap < 0
            or overlap >= chunk_size
        ):
            raise CodeChunkerError(
                "overlap must be an integer satisfying "
                "0 <= overlap < chunk_size"
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        """Split text into overlapping character-based chunks."""

        if not isinstance(text, str):
            raise CodeChunkerError("text must be a string")

        if text == "":
            return []

        chunks = []
        i = 0
        length = len(text)

        while i < length:
            end = i + self.chunk_size
            chunk_text = text[i:end]
            if not chunk_text:
                break
            chunks.append(chunk_text)

            # If this chunk reaches or exceeds the text length, we're done.
            if end >= length:
                break

            i = end - self.overlap

        return chunks