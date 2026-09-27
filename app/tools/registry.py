class ToolRegistryError(Exception):
    """Raised when a tool registry operation fails."""


class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name: str, tool) -> None:
        if name in self._tools:
            raise ToolRegistryError(
                f"Tool '{name}' is already registered."
            )

        self._tools[name] = tool

    def get(self, name: str):
        if name not in self._tools:
            raise ToolRegistryError(
                f"Tool '{name}' is not registered."
            )

        return self._tools[name]