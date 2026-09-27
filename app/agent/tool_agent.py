from app.tools.executor import ToolExecutor
from app.tools.parser import ToolRequestParser
from app.tools.request import ToolRequest


class ToolAgent:
    def __init__(self, executor: ToolExecutor):
        self.parser = ToolRequestParser()
        self.executor = executor

    def parse_model_output(self, text: str) -> ToolRequest:
        return self.parser.parse(text)

    def execute_model_output(self, text: str):
        request = self.parse_model_output(text)
        return self.executor.execute(request)