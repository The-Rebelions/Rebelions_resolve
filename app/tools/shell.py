from pathlib import Path
import shlex
import subprocess

from app.tools.permissions import PermissionPolicy


class ShellToolError(Exception):
    """Raised when a shell tool operation fails."""


class ShellTool:
    def __init__(self, project_root: str, permissions: PermissionPolicy):
        self.project_root = Path(project_root).resolve()
        self.permissions = permissions

    def execute(self, command: str, cwd: str = ".") -> dict:
        self.permissions.check_shell_execution()

        if not command or not command.strip():
            raise ShellToolError("Command cannot be empty.")

        resolved_cwd = (self.project_root / cwd).resolve()

        if not resolved_cwd.is_relative_to(self.project_root):
            raise ShellToolError(
                "Access denied: working directory is outside the project directory."
            )

        if not resolved_cwd.exists():
            raise ShellToolError("Working directory does not exist.")

        if not resolved_cwd.is_dir():
            raise ShellToolError("Working directory is not a directory.")

        try:
            args = shlex.split(command)
        except ValueError as error:
            raise ShellToolError(
                f"Invalid command syntax: {error}"
            ) from error

        if not args:
            raise ShellToolError("Command cannot be empty.")

        try:
            result = subprocess.run(
                args,
                cwd=str(resolved_cwd),
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as error:
            raise ShellToolError(
                f"Command executable not found: {error}"
            ) from error
        except OSError as error:
            raise ShellToolError(
                f"Failed to execute command: {error}"
            ) from error
        except subprocess.SubprocessError as error:
            raise ShellToolError(
                f"Subprocess execution failed: {error}"
            ) from error

        return {
            "command": command,
            "cwd": str(resolved_cwd),
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
