"""
Based on https://stackoverflow.com/questions/9452701/ukkonens-suffix-tree-algorithm-in-plain-english
"""
from __future__ import annotations

import time
from pathlib import Path
from random import randint
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


class SuffixString:
    string: str
    start_index: int
    end_index: int
    termination_char: str

    def __init__(self, string, start, end, termination_char):
        self.string = string
        self.start = start
        self.end = end
        self.termination_char = termination_char


class SuffixTree:
    root: SuffixNode
    total_string: str

    def __init__(self):
        self.total_string = ""
        self.strings = list()

        self.root = SuffixNode(None, None)
        self.active = Active(self.root, "", 0)
        self.remainder = 0
        self.global_idx = -1

    def _select_termination_character(self, string: str):
        some_char = None
        while not some_char:
            some_char = chr(randint(0x2980, 0x2AFF))
            found = False
            found |= some_char in self.total_string
            if found:
                some_char = None
        return some_char

    def insert_string(self, string: str):
        termination_char = self._select_termination_character(string)
        string += termination_char
        self.strings.append(
            SuffixString(
                string,
                len(self.total_string),
                len(self.total_string) + len(string),
                termination_char=termination_char,
            )
        )
        for local_idx, chr in enumerate(string):
            self.total_string += chr
            self.global_idx += 1
            self.remainder += 1
            to_link = None
            while self.remainder:
                if self.active.length == 0:
                    self.active.edge = chr
                if self.active.edge not in self.active.node.nodes:
                    self.active.node.nodes[self.active.edge] = SuffixNode(
                        start=self.global_idx, end=None
                    )

                    # Rule 2
                    if to_link:
                        to_link.suffix_link = self.active.node
                    to_link = self.active.node

                else:
                    next = self.active.node.nodes[self.active.edge]
                    edge_length = (next.end or self.global_idx + 1) - next.start
                    if self.active.length >= edge_length:
                        self.active.edge = self.total_string[next.start + edge_length]
                        self.active.length -= edge_length
                        self.active.node = next
                        continue
                    if self.total_string[next.start + self.active.length] == chr:
                        self.active.length += 1

                        # Rule 2
                        if to_link:
                            to_link.suffix_link = self.active.node
                        break

                    split_node = SuffixNode(next.start, next.start + self.active.length)
                    self.active.node.nodes[self.active.edge] = split_node
                    new_node = SuffixNode(self.global_idx, None)
                    split_node.nodes[chr] = new_node
                    next.start += self.active.length
                    split_node.nodes[self.total_string[next.start]] = next

                    # Rule 2
                    if to_link:
                        to_link.suffix_link = split_node
                    to_link = split_node

                self.remainder -= 1

                # Rule 1
                if self.active.node == self.root and self.active.length > 0:
                    self.active.edge = string[local_idx - self.remainder + 1]
                    self.active.length -= 1
                else:
                    self.active.node = self.active.node.suffix_link or self.root

    @property
    def nodes(self) -> Generator[SuffixNode, None, None]:
        to_visit = [self.root]
        while to_visit:
            node = to_visit.pop()
            yield node
            to_visit.extend(list(node.nodes.values()))

    def _get_end(self, node: SuffixNode):
        if not node.end:
            ends = [s.end for s in self.strings if s.end > node.start]
            if ends:
                return min(ends) - 1
        return node.end

    def to_dot(self, file: Path, include_suffix_links=True):
        result = "digraph { rankdir=LR;"
        for node in self.nodes:
            result += f'{hash(node)} [label="", shape=circle, height=.1, width=.1];'
            for n in node.nodes.values():
                result += f'{hash(node)} -> {hash(n)} [label="{self.total_string[n.start:self._get_end(n)]}"];'
            if include_suffix_links and node.suffix_link:
                result += f'{hash(node)} -> {hash(node.suffix_link)} [label="", style="dashed"];'
        result += "}"
        file.write_text(result)


if __name__ == "__main__":
    start = time.time()
    st = SuffixTree()
    for s in (
        "banan",
        "ananas",
        "bananas",
        "annas",
    ):
        st.insert_string(s)
    st.to_dot(Path(f"tmp.dot"))
    end = time.time()
    print(end - start)
