from dataclasses import dataclass


@dataclass(frozen=True)
class ToolResult:
    tool_name: str
    action: str
    success: bool
    output: str