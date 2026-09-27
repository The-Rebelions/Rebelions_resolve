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