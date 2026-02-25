"""
Vietnamese Text Normalizer - A Python library for normalizing Vietnamese text.

This library provides comprehensive Vietnamese text normalization including:
- Number to word conversion (numbers, dates, times, currency, percentages)
- Acronym expansion from CSV dictionaries
- Non-Vietnamese word replacement from CSV dictionaries
- Rule-based transliteration for words not in dictionaries
- Vietnamese word detection
- Text cleaning and Unicode normalization
- Measurement unit conversion
- Phone number reading
- Year range, ordinal, and date range handling

Example:
    >>> from vietnormalizer import VietnameseNormalizer
    >>> normalizer = VietnameseNormalizer()
    >>> normalized = normalizer.normalize("Hôm nay là 25/12/2023")
    >>> print(normalized)
    'hôm nay là ngày hai mươi lăm tháng mười hai năm hai nghìn không trăm hai mươi ba'
"""

from .normalizer import VietnameseNormalizer
from .processor import VietnameseTextProcessor
from .detector import VnLanguageDetector, is_vietnamese_word
from .transliterator import transliterate_word, english_to_vietnamese

__version__ = "0.2.1"
__all__ = [
    "VietnameseNormalizer",
    "VietnameseTextProcessor",
    "VnLanguageDetector",
    "is_vietnamese_word",
    "transliterate_word",
    "english_to_vietnamese",
]
