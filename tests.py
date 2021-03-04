import string

from hypothesis import given
from hypothesis import strategies as st
from hypothesis.strategies import composite

from suffix_tree import SuffixTree


@composite
def text_and_search_term(draw):
    text = draw(st.text(min_size=0, max_size=1000, alphabet=string.ascii_lowercase))
    search_term = draw(
        st.text(min_size=1, max_size=1000, alphabet=string.ascii_uppercase)
    )
    insertion_point = draw(st.integers(min_value=0, max_value=len(text)))
    return text[:insertion_point] + search_term + text[insertion_point:], search_term


@composite
def text_search_term_insertion_count(draw):
    text = draw(st.text(min_size=0, max_size=1000, alphabet=string.ascii_lowercase))
    search_term = draw(
        st.text(min_size=1, max_size=1000, alphabet=string.ascii_uppercase)
    )
    insertions = draw(st.integers(min_value=0, max_value=len(text)))
    result_text = ""

    prev_pos = 0
    insertion_points = set([insertions for _ in range(insertions)])
    for pos in sorted(insertion_points):
        result_text += text[prev_pos:pos] + search_term
        prev_pos = pos
    result_text += text[prev_pos:]

    return result_text, search_term, len(insertion_points)


def suffixes(search_term):
    for x in range(len(search_term) - 1):
        yield search_term[x:]


def test_create():
    st = SuffixTree()
    assert st is not None


@given(st.text(min_size=0, max_size=1000))
def test_insertion(string: str):
    st = SuffixTree()
    st.insert_string(string)
    assert len([node for node in st.nodes if node.end is None]) == len(string) + 2
    for suffix in suffixes(string):
        assert suffix in st


@given(st.lists(st.text(min_size=1, max_size=1000), min_size=1, max_size=100))
def test_insert_multiple(lst):
    st = SuffixTree()
    for string in lst:
        st.insert_string(string)
    assert (
        len([node for node in st.nodes if node.end is None])
        == sum(len(string) + 1 for string in lst) + 1
    )
    for suffix in suffixes(string):
        assert suffix in st


@given(text_and_search_term())
def test_contains(text_and_search_term):
    text, search_term = text_and_search_term
    st = SuffixTree()
    st.insert_string(text)
    for suffix in suffixes(search_term):
        assert suffix in st


@given(
    st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=1000),
    st.text(alphabet=string.ascii_uppercase, min_size=1, max_size=1000),
)
def test_contains_not(text, search_term):
    st = SuffixTree()
    st.insert_string(text)
    assert search_term not in st


@given(text_search_term_insertion_count())
def test_occurrances(text_search_term_insertion_count):
    text, search_term, insertion_count = text_search_term_insertion_count
    st = SuffixTree()
    st.insert_string(text)
    assert st.occurrances(search_term) == insertion_count
