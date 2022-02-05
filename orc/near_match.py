from dataclasses import dataclass
import regex

import orc


@dataclass
class NearMatch:
    specimen: str
    pattern: str
    candidate: str
    start: int
    end: int
    edits: orc.Edits

    @classmethod
    def from_regex(cls, match: regex.Match, specimen: str, pattern: str):
        return cls(
            specimen=specimen,
            pattern=pattern,
            candidate=match.group(),
            start=match.start(),
            end=match.end(),
            edits=orc.Edits.from_regex(match, specimen),
        )
