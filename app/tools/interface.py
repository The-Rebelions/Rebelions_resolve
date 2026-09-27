from app.tools.request import ToolRequest


class ToolInterface:
    def create_request(
        self,
        tool_name: str,
        action: str,
        arguments: dict,
    ) -> ToolRequest:
        return ToolRequest(
            tool_name=tool_name,
            action=action,
            arguments=arguments,
        )