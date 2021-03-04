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
        self._root = SuffixNode(None, None)
        self._insertion_string = None

        self._active_node = None
        self._active_edge = None
        self._active_length = None

    def insert(self, string):
        assert isinstance(string, str)
        active_node = self._root
        active_edge = ""
        active_length = 0
        remainder = 1

        for idx, char in enumerate(string):
            if active_edge:
                node = active_node.edges[active_edge]
                if string[node.start + active_length] == char:
                    active_length += 1
                    remainder += 1
            elif char in active_node.edges:
                active_edge += char
                active_length = 1
                remainder += 1
            else:
                active_node.edges[char] = SuffixNode(idx, None)

        pass  # Breakpoint

    def _edge_of(self, start, end):
        return start, end


if __name__ == "__main__":
    st = SuffixTree()
    st.insert("abcab")
