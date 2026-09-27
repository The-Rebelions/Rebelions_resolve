from app.tools.request import ToolRequest
from app.tools.registry import ToolRegistry


class ToolRequestValidationError(Exception):
    """Raised when a tool request is invalid."""


class ToolRequestValidator:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

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

        try:
            self.registry.get(request.tool_name)
        except Exception as error:
            raise ToolRequestValidationError(
                f"Tool '{request.tool_name}' is not available."
            ) from error
            
        tool = self.registry.get(request.tool_name)
        if request.action not in tool.supported_actions():
            raise ToolRequestValidationError(
                f"Action '{request.action}' is not supported by tool '{request.tool_name}'."
            )