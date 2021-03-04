"""
Based on https://stackoverflow.com/questions/9452701/ukkonens-suffix-tree-algorithm-in-plain-english
"""
from __future__ import annotations

from pathlib import Path
from typing import Union, Dict, Iterable


class SuffixNode:
    start: int
    end: Union[int, None]
    _edges: Dict[str, SuffixNode]
    suffix_link: Union[None, SuffixNode]

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self._edges = dict()
        self.suffix_link = None

    def __setitem__(self, key, value):
        self._edges[key] = value

    def __getitem__(self, key):
        return self._edges[key]

    def __contains__(self, key):
        return key in self._edges

    @property
    def edges(self) -> Iterable[SuffixNode]:
        return self._edges.values()


class Active:
    node: SuffixNode
    edge: str
    length: int

    def __init__(self, node, edge, length):
        self.node = node
        self.edge = edge
        self.length = length


class SuffixTree:
    def __init__(self, string: str):
        self._root = SuffixNode(None, None)
        self.string = string
        act = Active(self._root, "", 0)
        remainder = 1

        for idx, char in enumerate(string):
            to_link = None
            if act.edge:
                node = act.node[act.edge]
                if string[node.start + act.length] == char:
                    act.length += 1
                    remainder += 1

                    if node.start + act.length == node.end:
                        act.node = node
                        act.edge = ""
                        act.length = 0
                else:
                    while act.edge in act.node:
                        node = act.node[act.edge]
                        split_node = SuffixNode(node.start + act.length, None)

                        # Check Rule 2
                        if to_link:
                            to_link.suffix_link = node

                        node.end = node.start + act.length
                        node[string[node.start + act.length]] = split_node
                        node[char] = SuffixNode(idx, None)
                        remainder -= 1

                        # Check Rule 1
                        if act.node == self._root:
                            if act.length:
                                act.length -= 1
                                act.edge = string[idx - act.length]
                        else:
                            # Rule 3
                            act.node = (
                                act.node.suffix_link
                                if act.node.suffix_link
                                else self._root
                            )
                        to_link = node
                    act.node[act.edge] = SuffixNode(idx, None)
                    act.edge = ""

            elif char in act.node:
                act.edge += char
                act.length = 1
                remainder += 1
            else:
                act.node[char] = SuffixNode(idx, None)

    def to_string(self):
        def _to_string_helper(node, prefixes=None):
            result = ["".join(prefixes + [self.string[node.start : node.end]])]
            for node in node.edges:
                result.extend(
                    _to_string_helper(node, prefixes=prefixes[:-1] + ["┃", "┣"])
                )
            return result

        result = ["@"]
        for node in self._root.edges:
            result.extend(_to_string_helper(node, prefixes=["┣"]))
        return "\n".join(result)

    def to_dot(self, file: Path):
        nodes_to_visit = []
        current_node = self._root
        result = "digraph { rankdir=LR;"
        while current_node:
            result += f'{hash(current_node)} [label=""]'
            nodes_to_visit.extend(list(current_node.edges))
            for node in current_node.edges:
                result += f'{hash(current_node)} -> {hash(node)} [label="{self.string[node.start:node.end or None]}"];'
            if current_node.suffix_link:
                result += f'{hash(current_node)} -> {hash(current_node.suffix_link)} [label="", style="dashed"];'

            if nodes_to_visit:
                current_node = nodes_to_visit.pop()
            else:
                current_node = None
        result += "}"
        file.write_text(result)


if __name__ == "__main__":
    s = "abcabxabcd"
    st = SuffixTree(s)
    print(st.to_string())
    st.to_dot(Path(f"{s}.dot"))
