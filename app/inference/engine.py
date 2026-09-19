from pathlib import Path
import subprocess


class InferenceError(Exception):
    """Raised when local model inference fails."""


class InferenceEngine:
    def __init__(
        self,
        model_path: str,
        llama_path: str,
        context_size: int,
        max_tokens: int,
        temperature: float,
        gpu_layers: str,
    ):
        self.model_path = Path(model_path)
        self.llama_path = Path(llama_path)
        self.context_size = context_size
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.gpu_layers = gpu_layers

    def generate(self, prompt: str) -> str:
        command = [
            str(self.llama_path),
            "cli",
            "-m",
            str(self.model_path),
            "-c",
            str(self.context_size),
            "-n",
            str(self.max_tokens),
            "-ngl",
            str(self.gpu_layers),
            "--temperature",
            str(self.temperature),
            "--single-turn",
            "--simple-io",
            "--no-display-prompt",
            "-p",
            prompt,
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )
        except FileNotFoundError as error:
            raise InferenceError(
                "Inference executable was not found."
            ) from error

        except subprocess.CalledProcessError as error:
            raise InferenceError(
                f"Model inference failed with exit code {error.returncode}."
            ) from error        

        output = result.stdout

        if prompt in output:
            output = output.split(prompt, 1)[1]

        if "[ Prompt:" in output:
            output = output.split("[ Prompt:", 1)[0]

        return output.strip()