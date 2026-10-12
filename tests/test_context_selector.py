import pytest

from app.agent.context_selector import CodebaseContextSelector


@pytest.fixture
def selector():
    return CodebaseContextSelector()


# ---------------------------------------------------------------------------
# 1. Empty request → False
# ---------------------------------------------------------------------------

def test_empty_request(selector):
    assert selector.needs_context("") is False


def test_whitespace_only_request(selector):
    assert selector.needs_context("   ") is False


# ---------------------------------------------------------------------------
# 2. General concept question → False
# ---------------------------------------------------------------------------

def test_general_python_decorators(selector):
    assert selector.needs_context("Explain Python decorators") is False


def test_general_list_question(selector):
    assert selector.needs_context("How does a Python list work?") is False


# ---------------------------------------------------------------------------
# 3. Refers to *this project* → True
# ---------------------------------------------------------------------------

def test_this_project_reference(selector):
    assert selector.needs_context(
        "Where is the configuration loaded in this project?"
    ) is True


# ---------------------------------------------------------------------------
# 4. Bug / error in specific code → True
# ---------------------------------------------------------------------------

def test_bug_in_code(selector):
    assert selector.needs_context(
        "Find the bug in the authentication code"
    ) is True


# ---------------------------------------------------------------------------
# 5. "This function" → True
# ---------------------------------------------------------------------------

def test_this_function(selector):
    assert selector.needs_context("What does this function do?") is True


# ---------------------------------------------------------------------------
# Additional edge cases
# ---------------------------------------------------------------------------

def test_codebase_keyword(selector):
    assert selector.needs_context("Search the codebase for TODO comments") is True


def test_refactor_keyword(selector):
    assert selector.needs_context("Can you refactor this?") is True


def test_our_code_phrase(selector):
    assert selector.needs_context("Review our code for security issues") is True


def test_general_oop_question(selector):
    assert selector.needs_context("What is object-oriented programming?") is False


def test_general_algorithm_question(selector):
    assert selector.needs_context("How does quicksort work?") is False
