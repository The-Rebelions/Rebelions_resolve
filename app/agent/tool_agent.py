
from app.agent.prompt import ToolPromptBuilder
from app.tools.executor import ToolExecutor,ToolExecutionError
from app.tools.parser import ToolRequestParser,ToolRequestParseError
from app.tools.request import ToolRequest


class ToolAgent:
    def __init__(self, executor: ToolExecutor,inference_engine):
        self.parser = ToolRequestParser()
        self.executor = executor
        self.inference_engine=inference_engine
        self.prompt_builder = ToolPromptBuilder()

    def build_prompt(self, user_request: str) -> str:
        return self.prompt_builder.build(user_request)

    def parse_model_output(self, text: str) -> ToolRequest:
        return self.parser.parse(text)

    def execute_model_output(self, text: str):
        request = self.parse_model_output(text)
        return self.executor.execute(request)
    
    def build_tool_result_prompt(
        self,
        user_request: str,
        tool_result: str,
    ) -> str:
        return self.prompt_builder.build_tool_result_prompt(
            user_request,
            tool_result,
        )
    
    def run_tool_loop(
        self,
        user_request: str,
        model_output: str,
        max_steps: int = 3,
    ):
        results = []
        current_output = model_output

        for _ in range(max_steps):
            if self.is_final_response(current_output):
                break

            try:
                result = self.execute_model_output(current_output)
            except ToolRequestParseError as error:
                return results, f"Tool request parsing failed: {error}"
            except ToolExecutionError as error:
                if error.error.recoverable:
                    return results, (
                        f"Tool execution failed, but the error is recoverable: "
                        f"{error.error.message}"
                    )

                return results, (
                    f"Tool execution failed and cannot be recovered: "
                    f"{error.error.message}"
                )

            results.append(result)

            current_output = self.generate_next_action(
                user_request,
                result,
            )

        return results,current_output

    def generate_model_output(self, prompt: str) -> str:
        response, _ = self.inference_engine.generate(prompt)
        return response

    def generate_next_action(
        self,
        user_request: str,
        tool_result,
    ) -> str:
        formatted_result = self.prompt_builder.build_tool_result_prompt(
            user_request,
            str(tool_result.output),
        )

        return self.generate_model_output(formatted_result)

    def is_final_response(self, model_output: str) -> bool:
        return not model_output.strip().startswith("{")
        