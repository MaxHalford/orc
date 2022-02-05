from dataclasses import dataclass, field
from typing import List

import regex


@dataclass
class Edit:
    """

    Parameters
    ----------
    at
        Location in the candidate.

    """

    at: int


@dataclass
class Substitution(Edit):
    new: str

    def do(self, s: str) -> str:
        return s[: self.at] + self.new + s[self.at + 1 :]


@dataclass
class Insertion(Edit):
    new: str

    def do(self, s: str) -> str:
        return s[: self.at] + self.new + s[self.at :]


@dataclass
class Deletion(Edit):
    def do(self, s: str) -> str:
        return s[: self.at] + s[self.at + 1 :]


@dataclass
class Edits:
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

    def do_iter(self, s):
        for edit in self:
            yield (s := edit.do(s))

    def do(self, s):
        for s in self.do_iter(s):
            pass
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
                Insertion(at - match.start(), specimen[at - match.start()])
                for at in match.fuzzy_changes[2]
            ],
            deletions=[Deletion(at - match.start()) for at in match.fuzzy_changes[1]],
        )

    def invert(self, target: str):
        return Edits(
            substitutions=self.substitutions,
            insertions=[
                Insertion(deletion.at, target[deletion.at - len(self.deletions)])
                for deletion in self.deletions
            ],
            deletions=[Deletion(insertion.at) for insertion in self.insertions],
        )
