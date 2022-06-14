from dataclasses import dataclass
from typing import List
import regex

import orc


@dataclass
class NearMatch:
    specimen: str
    candidate: str
    edits: orc.Edits

    @classmethod
    def from_regex(cls, match: regex.Match, specimen: str):
        return cls(
            specimen=specimen,
            candidate=match.group(),
            edits=orc.Edits.from_regex(match, specimen),
        )

    def __repr__(self):
        candidate = self.candidate
        s = f"{candidate}\n"
        for edit in self.edits:
            s += " " * edit.at + edit.__class__.__name__[0] + "\n"
            candidate = edit.do(candidate)
            s += f"{candidate}\n"
        return s.rstrip()


@dataclass
class WordSpan:
    word_pos: int
    start: int
    end: int

@dataclass
class OCRNearMatch(NearMatch):
    word_spans: List[WordSpan]

    def __repr__(self):
        return super().__repr__()


def search(specimen, document):

    fuzzy_pattern = f"({specimen})" + "{s<=3,i<=3,d<=3}"
    for page in document.pages:
        text = repr(page)

        # Determine where each word starts in the text
        word_starts = {pos: pos + sum(map(len, text.split(' ')[:pos])) for pos in range(len(page.words))}

        # Determine where each word end in the text
        word_ends = {pos: start + len(page.words[pos].characters) for pos, start in word_starts.items()}

        for match in regex.finditer(
            fuzzy_pattern, text, regex.BESTMATCH#, overlapped=True
        ):

            # Determine which words belong to the match
            word_positions = range(text[:match.start()].count(' '), text[:match.end()].count(' ') + 1)

            yield OCRNearMatch(
                specimen=specimen,
                candidate=match.group(),
                edits=orc.Edits.from_regex(match, specimen),
                word_spans=[
                    WordSpan(
                        word_pos=pos,
                        start=max(word_starts[pos], match.start()) - word_starts[pos],
                        end=min(match.end(), word_ends[pos]) - word_starts[pos]
                    )
                    for pos in word_positions
                ]
            )
