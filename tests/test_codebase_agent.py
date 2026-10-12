import os
import tempfile
import pytest
from unittest.mock import MagicMock, call

from app.codebase.indexer import CodebaseIndexer
from app.agent.codebase_context import CodebaseContextProvider
from app.agent.context_selector import CodebaseContextSelector
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
# Existing tests (unchanged)
# ---------------------------------------------------------------------------

def test_context_included_in_prompt():
    with tempfile.TemporaryDirectory() as root:
        _write(root, "utils.py", "def calculate_tax(amount):\n    return amount * 0.1\n")
        engine = FakeEngine()
        agent = _make_agent(root, engine)
        agent.answer("where is calculate_tax implemented in this codebase?")
        assert "calculate_tax" in engine.last_prompt
        assert "File:" in engine.last_prompt

def test_user_request_included_in_prompt():
    with tempfile.TemporaryDirectory() as root:
        _write(root, "a.py", "x = 1\n")
        engine = FakeEngine()
        agent = _make_agent(root, engine)
        agent.answer("how does x work?")
        assert "how does x work?" in engine.last_prompt

def test_model_response_returned():
    with tempfile.TemporaryDirectory() as root:
        _write(root, "b.py", "y = 2\n")
        engine = FakeEngine(answer="Here is my explanation.")
        agent = _make_agent(root, engine)
        result = agent.answer("explain y")
        assert result == "Here is my explanation."

def test_empty_context_still_answers():
    with tempfile.TemporaryDirectory() as root:
        _write(root, "c.py", "z = 3\n")
        engine = FakeEngine(answer="no context answer")
        agent = _make_agent(root, engine)
        result = agent.answer("xyzzy_unknown_symbol_404")
        assert result == "no context answer"
        assert "File:" not in engine.last_prompt
        assert "xyzzy_unknown_symbol_404" in engine.last_prompt

def test_top_k_limits_context_chunks():
    with tempfile.TemporaryDirectory() as root:
        for i in range(5):
            _write(root, f"mod{i}.py", f"shared_{i} = {i}\n")
        engine = FakeEngine()
        agent = _make_agent(root, engine)
        agent.answer("find shared in this codebase", top_k=2)
        file_headers = [line for line in engine.last_prompt.splitlines() if line.startswith("File:")]
        assert len(file_headers) == 2

# ---------------------------------------------------------------------------
# Integration-unit tests: CodebaseContextSelector + CodebaseAgent
# ---------------------------------------------------------------------------

def test_selector_triggers_context_retrieval_not_yet_integrated():
    """Integration-unit test: selector.needs_context() is True for a codebase request.

    The current CodebaseAgent constructor does NOT accept a selector parameter,
    so this test documents the intended integration contract and confirms
    that, without a selector guard, get_context() is always called.
    """
    selector = CodebaseContextSelector()
    request = "Where is the configuration loaded in this project?"

    # Real selector must classify this as needing codebase context.
    assert selector.needs_context(request) is True

    # --- MagicMock objects ---
    context_provider = MagicMock()
    context_provider.get_context.return_value = "config.py contains load_config"
    inference_engine = MagicMock()
    inference_engine.generate.return_value = (
        "The configuration is loaded by load_config.",
        None,
    )

    # CodebaseAgent does NOT yet support a selector in its constructor.
    agent = CodebaseAgent(context_provider, inference_engine)
    result = agent.answer(request)

    # Without selector integration the provider is always consulted.
    context_provider.get_context.assert_called_once_with(request, top_k=5)

    # The returned context must reach the inference engine's prompt.
    prompt_used = inference_engine.generate.call_args[0][0]
    assert "config.py contains load_config" in prompt_used
    assert request in prompt_used

    # Agent returns only the model's text, not the raw tuple.
    assert result == "The configuration is loaded by load_config."


def test_selector_skips_context_for_general_question():
    """Integration-unit test: selector.needs_context() is False for a general question.

    A thin local subclass simulates the intended selector integration so we can
    verify that context_provider.get_context() is never called for general
    questions, without modifying any production file.
    """
    selector = CodebaseContextSelector()
    request = "Explain Python decorators"

    # Real selector must classify this as NOT needing codebase context.
    assert selector.needs_context(request) is False

    # --- MagicMock objects ---
    context_provider = MagicMock()
    inference_engine = MagicMock()
    inference_engine.generate.return_value = ("Python decorators modify functions.", None)

    # Thin wrapper that gates context retrieval on the selector.
    class AgentWithSelector(CodebaseAgent):
        def __init__(self, sel, provider, engine):
            super().__init__(provider, engine)
            self._selector = sel

        def answer(self, user_request: str, top_k: int = 5) -> str:
            if self._selector.needs_context(user_request):
                context = self._context_provider.get_context(user_request, top_k=top_k)
            else:
                context = ""
            if context:
                prompt = self.PROMPT_TEMPLATE.format(
                    context=context, user_request=user_request
                )
            else:
                prompt = self.NO_CONTEXT_TEMPLATE.format(user_request=user_request)
            result = self._engine.generate(prompt)
            return result[0] if isinstance(result, tuple) else result

    agent = AgentWithSelector(selector, context_provider, inference_engine)
    result = agent.answer(request)

    # get_context must NEVER be called for a general question.
    context_provider.get_context.assert_not_called()

    # The prompt must not contain the "File:" context block marker.
    prompt_used = inference_engine.generate.call_args[0][0]
    assert "File:" not in prompt_used
    assert request in prompt_used

    assert result == "Python decorators modify functions."

