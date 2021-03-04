"""
Based on https://stackoverflow.com/questions/9452701/ukkonens-suffix-tree-algorithm-in-plain-english
"""
from __future__ import annotations
from typing import Union, Dict


class SuffixNode:
    start: int
    end: Union[int, None]
    edges: Dict[str, SuffixNode]
    suffix_link: Union[None, SuffixNode]

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.edges = dict()
        self.suffix_link = None


class SuffixTree:
    def __init__(self):
        self._root = SuffixNode(None, None)
        self.string = None

        self._active_node = None
        self._active_edge = None
        self._active_length = None

    def insert(self, string):
        assert isinstance(string, str)
        self.string = string
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
                else:
                    to_link = None
                    while active_edge in active_node.edges:
                        node = active_node.edges[active_edge]
                        split_node = SuffixNode(node.start + active_length, None)

                        # Check Rule 2
                        if to_link:
                            to_link.suffix_link = node

                        node.end = node.start + active_length
                        node.edges[string[node.start + active_length]] = split_node
                        node.edges[char] = SuffixNode(idx, None)
                        remainder -= 1

                        # Check Rule 1
                        if active_node == self._root:
                            if active_length:
                                active_length -= 1
                                active_edge = string[idx - active_length]

                        to_link = node
                    active_node.edges[active_edge] = SuffixNode(idx, None)
                    active_edge = ""

            elif char in active_node.edges:
                active_edge += char
                active_length = 1
                remainder += 1
            else:
                active_node.edges[char] = SuffixNode(idx, None)

        pass  # Breakpoint

    def to_string(self):
        def _to_string_helper(node, prefixes=None):
            result = ["".join(prefixes + [self.string[node.start : node.end]])]
            for node in node.edges.values():
                result.extend(
                    _to_string_helper(node, prefixes=prefixes[:-1] + ["┃", "┣"])
                )
            return result

        result = ["@"]
        for node in self._root.edges.values():
            result.extend(_to_string_helper(node, prefixes=["┣"]))
        return "\n".join(result)


if __name__ == "__main__":
    st = SuffixTree()
    st.insert("abcabx")
    print(st.to_string())
