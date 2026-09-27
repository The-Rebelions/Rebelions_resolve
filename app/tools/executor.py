from app.tools.request import ToolRequest
from app.tools.registry import ToolRegistry


class ToolExecutionError(Exception):
    """Raised when a tool request cannot be executed."""


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, request: ToolRequest):
        tool = self.registry.get(request.tool_name)

        if request.action == "read":
            return tool.read_file(**request.arguments)

        if request.action == "write":
            return tool.write_file(**request.arguments)

        raise ToolExecutionError(
            f"Action '{request.action}' cannot be executed."
        )