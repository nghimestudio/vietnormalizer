# Vietnamese Normalizer Library Structure

## Package Structure

```
vietnormalizer/
├── __init__.py              # Package initialization and exports
├── processor.py             # VietnameseTextProcessor class (core text processing)
├── normalizer.py            # VietnameseNormalizer class (main API with CSV support)
└── data/
    ├── acronyms.csv         # Acronym dictionary
    └── non-vietnamese-words.csv  # Non-Vietnamese word dictionary
```

## Installation

### Development Installation

```bash
# Install in editable mode
pip install -e .
```

### Production Installation

```bash
# Build and install
python setup.py sdist bdist_wheel
pip install dist/vietnormalizer-0.1.0.tar.gz

# Or install from PyPI
pip install vietnormalizer
```

## Usage

### Basic Usage

```python
from vietnormalizer import VietnameseNormalizer

# Initialize
normalizer = VietnameseNormalizer()

# Normalize text
result = normalizer.normalize("Hôm nay là 25/12/2023")
```

### Advanced Usage

```python
# Custom dictionary paths
normalizer = VietnameseNormalizer(
    acronyms_path="custom/acronyms.csv",
    non_vietnamese_words_path="custom/words.csv"
)

# Disable preprocessing (faster, only dictionary replacements)
result = normalizer.normalize(text, enable_preprocessing=False)

# Reload dictionaries
normalizer.reload_dictionaries(acronyms_path="updated/acronyms.csv")
```

### Direct Processor Usage

```python
from vietnormalizer import VietnameseTextProcessor

processor = VietnameseTextProcessor()
words = processor.number_to_words("123")  # "một trăm hai mươi ba"
```

## Features

1. **Number Conversion**: All numbers → Vietnamese words
2. **Date/Time**: Dates and times → Vietnamese words
3. **Currency**: VND and USD amounts → Vietnamese words
4. **Percentages**: Percentages → Vietnamese words
5. **Acronym Expansion**: Using CSV dictionary
6. **Word Transliteration**: Non-Vietnamese words → Vietnamese pronunciation
7. **Text Cleaning**: Emoji removal, Unicode normalization

## Testing

Run the test script:

```bash
python3 test_normalizer.py
```

## Files

- `processor.py`: Core text processing logic (no dependencies on CSV files)
- `normalizer.py`: Main API that combines processor with dictionary support
- `__init__.py`: Package exports
- `setup.py`: Installation script (alternative to pyproject.toml)
- `pyproject.toml`: Modern Python package configuration
- `README.md`: User documentation
- `test_normalizer.py`: Simple test script

