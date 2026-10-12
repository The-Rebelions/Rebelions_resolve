import os
import tempfile

import pytest

from app.codebase.indexer import CodebaseIndexer
from app.agent.codebase_context import (
    CodebaseContextProvider,
    CodebaseContextProviderError,
)


def _write(root: str, rel_path: str, content: str) -> None:
    full = os.path.join(root, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)


# ---------------------------------------------------------------------------
# 1. Relevant context is returned
# ---------------------------------------------------------------------------

def test_relevant_context_returned():
    with tempfile.TemporaryDirectory() as root:
        _write(root, "a.py", "def foo():\n    return 42\n")
        indexer = CodebaseIndexer(root, chunk_size=200)
        indexer.build()
        provider = CodebaseContextProvider(indexer)

        context = provider.get_context("foo")

        assert "def foo()" in context
        assert "File: a.py" in context


# ---------------------------------------------------------------------------
# 2. File paths are included in the output
# ---------------------------------------------------------------------------

def test_file_paths_included():
    with tempfile.TemporaryDirectory() as root:
        _write(root, os.path.join("app", "module", "b.py"), "value = 123\n")
        indexer = CodebaseIndexer(root, chunk_size=200)
        indexer.build()
        provider = CodebaseContextProvider(indexer)

        context = provider.get_context("value")

        assert "File:" in context
        # path separator is OS-dependent; check that the filename appears
        assert "b.py" in context


# ---------------------------------------------------------------------------
# 3. Multiple results are separated by a blank line
# ---------------------------------------------------------------------------

def test_multiple_results_separated():
    with tempfile.TemporaryDirectory() as root:
        _write(root, "alpha.py", "alpha = 1\n")
        _write(root, "beta.py", "beta = 2\n")
        indexer = CodebaseIndexer(root, chunk_size=200)
        indexer.build()
        provider = CodebaseContextProvider(indexer)

        context = provider.get_context("alpha beta", top_k=2)

        # Splitting on double newlines yields the two separate blocks
        blocks = [b.strip() for b in context.split("\n\n") if b.strip()]
        assert len(blocks) >= 2
        file_headers = [b for b in blocks if b.startswith("File:")]
        assert len(file_headers) == 2


# ---------------------------------------------------------------------------
# 4. No results returns an empty string
# ---------------------------------------------------------------------------

def test_no_results_returns_empty_string():
    with tempfile.TemporaryDirectory() as root:
        _write(root, "c.py", "print('hello')\n")
        indexer = CodebaseIndexer(root, chunk_size=200)
        indexer.build()
        provider = CodebaseContextProvider(indexer)

        context = provider.get_context("nonexistent_xyz_keyword_404")

        assert context == ""
