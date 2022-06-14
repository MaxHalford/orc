import os
import pathlib
import json
from google.cloud import vision
import abc
import dataclasses
from typing import Any, List
import dataclasses_json

@dataclasses.dataclass
class Point(dataclasses_json.DataClassJsonMixin):
    x: float
    y: float


@dataclasses.dataclass
class BoundingBox(dataclasses_json.DataClassJsonMixin):
    top_left: Point
    bottom_right: Point


@dataclasses.dataclass
class Character(dataclasses_json.DataClassJsonMixin):
    value: str
    bounding_box: BoundingBox
    confidence: float


@dataclasses.dataclass
class Word(dataclasses_json.DataClassJsonMixin):
    characters: List[Character]

    def __repr__(self):
        return "".join(char.value for char in self.characters)


@dataclasses.dataclass
class Page(dataclasses_json.DataClassJsonMixin):
    words: List[Word]

    def __repr__(self):
        return " ".join(map(repr, self.words))


@dataclasses.dataclass
class Document(dataclasses_json.DataClassJsonMixin):
    pages: List[Page]

    def __repr__(self):
        return "\n\n".join(map(repr, self.pages))


class OCR(abc.ABC):

    @property
    def cache_dir(self):
        """The location where documents are cached."""
        directory = os.environ.get("ORC_CACHE_DIR", pathlib.Path.home() / "orc_cache")
        directory = pathlib.Path(directory) / self.__class__.__name__.lower()
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @abc.abstractmethod
    def _read(self, content: bytes) -> Any:
        ...

    @abc.abstractmethod
    def _translate(self, raw: Any) -> Document:
        ...

    def __call__(self, content=None, key=None):
        if key:
            cache_key = (self.cache_dir / key).with_suffix(".json")
            if cache_key.exists():
                return Document.from_json(cache_key.read_text())

        if content is None:
            raise ValueError("content has to be provided if no valid key is provided")

        raw = self._read(content)
        document = self._translate(raw)

        if key:
            cache_key = (self.cache_dir / key).with_suffix(".json")
            with open(cache_key, "w") as f:
                json.dump(document.to_dict(), f, indent=4, sort_keys=True)

        return document



class GCPVision(OCR):

    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/max.halford/projects/orc/service_account.json"
        self.client = vision.ImageAnnotatorClient()

    def _read(self, content):
        image = vision.Image(content=content)
        raw = self.client.document_text_detection(image=image)
        return raw

    def _translate(self, raw):

        document = Document(pages=[])

        for p in raw.full_text_annotation.pages:
            page = Page(words=[])
            document.pages.append(page)

            for b in p.blocks:
                for par in b.paragraphs:
                    for w in par.words:
                        word = Word(characters=[])
                        page.words.append(word)

                        for s in w.symbols:
                            character = Character(
                                value=s.text,
                                # Google Cloud Vision orders points clockwise starting at the top-left.
                                # The top-left is relative to the position of the character as if the page
                                # were straight. In other, the top-left coordinate is correct even if the
                                # page is rotated.
                                bounding_box=BoundingBox(
                                    top_left=Point(
                                        x=s.bounding_box.vertices[0].x,
                                        y=s.bounding_box.vertices[0].y
                                    ),
                                    bottom_right=Point(
                                        x=s.bounding_box.vertices[2].x,
                                        y=s.bounding_box.vertices[2].y
                                    )
                                ),
                                confidence=s.confidence
                            )
                            word.characters.append(character)

        return document

