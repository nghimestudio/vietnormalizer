# Vietnamese Text Normalizer

[![PyPI version](https://badge.fury.io/py/vietnormalizer.svg)](https://badge.fury.io/py/vietnormalizer)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A Python library for normalizing Vietnamese text, designed for Text-to-Speech (TTS) and Natural Language Processing (NLP) applications.

## Features

- **Number Conversion**: Converts numbers to Vietnamese words (e.g., `123` → `một trăm hai mươi ba`)
- **Date & Time Normalization**: Converts dates and times to Vietnamese words
- **Currency Conversion**: Handles VND and USD amounts
- **Percentage Conversion**: Converts percentages to Vietnamese words
- **Acronym Expansion**: Expands acronyms using dictionary mappings
- **Non-Vietnamese Word Transliteration**: Transliterates foreign words to Vietnamese pronunciation
- **Text Cleaning**: Removes emojis, special characters, and normalizes Unicode
- **High Performance**: Pre-compiled regex patterns for fast processing

## Installation

```bash
pip install -e .
```

Or install from PyPI:

```bash
pip install vietnormalizer
```

Or install from source:

```bash
git clone https://github.com/nghimestudio/vietnormalizer.git
cd vietnormalizer
pip install -e .
```

```bash
pip install vietnormalizer
```

## Quick Start

```python
from vietnormalizer import VietnameseNormalizer

# Initialize the normalizer
normalizer = VietnameseNormalizer()

# Normalize text
text = "Hôm nay là 25/12/2023, lúc 14:30"
normalized = normalizer.normalize(text)
print(normalized)
# Output: "Hôm nay là ngày hai mươi lăm tháng mười hai năm hai nghìn không trăm hai mươi ba, lúc mười bốn giờ ba mươi"
```

## Usage Examples

### Basic Normalization

```python
from vietnormalizer import VietnameseNormalizer

normalizer = VietnameseNormalizer()

# Numbers
normalizer.normalize("Tôi có 123 quyển sách")
# "Tôi có một trăm hai mươi ba quyển sách"

# Dates
normalizer.normalize("Sinh nhật vào 15/08/1990")
# "Sinh nhật vào mười lăm tháng tám năm một nghìn chín trăm chín mươi"

# Times
normalizer.normalize("Cuộc họp lúc 9:30")
# "Cuộc họp lúc chín giờ ba mươi"

# Currency
normalizer.normalize("Giá là 1.500.000 đồng")
# "Giá là một triệu năm trăm nghìn đồng"

# Percentages
normalizer.normalize("Tăng 25% so với năm ngoái")
# "Tăng hai mươi lăm phần trăm so với năm ngoái"
```

### Custom Dictionary Paths

```python
from vietnormalizer import VietnameseNormalizer

# Use custom CSV files
normalizer = VietnameseNormalizer(
    acronyms_path="path/to/custom/acronyms.csv",
    non_vietnamese_words_path="path/to/custom/words.csv"
)
```

### Disable Preprocessing

```python
# Only apply dictionary replacements, skip number/date conversion
normalized = normalizer.normalize(text, enable_preprocessing=False)
```

### Reload Dictionaries

```python
# Reload dictionaries without recreating the normalizer
normalizer.reload_dictionaries(
    acronyms_path="path/to/updated/acronyms.csv"
)
```

## Advanced Usage

### Using the Processor Directly

For more control, you can use the `VietnameseTextProcessor` class directly:

```python
from vietnormalizer import VietnameseTextProcessor

processor = VietnameseTextProcessor()

# Convert numbers only
words = processor.number_to_words("123")
# "một trăm hai mươi ba"

# Process text without dictionary replacements
processed = processor.process_vietnamese_text("Hôm nay là 25/12/2023")
```

## CSV Dictionary Format

### Acronyms CSV

```csv
acronym,transliteration
USA,Hoa Kỳ
GDP,Tổng sản phẩm quốc nội
AI,trí tuệ nhân tạo
```

### Non-Vietnamese Words CSV

```csv
original,transliteration
original,ô-ri-gin-nồ
container,công-tê-nơ
singapore,xin-ga-po
```

## Performance

The library is optimized for performance:
- All regex patterns are pre-compiled at initialization
- Dictionary replacements use a single combined regex pass
- Minimal memory allocations during processing

## Requirements

- Python 3.8+
- No external dependencies (uses only standard library)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

This library is ported from JavaScript implementations used in Vietnamese TTS systems.

