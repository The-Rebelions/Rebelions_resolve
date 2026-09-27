from dataclasses import dataclass


@dataclass(frozen=True)
class ToolMetadata:
    name: str
    description: str
    requires_permission: str