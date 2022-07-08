from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import regex


class Edit(ABC):
    @abstractmethod
    def do(self, s: str) -> str:
        ...


@dataclass
class Substitution(Edit):
    at: int
    old: str
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
    old: str
    at: int

    def do(self, s: str) -> str:
        return s[: self.at] + s[self.at + 1 :]


@dataclass
class Edits(Edit):
    substitutions: list[Substitution] = field(default_factory=list)
    insertions: list[Insertion] = field(default_factory=list)
    deletions: list[Deletion] = field(default_factory=list)

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

    def __neg__(self):
        return Edits(
            substitutions=[
                Substitution(
                    at=s.at
                    + sum(1 for i in self.insertions if i.at < s.at)
                    - sum(1 for d in self.deletions if d.at < s.at),
                    old=s.new,
                    new=s.old,
                )
                for s in self.substitutions
            ],
            insertions=[Insertion(at=d.at, new=d.old) for d in self.deletions],
            deletions=[Deletion(at=i.at, old=i.new) for i in self.insertions],
        )

    @classmethod
    def from_regex(cls, match: regex.Match, specimen: str):
        return cls(
            substitutions=[
                Substitution(
                    at=at - match.start(),
                    old=match.group()[at - match.start()],
                    new=specimen[
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
                    at=at - match.start(),
                    new=specimen[
                        at
                        - match.start()
                        - sum(1 for x in match.fuzzy_changes[1] if x < at)
                    ],
                )
                for at in match.fuzzy_changes[2]
            ],
            deletions=[
                Deletion(
                    at=at
                    - match.start()
                    + sum(1 for x in match.fuzzy_changes[2] if x < at),
                    old=match.group()[at - match.start()],
                )
                for at in match.fuzzy_changes[1]
            ],
        )


@dataclass
class NearMatch:
    specimen: str
    candidate: str
    edits: Edits

    @classmethod
    def from_regex(cls, match: regex.Match, specimen: str):
        return cls(
            specimen=specimen,
            candidate=match.group(),
            edits=Edits.from_regex(match, specimen),
        )

    def __repr__(self):
        candidate = self.candidate
        s = f"{candidate}\n"
        for edit in self.edits:
            s += " " * edit.at + edit.__class__.__name__[0] + "\n"
            candidate = edit.do(candidate)
            s += f"{candidate}\n"
        return s.rstrip()
