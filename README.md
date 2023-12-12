# orc 🧌

orc is a tool for parsing structured information from (messy) OCR outputs. This toolkit doesn't use fancy deep learning models. It focuses on simple and efficient algorithms that are practical enough to be used in battle.

## Usage

### `fuzz`: fuzzy string matching 😶‍🌫️

This modules focuses on [approximate string matching](https://www.wikiwand.com/en/Approximate_string_matching). Not only does it give the ability to calculate distances between words, it also records the operations that were performed to transform one word into another.

### `spell`: spell checking 📝

### `ocr`: optical character recognition 🔬

### `lines`: line segmentation 📏

## Development

```sh
git clone https://github.com/MaxHalford/orc
cd orc
pip install poetry
poetry install
poetry shell
pytest
```

## License

The MIT License (MIT). Please see the [license file](LICENSE) for more information.
