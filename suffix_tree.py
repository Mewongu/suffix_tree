"""
Based on https://stackoverflow.com/questions/9452701/ukkonens-suffix-tree-algorithm-in-plain-english
"""
from __future__ import annotations
from typing import Union, Dict


class SuffixNode:
    start: int
    end: Union[int, None]
    edges: Dict[str, SuffixNode]

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.edges = dict()
class SuffixTree:
    def __init__(self):
        self.root = dict()
        self._insertion_string = None

    def insert(self, string):
        assert isinstance(string, str)
        self._insertion_string = string

        for idx, char in enumerate(string):
            self.root[char] = SuffixNode(idx, None)

    def _edge_of(self, start, end):
        return start, end


if __name__ == "__main__":
    st = SuffixTree()
    st.insert("abc")
    pass
