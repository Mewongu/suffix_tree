"""
Based on https://stackoverflow.com/questions/9452701/ukkonens-suffix-tree-algorithm-in-plain-english
"""
from __future__ import annotations

from functools import total_ordering
from pathlib import Path
from random import randint
from typing import Union, Dict, Generator, Tuple


@total_ordering
class StringId:
    id: int

    def __init__(self, id: int):
        self.id = id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id})"

    def __eq__(self, other):
        return self.id == other.id

    def __le__(self, other):
        return self.id < other.id


class SuffixNode:
    nodes: Dict[str, SuffixNode]
    start: int
    end: Union[int, None]
    suffix_link: Union[SuffixNode, None]
    parent: Union[SuffixNode, None]

    def __init__(self, start: int, end: int, parent: SuffixNode):
        self.start = start
        self.end = end
        self.nodes = dict()
        self.suffix_link = None
        self.parent = parent

    def iter_leaves(self) -> Generator[SuffixNode, None, None]:
        to_visit = [self]
        while to_visit:
            node = to_visit.pop()
            if node.end is None:
                yield node
            else:
                to_visit.extend([n for n in node.nodes.values()])


class Active:
    node: SuffixNode
    edge: str
    length: int

    def __init__(self, node: SuffixNode, edge: str, length: int):
        self.node = node
        self.edge = edge
        self.length = length


class SuffixString:
    id: StringId
    string: str
    start_index: int
    end_index: int
    termination_char: str

    def __init__(
        self, id: StringId, string: str, start: int, end: int, termination_char: str
    ):
        self.id = id
        self.string = string
        self.start = start
        self.end = end
        self.termination_char = termination_char

    @property
    def length(self) -> int:
        return self.end - self.start - 1


class SuffixTree:
    root: SuffixNode
    total_string: str

    def __init__(self):
        self.total_string = ""
        self.strings = dict()

        self.root = SuffixNode(None, None, None)
        self.active = Active(self.root, "", 0)
        self.remainder = 0
        self.global_idx = -1

    @property
    def nodes(self) -> Generator[SuffixNode, None, None]:
        to_visit = [self.root]
        while to_visit:
            node = to_visit.pop()
            yield node
            to_visit.extend(list(node.nodes.values()))

    def insert_string(self, string: str):
        termination_char = self._select_termination_character(string)
        string += termination_char
        suffix_string = SuffixString(
            StringId(len(self.strings) + 0xBEEF),
            string,
            len(self.total_string),
            len(self.total_string) + len(string),
            termination_char=termination_char,
        )
        self.strings[suffix_string.id] = suffix_string
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
                        start=self.global_idx, end=None, parent=self.active.node
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

                    split_node = SuffixNode(
                        next.start,
                        next.start + self.active.length,
                        parent=self.active.node,
                    )
                    self.active.node.nodes[self.active.edge] = split_node
                    leaf = SuffixNode(self.global_idx, None, parent=split_node)
                    split_node.nodes[chr] = leaf
                    next.start += self.active.length
                    split_node.nodes[self.total_string[next.start]] = next
                    next.parent = split_node

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
        return suffix_string.id

    def get_string(self, string_id: StringId) -> SuffixString:
        return self.strings[string_id]

    def _select_termination_character(self, string: str):
        some_char = None
        while not some_char:
            some_char = chr(randint(0x2980, 0x2AFF))
            found = False
            found |= some_char in self.total_string
            found |= some_char in string
            if found:
                some_char = None
        return some_char

    def _get_string_for_total_index(self, index: int) -> SuffixString:
        return min(
            [s for s in self.strings.values() if s.end > index], key=lambda x: x.end
        )

    def _get_end(self, node: SuffixNode) -> Union[int, None]:
        if not node.end:
            suffix_string = self._get_string_for_total_index(node.start)
            return suffix_string.end - 1
        return node.end

    def find_all(self, string: str) -> Generator[Tuple[StringId, int], None, None]:
        active = self._traverse(string)
        if not active:
            return None
        node = active.node
        if active.edge:
            node = node.nodes[active.edge]
        for node in node.iter_leaves():
            suffix_string = self._get_string_for_total_index(node.start)
            distance = 0
            while node.start is not None:
                distance += self._get_edge_length(node)
                node = node.parent
            yield suffix_string, suffix_string.length - distance

    def _get_edge_length(self, node: SuffixNode) -> int:
        return self._get_end(node) - node.start

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

    def _traverse(self, string) -> Union[Active, None]:
        active = Active(self.root, "", 0)
        active.node = self.root
        active.length = 0
        active.edge = ""

        for c in string:
            if active.edge:
                if (
                    c
                    != self.total_string[
                        active.node.nodes[active.edge].start + active.length
                    ]
                ):
                    return None
                active.length += 1

            else:
                active.edge = c
                active.length = 1
                if active.edge not in active.node.nodes:
                    return None
            edge_node = active.node.nodes[active.edge]
            if edge_node.end == edge_node.start + active.length:
                active.node = edge_node
                active.edge = ""
        return active

    def __contains__(self, string: str) -> bool:
        return self._traverse(string) is not None

    def occurrences(self, string: str) -> int:
        active = self._traverse(string)
        if not active:
            return 0
        node = active.node
        if active.edge:
            node = node.nodes[active.edge]
        count = 0

        to_visit = [node]
        while to_visit:
            node = to_visit.pop()
            if node.end is None:
                count += 1
            to_visit.extend(node.nodes.values())
        return count


if __name__ == "__main__":
    import time

    start = time.time()
    st = SuffixTree()
    for s in (
        "banan",
        "ananas",
        "aabbcc",
    ):
        st.insert_string(s)
    st.to_dot(Path(f"tmp.dot"))
