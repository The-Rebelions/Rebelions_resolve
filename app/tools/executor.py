from app.tools.request import ToolRequest
from app.tools.registry import ToolRegistry
from app.tools.validation import ToolRequestValidator
from app.tools.result import ToolResult


class ToolExecutionError(Exception):
    """Raised when a tool request cannot be executed."""


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.validator = ToolRequestValidator(registry)

    def execute(self, request: ToolRequest) -> ToolResult:
        self.validator.validate(request)

        tool = self.registry.get(request.tool_name)

        if request.action == "read":
            output = tool.read_file(**request.arguments)
            return ToolResult(
                tool_name=request.tool_name,
                action=request.action,
                success=True,
                output=output,
            )

        if request.action == "write":
            tool.write_file(**request.arguments)
            return ToolResult(
                tool_name=request.tool_name,
                action=request.action,
                success=True,
                output="File written successfully.",
            )

        raise ToolExecutionError(
            f"Action '{request.action}' cannot be executed."
        )