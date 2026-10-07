from app.tools.request import ToolRequest
from app.tools.registry import ToolRegistry
from app.tools.validation import ToolRequestValidator
from app.tools.result import ToolResult
from app.tools.errors import ToolError
from app.tools.permissions import PermissionError


class ToolExecutionError(Exception):
    """Raised when a tool request cannot be executed."""
    def __init__(self,error: ToolError):
        self.error = error
        super().__init__(error.message)


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.validator = ToolRequestValidator(registry)

    def execute(self, request: ToolRequest) -> ToolResult:
        try:
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
                ToolError(
                    message=f"Action '{request.action}' cannot be executed.",
                    recoverable=False,
                )
            )

        except ToolExecutionError:
            raise
        except PermissionError as error:
            raise ToolExecutionError(
                ToolError(
                    message=f"Tool '{request.tool_name}' execution failed: {error}",
                    recoverable=False,
                )
            ) from error
        except Exception as error:
            raise ToolExecutionError(
                ToolError(
                    message=f"Tool '{request.tool_name}' execution failed: {error}",
                    recoverable=True,
                )
            ) from error