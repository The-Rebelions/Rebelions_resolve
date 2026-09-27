from dataclasses import dataclass


@dataclass(frozen=True)
class ToolRequest:
    tool_name: str
    action: str
    arguments: dict