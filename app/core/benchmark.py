import re
import time
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    prompt_tokens_per_second: float
    generation_tokens_per_second: float

class BenchmarkError(Exception):
    """Raised when benchmark timing is used incorrectly."""


class BenchmarkTimer:
    def start(self):
        self._start_time = time.perf_counter()

    def stop(self) -> float:
        if not hasattr(self, "_start_time"):
            raise BenchmarkError("Benchmark timer was not started.")

        return time.perf_counter() - self._start_time

    def tokens_per_second(self, token_count: int) -> float:
        elapsed = self.stop()

        if elapsed <= 0:
            raise BenchmarkError("Benchmark elapsed time must be greater than zero.")

        return token_count / elapsed

    def parse_llama_performance(self, output: str) -> PerformanceMetrics:
        match = re.search(
            r"\[ Prompt:\s*([\d.]+)\s*t/s \| Generation:\s*([\d.]+)\s*t/s \]",
            output,
        )

        if not match:
            raise BenchmarkError(
                "llama.cpp performance metrics were not found."
            )

        return PerformanceMetrics(
            prompt_tokens_per_second=float(match.group(1)),
            generation_tokens_per_second=float(match.group(2)),
        )