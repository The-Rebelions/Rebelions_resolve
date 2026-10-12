import pytest
from app.codebase.retriever import CodeChunk, CodebaseRetriever, CodebaseRetrieverError

# Helper to create chunks

def make_chunk(path, text):
    return CodeChunk(path, text)


def test_exact_keyword_match():
    chunks = [make_chunk('a.py', 'def foo(): pass'), make_chunk('b.py', 'def bar(): pass')]
    retriever = CodebaseRetriever(chunks)
    result = retriever.search('foo')
    assert len(result) == 1
    assert result[0].path == 'a.py'


def test_case_insensitive_matching():
    chunks = [make_chunk('a.py', 'def Foo(): pass')]
    retriever = CodebaseRetriever(chunks)
    result = retriever.search('foo')
    assert result[0].path == 'a.py'


def test_multiple_keyword_scoring():
    chunks = [
        make_chunk('a.py', 'foo bar baz'),
        make_chunk('b.py', 'foo qux'),
        make_chunk('c.py', 'bar baz'),
    ]
    retriever = CodebaseRetriever(chunks)
    result = retriever.search('foo bar')
    # a.py matches both terms (score 2), b.py matches one (score 1)
    assert [c.path for c in result] == ['a.py', 'b.py', 'c.py']


def test_descending_relevance_order():
    chunks = [
        make_chunk('a.py', 'alpha beta'),
        make_chunk('b.py', 'beta'),
        make_chunk('c.py', 'alpha'),
    ]
    retriever = CodebaseRetriever(chunks)
    result = retriever.search('alpha beta')
    # a.py matches both (2), b.py and c.py each match one (1). Order b then c because of original order.
    assert [c.path for c in result] == ['a.py', 'b.py', 'c.py']


def test_deterministic_order_for_equal_scores():
    chunks = [
        make_chunk('a.py', 'foo'),
        make_chunk('b.py', 'foo'),
        make_chunk('c.py', 'bar'),
    ]
    retriever = CodebaseRetriever(chunks)
    result = retriever.search('foo')
    # a.py and b.py have same score; should preserve original order a then b.
    assert [c.path for c in result] == ['a.py', 'b.py']


def test_empty_query_returns_empty():
    chunks = [make_chunk('a.py', 'something')]
    retriever = CodebaseRetriever(chunks)
    assert retriever.search('') == []
    assert retriever.search('   ') == []


def test_invalid_top_k():
    chunks = []
    retriever = CodebaseRetriever(chunks)
    with pytest.raises(CodebaseRetrieverError):
        retriever.search('test', top_k=0)
    with pytest.raises(CodebaseRetrieverError):
        retriever.search('test', top_k=-1)


def test_query_with_no_matches():
    chunks = [make_chunk('a.py', 'foo'), make_chunk('b.py', 'bar')]
    retriever = CodebaseRetriever(chunks)
    assert retriever.search('baz') == []


def test_top_k_larger_than_results():
    chunks = [make_chunk('a.py', 'foo'), make_chunk('b.py', 'foo bar')]
    retriever = CodebaseRetriever(chunks)
    # Only 2 matching chunks, but ask for top_k=5
    result = retriever.search('foo', top_k=5)
    assert len(result) == 2
    assert [c.path for c in result] == ['a.py', 'b.py']
