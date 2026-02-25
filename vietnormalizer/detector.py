"""
Vietnamese Language Detector - Detects if a word is Vietnamese.

Ported from nghitts/src/utils/vietnamese-detector.js
Uses diacritics, character patterns, and word structure analysis.
"""

import re


class VnLanguageDetector:
    """Detect if a word is Vietnamese based on structure and character analysis."""

    def __init__(self):
        self.vn_accent_regex = re.compile(
            r'[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]',
            re.IGNORECASE
        )
        self.vn_vowels = "ueoaiy"
        self.vn_onsets = {
            'b', 'c', 'd', 'đ', 'g', 'h', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'x',
            'ch', 'gh', 'gi', 'kh', 'ng', 'nh', 'ph', 'qu', 'th', 'tr'
        }
        self.vn_endings = {'p', 't', 'c', 'm', 'n', 'ng', 'ch', 'nh'}
        self.en_special_chars = re.compile(r'[fwzj]', re.IGNORECASE)
        self.syllable_regex = re.compile(r'^([^ueoaiy]*)([ueoaiy]+)([^ueoaiy]*)$')

    def is_vietnamese_word(self, word: str) -> bool:
        if not word:
            return False
        w = word.lower().strip()

        if self.vn_accent_regex.search(w):
            return True

        if self.en_special_chars.search(w):
            return False

        match = self.syllable_regex.match(w)
        if not match:
            return False

        onset, vowel, ending = match.group(1), match.group(2), match.group(3)

        if onset and onset not in self.vn_onsets:
            return False

        if ending and ending not in self.vn_endings:
            return False

        if re.search(r'ee|oo|ea|ae|ie', vowel):
            if vowel not in ('oa', 'oe', 'ua', 'uy'):
                return False

        return True


_detector = VnLanguageDetector()


def is_vietnamese_word(word: str) -> bool:
    """Check if a word is Vietnamese."""
    return _detector.is_vietnamese_word(word)
