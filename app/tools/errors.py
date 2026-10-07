from dataclasses import dataclass


@dataclass(frozen=True)
class ToolError:
    message: str
    recoverable: bool