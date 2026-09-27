from app.tools.parser import ToolRequestParser
from app.tools.request import ToolRequest


class ToolAgent:
    def __init__(self):
        self.parser = ToolRequestParser()

    def parse_model_output(self, text: str) -> ToolRequest:
        return self.parser.parse(text)