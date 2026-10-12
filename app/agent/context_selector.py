"""Lightweight heuristic to decide if a user request needs codebase context."""


class CodebaseContextSelector:
    """Decide whether a user request is likely to require repository context.

    The decision is entirely keyword/phrase‑based — no LLM, no external
    dependencies, fully deterministic.

    Classification rules (evaluated in order):
    1. Empty / whitespace‑only  → **False**
    2. Contains a *strong phrase* that explicitly references this codebase
       (e.g. "this project", "this function", "the repository") → **True**
    3. Contains a *strong keyword* that strongly implies working with
       existing code (e.g. "bug", "error", "implementation", "config") → **True**
    4. Everything else → **False** (treat as a general programming question)
    """

    # Phrases that unambiguously refer to the user''s own project/code.
    _STRONG_PHRASES: tuple[str, ...] = (
        "this project",
        "this codebase",
        "this repository",
        "this repo",
        "this function",
        "this method",
        "this class",
        "this module",
        "this file",
        "this code",
        "this script",
        "our project",
        "our codebase",
        "our repository",
        "our repo",
        "our code",
        "the codebase",
        "the repository",
        "the repo",
        "the project",
        "in the code",
        "in our code",
    )

    # Single words that strongly suggest working with existing code rather than
    # asking a general language/concept question.
    _STRONG_KEYWORDS: tuple[str, ...] = (
        "bug",
        "bugs",
        "error",
        "errors",
        "exception",
        "exceptions",
        "traceback",
        "stacktrace",
        "implementation",
        "implementations",
        "refactor",
        "refactoring",
        "codebase",
        "repository",
        "repo",
        "existing",
        "config",
        "configuration",
        "settings",
    )

    def needs_context(self, user_request: str) -> bool:
        """Return True if *user_request* is likely to need codebase context.

        Parameters
        ----------
        user_request : str
            The raw user input string.
        """
        if not user_request or not user_request.strip():
            return False

        lowered = user_request.lower()

        for phrase in self._STRONG_PHRASES:
            if phrase in lowered:
                return True

        # Tokenise to avoid substring false‑positives (e.g. "error" inside
        # "decorators").  Keep only alphabetic tokens for simplicity.
        tokens = set(
            token.strip("?.,!;:'\"()")
            for token in lowered.split()
        )
        for keyword in self._STRONG_KEYWORDS:
            if keyword in tokens:
                return True

        return False
