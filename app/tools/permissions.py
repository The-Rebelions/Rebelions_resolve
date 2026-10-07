from dataclasses import dataclass


class PermissionError(Exception):
    """Raised when a tool operation is not permitted."""


@dataclass
class PermissionPolicy:
    allow_file_read: bool = False
    allow_file_write: bool = False
    allow_shell_execution: bool = False

    def check_file_read(self) -> None:
        if not self.allow_file_read:
            raise PermissionError(
                "File read operation is not permitted."
            )

    def check_file_write(self) -> None:
        if not self.allow_file_write:
            raise PermissionError(
                "File write operation is not permitted."
            )

    def check_shell_execution(self) -> None:
        if not self.allow_shell_execution:
            raise PermissionError(
                "Shell execution is not permitted."
            )