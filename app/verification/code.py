class VerificationError(Exception):
    """Raised when generated code fails verification."""


class CodeVerifier:
    def verify_python_syntax(self, code: str) -> bool:
        try:
            compile(code, "<generated>", "exec")
        except SyntaxError as error:
            raise VerificationError(
                f"Python syntax verification failed: {error}"
            ) from error

        return True