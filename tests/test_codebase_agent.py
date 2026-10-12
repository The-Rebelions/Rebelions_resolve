import os
import tempfile

import pytest

from app.codebase.indexer import CodebaseIndexer
from app.agent.codebase_context import CodebaseContextProvider
from app.agent.codebase_agent import CodebaseAgent


# ---------------------------------------------------------------------------
# Minimal fake inference engine — no real model is loaded
# ---------------------------------------------------------------------------

class FakeEngine:
    """Record every prompt it receives and return a fixed answer."""

    def __init__(self, answer: str = "fake answer"):
        self._answer = answer
        self.last_prompt: str = ""

    def generate(self, prompt: str):
        self.last_prompt = prompt
        # Mimic the real engine''s (output, performance) return signature.
        return self._answer, None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(root: str, rel_path: str, content: str) -> None:
    full = os.path.join(root, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)


def _make_agent(root: str, fake_engine: FakeEngine) -> CodebaseAgent:
    indexer = CodebaseIndexer(root, chunk_size=200)
    indexer.build()
    provider = CodebaseContextProvider(indexer)
    return CodebaseAgent(provider, fake_engine)


# ---------------------------------------------------------------------------
# 1. Context is included in the model prompt
# ---------------------------------------------------------------------------

def test_context_included_in_prompt():
    with tempfile.TemporaryDirectory() as root:
        _write(root, "utils.py", "def calculate_tax(amount):\n    return amount * 0.1\n")
        engine = FakeEngine()
        agent = _make_agent(root, engine)

        agent.answer("calculate_tax")

        assert "calculate_tax" in engine.last_prompt
        # The repository context block must be present
        assert "File:" in engine.last_prompt


# ---------------------------------------------------------------------------
# 2. User request is included in the prompt
# ---------------------------------------------------------------------------

def test_user_request_included_in_prompt():
    with tempfile.TemporaryDirectory() as root:
        _write(root, "a.py", "x = 1\n")
        engine = FakeEngine()
        agent = _make_agent(root, engine)

        agent.answer("how does x work?")

        assert "how does x work?" in engine.last_prompt


# ---------------------------------------------------------------------------
# 3. Model response is returned to the caller
# ---------------------------------------------------------------------------

def test_model_response_returned():
    with tempfile.TemporaryDirectory() as root:
        _write(root, "b.py", "y = 2\n")
        engine = FakeEngine(answer="Here is my explanation.")
        agent = _make_agent(root, engine)

        result = agent.answer("explain y")

        assert result == "Here is my explanation."


# ---------------------------------------------------------------------------
# 4. Empty context still allows an answer
# ---------------------------------------------------------------------------

def test_empty_context_still_answers():
    with tempfile.TemporaryDirectory() as root:
        _write(root, "c.py", "z = 3\n")
        engine = FakeEngine(answer="no context answer")
        agent = _make_agent(root, engine)

        # Query that matches nothing → context will be empty
        result = agent.answer("xyzzy_unknown_symbol_404")

        assert result == "no context answer"
        # The "File:" block should NOT appear in the prompt
        assert "File:" not in engine.last_prompt
        # The user request should still appear
        assert "xyzzy_unknown_symbol_404" in engine.last_prompt


# ---------------------------------------------------------------------------
# 5. top_k is passed to the context provider
# ---------------------------------------------------------------------------

def test_top_k_limits_context_chunks():
    with tempfile.TemporaryDirectory() as root:
        # Create several files all containing the keyword "shared"
        for i in range(5):
            _write(root, f"mod{i}.py", f"shared_{i} = {i}\n")
        engine = FakeEngine()
        agent = _make_agent(root, engine)

        agent.answer("shared", top_k=2)

        # With top_k=2 only 2 "File:" headers should appear in the prompt
        file_headers = [
            line for line in engine.last_prompt.splitlines()
            if line.startswith("File:")
        ]
        assert len(file_headers) == 2
