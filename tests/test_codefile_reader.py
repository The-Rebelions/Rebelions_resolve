import os
import tempfile
import pytest
from app.codebase.reader import CodeFileReader, CodeFileReaderError

def test_read_normal_file():
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, "hello.py")
        content = "print('hello')"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        reader = CodeFileReader(tmp_dir)
        assert reader.read("hello.py") == content

def test_read_nested_file():
    with tempfile.TemporaryDirectory() as tmp_dir:
        nested_dir = os.path.join(tmp_dir, "src")
        os.makedirs(nested_dir)
        file_path = os.path.join(nested_dir, "app.py")
        content = "x = 42"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        reader = CodeFileReader(tmp_dir)
        assert reader.read(os.path.join("src", "app.py")) == content

def test_missing_file():
    with tempfile.TemporaryDirectory() as tmp_dir:
        reader = CodeFileReader(tmp_dir)
        with pytest.raises(CodeFileReaderError) as exc:
            reader.read("nonexistent.py")
        assert "does not exist" in str(exc.value)

def test_directory_instead_of_file():
    with tempfile.TemporaryDirectory() as tmp_dir:
        os.makedirs(os.path.join(tmp_dir, "mydir"))
        reader = CodeFileReader(tmp_dir)
        with pytest.raises(CodeFileReaderError) as exc:
            reader.read("mydir")
        assert "directory" in str(exc.value)

def test_path_traversal():
    with tempfile.TemporaryDirectory() as tmp_dir:
        # create a file outside the root (simulated by same temp dir but attempt traversal)
        outside_file = os.path.join(tmp_dir, "outside.txt")
        with open(outside_file, "w", encoding="utf-8") as f:
            f.write("outside")
        reader = CodeFileReader(tmp_dir)
        with pytest.raises(CodeFileReaderError):
            # Attempt to go up one level then into the same dir (should be blocked)
            reader.read(os.path.join("..", os.path.basename(outside_file)))

def test_invalid_utf8_content():
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, "binary.txt")
        with open(file_path, "wb") as f:
            f.write(b"\xff\xfe\xfd")
        reader = CodeFileReader(tmp_dir)
        with pytest.raises(CodeFileReaderError) as exc:
            reader.read("binary.txt")
        assert "UTF-8" in str(exc.value)
