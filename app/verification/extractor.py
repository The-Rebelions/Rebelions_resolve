import re


class CodeExtractionError(Exception):
    """Raised when Python code cannot be extracted from model output."""


class CodeExtractor:
    def extract_python(self, text: str) -> str:
        match = re.search(
            r"```python\s*(.*?)```",
            text,
            re.DOTALL | re.IGNORECASE,
        )

        if match:
            return match.group(1).strip()

        if "```" in text:
            raise CodeExtractionError(
                "A code block was found, but it is not marked as Python."
            )

        return text.strip()