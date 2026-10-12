"""
Integration test: real CodebaseAgent with the Qwen inference engine.

This test DOES NOT mock any component — it exercises the full pipeline:
    CodebaseIndexer -> CodebaseContextProvider -> CodebaseAgent -> InferenceEngine

Run with:
    python -m pytest tests/test_real_codebase_agent.py -v -s
"""

import pytest

from app.core.config import load_config, PROJECT_ROOT
from app.inference.engine import InferenceEngine
from app.codebase.indexer import CodebaseIndexer
from app.agent.codebase_context import CodebaseContextProvider
from app.agent.codebase_agent import CodebaseAgent


@pytest.fixture(scope="module")
def agent():
    """Build the full agent pipeline from config.yaml — once per test session."""
    cfg = load_config()

    engine = InferenceEngine(
        model_path=str(PROJECT_ROOT / cfg["model"]["path"]),
        llama_path=cfg["runtime"]["executable"],
        context_size=cfg["model"]["context_size"],
        max_tokens=cfg["model"]["max_tokens"],
        temperature=cfg["model"]["temperature"],
        gpu_layers=cfg["runtime"]["gpu_layers"],
    )

    indexer = CodebaseIndexer(
        project_root=str(PROJECT_ROOT),
        chunk_size=400,
        overlap=40,
    )
    indexer.build()

    provider = CodebaseContextProvider(indexer)
    return CodebaseAgent(provider, engine)


def test_real_codebase_agent_answers(agent):
    """The model must return a non-empty string for a real codebase question."""
    query = "Where is the codebase configuration loaded?"

    response = agent.answer(query)

    print(f"\n=== Model response ===\n{response}\n=====================")
    assert isinstance(response, str)
    assert len(response.strip()) > 0
