"""Tests for CodeSymbolExtractor."""

import pytest
from app.codebase.symbols import CodeSymbolExtractor, CodeSymbolExtractionError


@pytest.fixture
def extractor():
    return CodeSymbolExtractor()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _names(symbols, kind=None):
    if kind:
        return [s["name"] for s in symbols if s["type"] == kind]
    return [s["name"] for s in symbols]


def _by_name(symbols, name):
    return next(s for s in symbols if s["name"] == name)


# ---------------------------------------------------------------------------
# 1. Top-level function
# ---------------------------------------------------------------------------

def test_top_level_function(extractor):
    src = "def greet(name):\n    return f'Hello {name}'\n"
    symbols = extractor.extract("hello.py", src)
    assert len(symbols) == 1
    s = symbols[0]
    assert s["name"] == "greet"
    assert s["type"] == "function"
    assert s["file_path"] == "hello.py"


# ---------------------------------------------------------------------------
# 2. Class
# ---------------------------------------------------------------------------

def test_class(extractor):
    src = "class Dog:\n    pass\n"
    symbols = extractor.extract("animals.py", src)
    names = _names(symbols, "class")
    assert "Dog" in names


# ---------------------------------------------------------------------------
# 3. Method inside a class
# ---------------------------------------------------------------------------

def test_method_inside_class(extractor):
    src = (
        "class Calculator:\n"
        "    def add(self, a, b):\n"
        "        return a + b\n"
    )
    symbols = extractor.extract("calc.py", src)
    methods = [s for s in symbols if s["type"] == "method"]
    assert len(methods) == 1
    assert methods[0]["name"] == "add"
    assert methods[0]["file_path"] == "calc.py"


# ---------------------------------------------------------------------------
# 4. Multiple symbols: function + class + method
# ---------------------------------------------------------------------------

def test_multiple_symbols(extractor):
    src = (
        "def standalone():\n"
        "    pass\n"
        "\n"
        "class MyClass:\n"
        "    def method_one(self):\n"
        "        pass\n"
        "    def method_two(self):\n"
        "        pass\n"
    )
    symbols = extractor.extract("multi.py", src)

    assert _names(symbols, "function") == ["standalone"]
    assert _names(symbols, "class") == ["MyClass"]
    method_names = sorted(_names(symbols, "method"))
    assert method_names == ["method_one", "method_two"]


# ---------------------------------------------------------------------------
# 5. Non-Python file returns empty list
# ---------------------------------------------------------------------------

def test_non_python_file(extractor):
    src = "function hello() { return 'hi'; }\n"
    assert extractor.extract("script.js", src) == []
    assert extractor.extract("README.md", "# title\n") == []
    assert extractor.extract("data.txt", "some text\n") == []


# ---------------------------------------------------------------------------
# 6. Invalid Python syntax raises CodeSymbolExtractionError
# ---------------------------------------------------------------------------

def test_invalid_syntax_raises(extractor):
    src = "def broken(\n    pass\n"
    with pytest.raises(CodeSymbolExtractionError):
        extractor.extract("bad.py", src)


# ---------------------------------------------------------------------------
# 7. Correct line numbers
# ---------------------------------------------------------------------------

def test_line_numbers(extractor):
    src = (
        "# comment line 1\n"          # line 1
        "\n"                           # line 2
        "def top_func():\n"            # line 3
        "    pass\n"                   # line 4
        "\n"                           # line 5
        "class MyClass:\n"             # line 6
        "    def my_method(self):\n"   # line 7
        "        pass\n"               # line 8
    )
    symbols = extractor.extract("lines.py", src)

    assert _by_name(symbols, "top_func")["line_number"] == 3
    assert _by_name(symbols, "MyClass")["line_number"] == 6
    assert _by_name(symbols, "my_method")["line_number"] == 7


# ---------------------------------------------------------------------------
# 8. Standalone function is NOT reported as a method
# ---------------------------------------------------------------------------

def test_function_not_reported_as_method(extractor):
    src = "def utility():\n    pass\n"
    symbols = extractor.extract("util.py", src)
    assert all(s["type"] != "method" for s in symbols)


# ---------------------------------------------------------------------------
# 9. Class method is NOT reported as a top-level function
# ---------------------------------------------------------------------------

def test_method_not_reported_as_function(extractor):
    src = "class Foo:\n    def bar(self):\n        pass\n"
    symbols = extractor.extract("foo.py", src)
    assert all(s["type"] != "function" for s in symbols)
