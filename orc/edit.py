from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

import regex


class Edit(ABC):
    @abstractmethod
    def do(self, s: str) -> str:
        ...


@dataclass
class Substitution(Edit):
    at: int
    new: str

    def do(self, s: str) -> str:
        return s[: self.at] + self.new + s[self.at + 1 :]


@dataclass
class Insertion(Edit):
    at: int
    new: str

    def do(self, s: str) -> str:
        return s[: self.at] + self.new + s[self.at :]


@dataclass
class Deletion(Edit):
    at: int

    def do(self, s: str) -> str:
        return s[: self.at] + s[self.at + 1 :]


@dataclass
class Edits(Edit):
    substitutions: List[Substitution] = field(default_factory=list)
    insertions: List[Insertion] = field(default_factory=list)
    deletions: List[Deletion] = field(default_factory=list)

    def __post_init__(self):
        self.insertions = sorted(self.insertions, key=lambda x: x.at)
        self.deletions = sorted(self.deletions, key=lambda x: x.at, reverse=True)

    @property
    def __len__(self):
        return len(self.substitutions) + len(self.insertions) + len(self.deletions)

    def __iter__(self):
        yield from self.substitutions
        yield from self.insertions
        yield from self.deletions

    def do(self, s: str):
        for edit in self:
            s = edit.do(s)
        return s

    @classmethod
    def from_regex(cls, match: regex.Match, specimen: str):
        return cls(
            substitutions=[
                Substitution(
                    at - match.start(),
                    specimen[
                        at
                        - match.start()
                        - sum(1 for x in match.fuzzy_changes[1] if x < at)
                        + sum(1 for x in match.fuzzy_changes[2] if x < at)
                    ],
                )
                for at in match.fuzzy_changes[0]
            ],
            insertions=[
                Insertion(
                    at - match.start(),
                    specimen[
                        at
                        - match.start()
                        - sum(1 for x in match.fuzzy_changes[1] if x < at)
                    ],
                )
                for at in match.fuzzy_changes[2]
            ],
            deletions=[
                Deletion(
                    at
                    - match.start()
                    + sum(1 for x in match.fuzzy_changes[2] if x < at)
                )
                for at in match.fuzzy_changes[1]
            ],
        )
