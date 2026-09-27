from dataclasses import dataclass


class PermissionError(Exception):
    """Raised when a tool operation is not permitted."""


@dataclass
class PermissionPolicy:
    allow_file_read: bool = False

    def check_file_read(self) -> None:
        if not self.allow_file_read:
            raise PermissionError(
                "File read operation is not permitted."
            )