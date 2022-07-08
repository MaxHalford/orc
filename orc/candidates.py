from __future__ import annotations

import dataclasses
import regex
from orc import edit, ocr


def search(
    document: ocr.Document,
    specimen,
    case_insensitive=False,
    overlapped=False,
    n_substitutions=3,
    n_insertions=3,
    n_deletes=3,
    n_total_edits=3
):

    s = n_substitutions
    i = n_insertions
    d = n_deletes
    e = n_total_edits
    fuzzy_pattern = f"({specimen})" + f"{{s<={s},i<={i},d<={d},e<={e}}}"

    for page_number, page in enumerate(document.pages):
        text = repr(page)

        # Determine where each word starts in the text
        word_starts = {pos: pos + sum(map(len, text.split(' ')[:pos])) for pos in range(len(page.words))}

        # Determine where each word end in the text
        word_ends = {pos: start + len(page.words[pos].characters) for pos, start in word_starts.items()}

        flags = regex.BESTMATCH
        if case_insensitive:
            flags |= regex.IGNORECASE

        for match in regex.finditer(
            fuzzy_pattern, text, flags=flags, overlapped=overlapped
        ):

            # Determine which words belong to the match
            word_positions = range(text[:match.start()].count(' '), text[:match.end()].count(' ') + 1)

            yield DocumentNearMatch(
                page_number=page_number,
                specimen=specimen,
                candidate=match.group(),
                edits=edit.Edits.from_regex(match, specimen),
                word_spans=[
                    WordSpan(
                        word_pos=pos,
                        start=max(word_starts[pos], match.start()) - word_starts[pos],
                        end=min(match.end(), word_ends[pos]) - word_starts[pos]
                    )
                    for pos in word_positions
                ]
            )


@dataclasses.dataclass
class WordSpan:
    word_pos: int
    start: int
    end: int


@dataclasses.dataclass
class DocumentNearMatch(edit.NearMatch):
    page_number: int
    word_spans: list[WordSpan]

    def __repr__(self):
        return super().__repr__()
