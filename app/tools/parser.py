import contextlib
import json

from app.tools.request import ToolRequest


class ToolRequestParseError(Exception):
    """Raised when model output cannot be parsed as a tool request."""


class ToolRequestParser:
    def parse(self, text: str) -> ToolRequest:
        text = text.strip()

        # Remove markdown code block markers if present
        with contextlib.suppress(IndexError):
            if text.startswith("```json") and text.endswith("```"):
                text = text[7:-3].strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as error:
            raise ToolRequestParseError(
                "Model output is not valid JSON."
            ) from error

        if not isinstance(data, dict):
            raise ToolRequestParseError(
                "Tool request must be a JSON object."
            )

        try:
            return ToolRequest(
                tool_name=data["tool_name"],
                action=data["action"],
                arguments=data["arguments"],
            )
        except KeyError as error:
            raise ToolRequestParseError(
                f"Missing required field: {error.args[0]}"
            ) from error
    