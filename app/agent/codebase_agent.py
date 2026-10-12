from app.agent.codebase_context import CodebaseContextProvider


class CodebaseAgent:
    """Answer user requests by combining codebase context with local model inference.

    Parameters
    ----------
    context_provider : CodebaseContextProvider
        Provider used to retrieve relevant code chunks from the indexed project.
    inference_engine : InferenceEngine-compatible object
        Any object exposing a ``generate(prompt: str)`` method that returns
        ``(answer: str, performance)``.  The real ``InferenceEngine`` and lightweight
        fakes/mocks both satisfy this interface.
    """

    PROMPT_TEMPLATE = (
        "You are a local coding assistant.\n\n"
        "Use the following repository context when relevant:\n\n"
        "{context}\n\n"
        "User request:\n"
        "{user_request}\n\n"
        "Answer the user directly. Do not output tool JSON."
    )

    NO_CONTEXT_TEMPLATE = (
        "You are a local coding assistant.\n\n"
        "User request:\n"
        "{user_request}\n\n"
        "Answer the user directly. Do not output tool JSON."
    )

    def __init__(self, context_provider: CodebaseContextProvider, inference_engine):
        self._context_provider = context_provider
        self._engine = inference_engine

    def answer(self, user_request: str, top_k: int = 5) -> str:
        """Retrieve relevant context and generate an answer for *user_request*.

        Parameters
        ----------
        user_request : str
            The user''s question or coding request.
        top_k : int, optional
            Maximum number of code chunks to include in the context. Default is 5.

        Returns
        -------
        str
            The model''s answer text.
        """
        context = self._context_provider.get_context(user_request, top_k=top_k)

        if context:
            prompt = self.PROMPT_TEMPLATE.format(
                context=context,
                user_request=user_request,
            )
        else:
            prompt = self.NO_CONTEXT_TEMPLATE.format(user_request=user_request)

        result = self._engine.generate(prompt)

        # InferenceEngine.generate returns (output, performance); support both
        # the real engine (tuple) and simple fakes (plain string).
        if isinstance(result, tuple):
            answer, _ = result
        else:
            answer = result

        return answer
