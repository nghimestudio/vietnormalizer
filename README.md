# Vietnamese Text Normalizer

[![PyPI version](https://badge.fury.io/py/vietnormalizer.svg)](https://badge.fury.io/py/vietnormalizer)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A Python library for normalizing Vietnamese text, designed for Text-to-Speech (TTS) and Natural Language Processing (NLP) applications. Ported from [nghitts](https://github.com/nghimestudio/nghitts).

## Features

- **Number Conversion**: Numbers to Vietnamese words (`123` → `một trăm hai mươi ba`)
- **Date & Time**: Full date/time conversion including date ranges (`25-26/12` → `hai mươi lăm đến hai mươi sáu tháng mười hai`)
- **Currency**: VND and USD amounts (`50.000đ` → `năm mươi nghìn đồng`)
- **Percentages**: Including ranges (`3-5%` → `ba đến năm phần trăm`)
- **Year Ranges**: `1873-1907` → `một nghìn tám trăm bảy mươi ba đến một nghìn chín trăm lẻ bảy`
- **Ordinals**: `thứ 2` → `thứ hai`
- **Phone Numbers**: Digit-by-digit reading
- **Measurement Units**: `120km/h` → `một trăm hai mươi ki-lô-mét trên giờ`
- **Acronym Expansion**: Dictionary-based (`NASA` → `na-sa`)
- **Non-Vietnamese Word Replacement**: Dictionary-based (`container` → `công-tê-nơ`)
- **Rule-based Transliteration**: Words NOT in dictionaries are automatically transliterated to Vietnamese phonetics (`algorithm` → `a-go-rít`)
- **Vietnamese Word Detection**: Automatically detects Vietnamese words and skips them during transliteration
- **Text Cleaning**: Removes emojis, URLs, emails, normalizes Unicode and punctuation
- **Special Characters**: `&` → `và`, `@` → `a còng`, `#` → `thăng`
- **High Performance**: ~0.6ms per call with 17K+ dictionary entries

## Installation

```bash
pip install vietnormalizer
```

Or install from source:

```bash
git clone https://github.com/nghimestudio/vietnormalizer.git
cd vietnormalizer
pip install -e .
```

## Quick Start

```python
from vietnormalizer import VietnameseNormalizer

normalizer = VietnameseNormalizer()

# Numbers, dates, and times
normalizer.normalize("Hôm nay là 25/12/2023, lúc 14:30")
# → "hôm nay là ngày hai mươi lăm tháng mười hai năm hai nghìn không trăm hai mươi ba, lúc mười bốn giờ ba mươi phút"

# Non-Vietnamese word replacement (from built-in dictionary)
normalizer.normalize("Hello container from Singapore")
# → "hê-lô công-tê-nơ phờ-rôm xin-ga-po"

# Acronym expansion (from built-in dictionary)
normalizer.normalize("Tôi xem TV và dùng AI hàng ngày")
# → "tôi xem ti vi và dùng trí tuệ nhân tạo hàng ngày"

# Rule-based transliteration for words NOT in dictionary
normalizer.normalize("database server configuration")
# → "đa-ta-bê xơ-vơ con-phi-gu-raân"

# Measurement units
normalizer.normalize("Tốc độ 120km/h, diện tích 500m2")
# → "tốc độ một trăm hai mươi ki-lô-mét trên giờ, diện tích năm trăm mét vuông"

# Currency with thousand separators
normalizer.normalize("Giá 50.000đ cho mỗi người")
# → "giá năm mươi nghìn đồng cho mỗi người"

# Year ranges, ordinals, percentages
normalizer.normalize("1873-1907, thứ 2, tăng 6,5%")
# → "một nghìn tám trăm bảy mươi ba đến một nghìn chín trăm lẻ bảy, thứ hai, tăng sáu phẩy năm phần trăm"

# Date ranges
normalizer.normalize("ngày 25-26/12/2023")
# → "ngày hai mươi lăm đến hai mươi sáu tháng mười hai năm hai nghìn không trăm hai mươi ba"

# Percentage ranges
normalizer.normalize("3-5% dân số")
# → "ba đến năm phần trăm dân số"
```

## Transliteration Control

```python
# Disable transliteration (only use CSV dictionary replacements)
normalizer = VietnameseNormalizer(enable_transliteration=False)
normalizer.normalize("machine learning algorithm")
# → "ma-sin li-nin algorithm"  (words in CSV replaced, others kept as-is)

# Or override per-call
normalizer = VietnameseNormalizer(enable_transliteration=True)
normalizer.normalize("machine learning", enable_transliteration=False)
```

## Vietnamese Word Detection

```python
from vietnormalizer import is_vietnamese_word

is_vietnamese_word("xin")      # True (valid Vietnamese structure)
is_vietnamese_word("chào")     # True (has Vietnamese diacritics)
is_vietnamese_word("database") # False (contains 'b' ending, invalid structure)
is_vietnamese_word("flow")     # False (contains 'f' and 'w')
```

## Direct Transliteration

```python
from vietnormalizer import transliterate_word, english_to_vietnamese

transliterate_word("database")   # "đa-ta-bâi" (checks if Vietnamese first)
transliterate_word("xin")        # "xin" (detected as Vietnamese, kept as-is)
english_to_vietnamese("computer") # "com-pu-tơ" (always transliterates)
```

## Custom Dictionaries

```python
normalizer = VietnameseNormalizer(
    acronyms_path="path/to/acronyms.csv",
    non_vietnamese_words_path="path/to/words.csv"
)

# Or specify a directory containing both files
normalizer = VietnameseNormalizer(data_dir="path/to/data/")

# Reload dictionaries at runtime
normalizer.reload_dictionaries(acronyms_path="path/to/updated.csv")
```

### CSV Formats

**acronyms.csv:**
```csv
acronym,transliteration
NASA,na-sa
GDP,tổng sản phẩm quốc nội
AI,trí tuệ nhân tạo
```

**non-vietnamese-words.csv:**
```csv
original,transliteration
container,công-tê-nơ
singapore,xin-ga-po
server,xơ-vơ
```

## Advanced Usage

### Using the Processor Directly

```python
from vietnormalizer import VietnameseTextProcessor

processor = VietnameseTextProcessor()

# Convert numbers
processor.number_to_words("123")  # "một trăm hai mươi ba"

# Process text (numbers, dates, times, units - no dictionary replacements)
processor.process_vietnamese_text("Giá 50.000đ lúc 15h30")
```

### Disable Preprocessing

```python
# Only apply dictionary replacements and transliteration, skip number/date conversion
normalizer.normalize(text, enable_preprocessing=False)
```

## Processing Pipeline

The normalization follows this pipeline (matching [nghitts](https://github.com/nghimestudio/nghitts)):

1. Unicode normalization (NFC)
2. Special character replacement (`&` → `và`, `@` → `a còng`, URL/email removal)
3. Punctuation normalization
4. Text cleaning (emojis, non-Latin chars)
5. Year range conversion
6. Percentage range conversion
7. Date/time conversion (including ranges)
8. Ordinal conversion
9. Thousand separator removal
10. Currency conversion
11. Remaining percentage conversion
12. Phone number conversion
13. Decimal conversion
14. Measurement unit conversion
15. Standalone number conversion
16. Lowercase normalization
17. Acronym replacement (from CSV)
18. Non-Vietnamese word replacement (from CSV)
19. Rule-based transliteration (for remaining non-Vietnamese words)

## Performance

- ~0.6ms per normalization call with 17K+ dictionary entries
- All regex patterns pre-compiled at initialization
- Dictionary lookups use O(1) hash map instead of regex alternation
- Total initialization time: ~40ms

## Requirements

- Python 3.8+
- No external dependencies (uses only standard library)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

Ported from the JavaScript implementations in [nghitts](https://github.com/nghimestudio/nghitts).
