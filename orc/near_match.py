from dataclasses import dataclass
import regex

import orc


@dataclass
class NearMatch:
    specimen: str
    candidate: str
    start: int
    end: int
    edits: orc.Edits

    @classmethod
    def from_regex(cls, match: regex.Match, specimen: str):
        return cls(
            specimen=specimen,
            candidate=match.group(),
            start=match.start(),
            end=match.end(),
            edits=orc.Edits.from_regex(match, specimen),
        )

    def __repr__(self):
        candidate = self.candidate
        s = f"{candidate}\n"
        for edit in self.edits:
            s += " " * edit.at + edit.__class__.__name__[0] + "\n"
            candidate = edit.do(candidate)
            s += f"{candidate}\n"
        return s
