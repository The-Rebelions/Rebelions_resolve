import subprocess

import psutil


class ResourceMonitor:
    def get_memory_info(self) -> dict:
        memory = psutil.virtual_memory()

        return {
            "total_mb": round(memory.total / (1024 * 1024)),
            "available_mb": round(memory.available / (1024 * 1024)),
            "used_percent": memory.percent,
        }

    def get_cpu_info(self) -> dict:
        return {
            "usage_percent": psutil.cpu_percent(interval=0.5),
            "logical_cores": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False),
        }

    def get_gpu_info(self) -> dict:
        command = [
            "nvidia-smi",
            "--query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu",
            "--format=csv,noheader,nounits",
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            return {
                "available": False,
            }

        name, memory_used, memory_total, gpu_usage, temperature = (
            value.strip() for value in result.stdout.strip().split(",")
        )

        return {
            "available": True,
            "name": name,
            "memory_used_mb": int(memory_used),
            "memory_total_mb": int(memory_total),
            "usage_percent": int(gpu_usage),
            "temperature_c": int(temperature),
        }

    def get_snapshot(self) -> dict:
        return {
            "memory": self.get_memory_info(),
            "cpu": self.get_cpu_info(),
            "gpu":self.get_gpu_info(),
        }