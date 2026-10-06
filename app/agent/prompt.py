class ToolPromptBuilder:
    def build(self, user_request: str) -> str:
        return f"""
You are a local coding assistant.

You may request tools by returning ONLY valid JSON.

Available tool:
- file
  - read: read a file inside the project workspace
  - write: write content to a file inside the project workspace

For a tool request, use exactly this format:
{{
  "tool_name": "file",
  "action": "read",
  "arguments": {{
    "path": "app/main.py"
  }}
}}

User request:
{user_request}
""".strip()

    def build_tool_result_prompt(
        self,
        user_request: str,
        tool_result: str,
    ) -> str:
        return f"""
You are a local coding assistant.

The user requested:
{user_request}

A tool was executed.

Tool result:
{tool_result}

Based on the tool result, decide what to do next.

If another tool is required, return ONLY valid JSON using this format:
{{
  "tool_name": "file",
  "action": "read",
  "arguments": {{
    "path": "app/main.py"
  }}
}}

If no more tools are required, respond with a concise final answer.
""".strip()