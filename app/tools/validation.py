import __main__
from app.tools.request import ToolRequest


class ToolRequestValidationError(Exception):
    """Raised when a tool request is invalid."""


class ToolRequestValidator:
    def validate(self, request: ToolRequest) -> None:
        if not request.tool_name.strip():
            raise ToolRequestValidationError(
                "Tool name cannot be empty."
            )

        if not request.action.strip():
            raise ToolRequestValidationError(
                "Tool action cannot be empty."
            )

        if not isinstance(request.arguments, dict):
            raise ToolRequestValidationError(
                "Tool arguments must be a dictionary."
            )