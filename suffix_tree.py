"""
Based on https://stackoverflow.com/questions/9452701/ukkonens-suffix-tree-algorithm-in-plain-english
"""
from __future__ import annotations

from pathlib import Path
from typing import Union, Dict, Generator


class SuffixNode:
    nodes: Dict[str, SuffixNode]
    start: int
    end: Union[int, None]
    suffix_link: Union[SuffixNode, None]

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.nodes = dict()
        self.suffix_link = None


class Active:
    node: SuffixNode
    edge: str
    length: int

    def __init__(self, node, edge, length):
        self.node = node
        self.edge = edge
        self.length = length


class SuffixTree:
    root: SuffixNode
    string: str

    def __init__(self):
        self.string = None
        self.root = SuffixNode(None, None)

    def insert_string(self, string: str):
        self.string = string
        remainder = 0
        active = Active(self.root, "", 0)
        for idx, chr in enumerate(string):
            remainder += 1
            to_link = None
            while remainder:
                if active.length == 0:
                    active.edge = chr
                if active.edge not in active.node.nodes:
                    active.node.nodes[active.edge] = SuffixNode(start=idx, end=None)

                    # Rule 2
                    if to_link:
                        to_link.suffix_link = active.node
                    to_link = active.node

                else:
                    next = active.node.nodes[active.edge]
                    edge_length = (next.end or idx + 1) - next.start
                    if active.length >= edge_length:
                        active.edge = string[next.start + edge_length]
                        active.length -= edge_length
                        active.node = next
                        continue
                    if string[next.start + active.length] == chr:
                        active.length += 1

                        # Rule 2
                        if to_link:
                            to_link.suffix_link = active.node
                        break

                    split_node = SuffixNode(next.start, next.start + active.length)
                    active.node.nodes[active.edge] = split_node
                    new_node = SuffixNode(idx, None)
                    split_node.nodes[chr] = new_node
                    next.start += active.length
                    split_node.nodes[string[next.start]] = next

                    # Rule 2
                    if to_link:
                        to_link.suffix_link = split_node
                    to_link = split_node

                remainder -= 1

                # Rule 1
                if active.node == self.root and active.length > 0:
                    active.edge = string[idx - remainder + 1]
                    active.length -= 1
                else:
                    active.node = active.node.suffix_link or self.root

    @property
    def nodes(self) -> Generator[SuffixNode, None, None]:
        to_visit = [self.root]
        while to_visit:
            node = to_visit.pop()
            yield node
            to_visit.extend(list(node.nodes.values()))

    def to_dot(self, file: Path):
        result = "digraph { rankdir=LR;"
        for node in self.nodes:
            result += f'{hash(node)} [label="", shape=circle, height=.1, width=.1];'
            for n in node.nodes.values():
                result += f'{hash(node)} -> {hash(n)} [label="{self.string[n.start:n.end or None]}"];'
            if node.suffix_link:
                result += f'{hash(node)} -> {hash(node.suffix_link)} [label="", style="dashed"];'
        result += "}"
        file.write_text(result)


if __name__ == "__main__":
    s = "banana and ananas#"
    st = SuffixTree()
    st.insert_string(s)
    st.to_dot(Path(f"tmp.dot"))
