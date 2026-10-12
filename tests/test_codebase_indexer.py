import os
import pytest
from app.codebase.indexer import CodebaseIndexer, CodebaseIndexerError
from app.codebase.chunker import CodeChunker

def create_file(path, content, binary=False):
    mode = 'wb' if binary else 'w'
    with open(path, mode) as f:
        if binary:
            f.write(content)
        else:
            f.write(content)

def test_search_before_build_raises(tmp_path):
    idx = CodebaseIndexer(str(tmp_path), chunk_size=10)
    with pytest.raises(CodebaseIndexerError):
        idx.search('anything')

def test_multiple_files_indexed_and_search(tmp_path):
    # Create two python files.
    create_file(tmp_path / 'a.py', 'def foo():\n    pass')
    create_file(tmp_path / 'b.py', 'def bar():\n    pass')
    idx = CodebaseIndexer(str(tmp_path), chunk_size=5, overlap=2)
    idx.build()
    results = idx.search('foo')
    assert len(results) >= 1
    assert results[0].path == 'a.py'
    # Ensure both files are indexed (search for a term present in both files).
    create_file(tmp_path / 'c.py', 'def common():\n    pass')
    idx.build()
    all_results = idx.search('def')
    paths = {r.path for r in all_results}
    assert {'a.py', 'b.py', 'c.py'}.issubset(paths)

def test_chunking_behavior(tmp_path):
    # Long content to produce multiple chunks.
    long_text = 'abcdefghij' * 3  # 30 chars.
    create_file(tmp_path / 'long.py', long_text)
    idx = CodebaseIndexer(str(tmp_path), chunk_size=5, overlap=2)
    idx.build()
    # Retrieve all chunks for the file.
    chunks = [c for c in idx._chunks if c.path == 'long.py']
    # Use the same logic as CodeChunker for expected count.
    expected = CodeChunker(5, 2).chunk(long_text)
    assert [c.text for c in chunks] == expected

def test_unreadable_file_is_skipped(tmp_path):
    # Valid file.
    create_file(tmp_path / 'good.py', 'def hello():\n    pass')
    # Binary file with .py extension that will cause UnicodeDecodeError.
    create_file(tmp_path / 'bad.py', b'\xff\xff\xff', binary=True)
    idx = CodebaseIndexer(str(tmp_path), chunk_size=10)
    # Should not raise despite unreadable file.
    idx.build()
    # Search should return result from good.py only.
    results = idx.search('hello')
    assert len(results) == 1
    assert results[0].path == 'good.py'

# ---------------------------------------------------------------------------
# find_symbol() tests
# ---------------------------------------------------------------------------

def test_find_symbol_function(tmp_path):
    """find_symbol returns the correct descriptor for a top-level function."""
    create_file(
        tmp_path / 'config.py',
        'def load_config():\n    return {}\n',
    )
    idx = CodebaseIndexer(str(tmp_path), chunk_size=200)
    idx.build()

    results = idx.find_symbol('load_config')

    assert len(results) == 1
    sym = results[0]
    assert sym['name'] == 'load_config'
    assert sym['type'] == 'function'
    assert sym['file_path'] == 'config.py'
    assert sym['line_number'] == 1


def test_find_symbol_unknown_returns_empty(tmp_path):
    """find_symbol returns [] when the symbol does not exist."""
    create_file(tmp_path / 'mod.py', 'x = 1\n')
    idx = CodebaseIndexer(str(tmp_path), chunk_size=200)
    idx.build()

    assert idx.find_symbol('does_not_exist') == []


def test_find_symbol_class_method(tmp_path):
    """find_symbol can locate a method nested inside a class."""
    src = (
        'class MyService:\n'
        '    def process(self):\n'
        '        pass\n'
    )
    create_file(tmp_path / 'service.py', src)
    idx = CodebaseIndexer(str(tmp_path), chunk_size=200)
    idx.build()

    # Class is findable.
    classes = idx.find_symbol('MyService')
    assert len(classes) == 1
    assert classes[0]['type'] == 'class'

    # Method is findable.
    methods = idx.find_symbol('process')
    assert len(methods) == 1
    assert methods[0]['type'] == 'method'
    assert methods[0]['file_path'] == 'service.py'


def test_keyword_search_still_works_after_symbol_integration(tmp_path):
    """Existing search() behaviour is unchanged after adding symbol extraction."""
    create_file(tmp_path / 'utils.py', 'def helper():\n    return 42\n')
    idx = CodebaseIndexer(str(tmp_path), chunk_size=200)
    idx.build()

    results = idx.search('helper')
    assert len(results) >= 1
    assert any(r.path == 'utils.py' for r in results)

