from app.tools.result import ToolResult


class ToolResultFormatter:
    def format(self, result: ToolResult) -> str:
        return (
            f"Tool: {result.tool_name}\n"
            f"Action: {result.action}\n"
            f"Success: {result.success}\n"
            f"Output:\n{result.output}"
        )