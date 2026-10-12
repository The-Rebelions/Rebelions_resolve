import tempfile
from pathlib import Path

from app.codebase.scanner import CodebaseScanner


def test_scanner():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)

        (root / "main.py").write_text("print('hello')", encoding="utf-8")
        (root / "src").mkdir()
        (root / "src" / "app.py").write_text("x = 1", encoding="utf-8")

        (root / ".git").mkdir()
        (root / ".git" / "ignored.py").write_text("x = 1", encoding="utf-8")

        (root / ".venv").mkdir()
        (root / ".venv" / "ignored.py").write_text("x = 1", encoding="utf-8")

        (root / "models").mkdir()
        (root / "models" / "ignored.py").write_text("x = 1", encoding="utf-8")

        (root / "__pycache__").mkdir()
        (root / "__pycache__" / "ignored.py").write_text("x = 1", encoding="utf-8")

        (root / "program.exe").write_bytes(b"binary")
        (root / "image.png").write_bytes(b"binary")

        (root / "binary.py").write_bytes(b"\x00\x01\x02")

        scanner = CodebaseScanner(str(root))
        result = scanner.scan()

        assert result == [
            "main.py",
            "src\\app.py",
        ]

        empty_root = root / "empty"
        empty_root.mkdir()

        assert CodebaseScanner(str(empty_root)).scan() == []

        print("CodebaseScanner tests: PASSED")


if __name__ == "__main__":
    test_scanner()
