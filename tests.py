from hypothesis import given
from hypothesis import strategies as st

from suffix_tree import SuffixTree


def test_create():
    st = SuffixTree()
    assert st is not None


@given(st.text(min_size=0, max_size=1000))
def test_insertion(string: str):
    st = SuffixTree()
    st.insert_string(string)
    assert len([node for node in st.nodes if node.end is None]) == len(string) + 2


@given(st.lists(st.text(min_size=1, max_size=1000), min_size=1, max_size=100))
def test_insert_multiple(lst):
    st = SuffixTree()
    for string in lst:
        st.insert_string(string)
    assert (
        len([node for node in st.nodes if node.end is None])
        == sum(len(string) + 1 for string in lst) + 1
    )
