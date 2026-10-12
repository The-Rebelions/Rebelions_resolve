import pytest
from app.codebase.chunker import CodeChunker, CodeChunkerError

def test_empty_text():
    chunker = CodeChunker(chunk_size=10)
    assert chunker.chunk("") == []

def test_short_text():
    chunker = CodeChunker(chunk_size=10)
    text = "short"
    assert chunker.chunk(text) == [text]

def test_multiple_chunks():
    chunker = CodeChunker(chunk_size=5)
    text = "abcdefghij"
    assert chunker.chunk(text) == ["abcde", "fghij"]

def test_overlap_behavior():
    chunker = CodeChunker(chunk_size=5, overlap=2)
    text = "abcdefghij"
    assert chunker.chunk(text) == ["abcde", "defgh", "ghij"]

def test_invalid_chunk_size():
    with pytest.raises(CodeChunkerError):
        CodeChunker(chunk_size=0)

def test_invalid_overlap():
    with pytest.raises(CodeChunkerError):
        CodeChunker(chunk_size=5, overlap=5)
