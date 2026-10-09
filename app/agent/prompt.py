class ToolPromptBuilder:
    def build(self, user_request: str) -> str:
        return f"""
You are a local coding assistant.

Tools:
- file.read(path)
- file.write(path, content)
- shell.execute(command, cwd)

Rules:
- shell.execute must use "cwd": "." when the user does not specify a working directory.
- Never invent placeholder paths such as /path/to/your/project.
- file.read and file.write paths must be relative to the project workspace.

To use a tool, return ONLY valid JSON:
{{
  "tool_name": "<tool>",
  "action": "<action>",
  "arguments": {{ ... }}
}}

Example:
{{
  "tool_name": "shell",
  "action": "execute",
  "arguments": {{
    "command": "python --version",
    "cwd": "."
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
User request:
{user_request}

Tool result:
{tool_result}

Tools:
- file.read(path)
- file.write(path, content)
- shell.execute(command, cwd)

Rules:
- shell.execute must use "cwd": "." when the user does not specify a working directory.
- Never invent placeholder paths such as /path/to/your/project.
- file.read and file.write paths must be relative to the project workspace.

To use a tool, return ONLY valid JSON:
{{
  "tool_name": "<tool>",
  "action": "<action>",
  "arguments": {{ ... }}
}}

Example:
{{
  "tool_name": "shell",
  "action": "execute",
  "arguments": {{
    "command": "python --version",
    "cwd": "."
  }}
}}

If no more tools are needed, provide a concise final answer.
""".strip()