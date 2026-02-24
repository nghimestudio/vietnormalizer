"""
Vietnamese Text Normalizer - A Python library for normalizing Vietnamese text.

This library provides comprehensive Vietnamese text normalization including:
- Number to word conversion (numbers, dates, times, currency, percentages)
- Acronym expansion
- Non-Vietnamese word transliteration
- Text cleaning and Unicode normalization

Example:
    >>> from vietnormalizer import VietnameseNormalizer
    >>> normalizer = VietnameseNormalizer()
    >>> normalized = normalizer.normalize("Hôm nay là 25/12/2023")
    >>> print(normalized)
    'Hôm nay là ngày hai mươi lăm tháng mười hai năm hai nghìn không trăm hai mươi ba'
"""

from .normalizer import VietnameseNormalizer
from .processor import VietnameseTextProcessor

__version__ = "0.1.1"
__all__ = ["VietnameseNormalizer", "VietnameseTextProcessor"]

