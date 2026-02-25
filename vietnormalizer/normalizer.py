"""
Vietnamese Text Normalizer - Main normalization class with CSV dictionary support.

This module provides the VietnameseNormalizer class which combines text processing
with dictionary-based replacements (acronyms and non-Vietnamese words) and
rule-based transliteration for words not found in dictionaries.
"""

import csv
import re
from pathlib import Path
from typing import Dict, Optional

from .processor import VietnameseTextProcessor
from .detector import is_vietnamese_word
from .transliterator import transliterate_word

_WORD_BOUNDARY_REGEX = re.compile(r'[\w\u00C0-\u1EFF]+')

# Uppercase code pattern: 2+ chars, starts with uppercase letter, only uppercase + digits
_UPPERCASE_CODE_PATTERN = re.compile(r'\b([A-Z][A-Z0-9]+)\b')

LETTER_NAMES = {
    'A': 'a', 'B': 'bê', 'C': 'xê', 'D': 'đê', 'E': 'ê',
    'F': 'ép', 'G': 'giê', 'H': 'hát', 'I': 'i', 'J': 'giây',
    'K': 'ca', 'L': 'e-lờ', 'M': 'em', 'N': 'en', 'O': 'o',
    'P': 'pê', 'Q': 'cu', 'R': 'e-rờ', 'S': 'ét', 'T': 'tê',
    'U': 'u', 'V': 'vê', 'W': 'vê kép', 'X': 'ích', 'Y': 'i',
    'Z': 'dét',
}


class VietnameseNormalizer:
    """
    Vietnamese text normalizer with dictionary support and transliteration.
    
    Processing pipeline (matching nghitts/src/utils/text-cleaner.js):
    1. Clean text (remove emojis, special chars)
    2. Process Vietnamese text (numbers, dates, times, units, etc.)
    3. Lowercase normalization for matching
    4. Convert acronyms from CSV
    5. Replace non-Vietnamese words from CSV
    6. Transliterate remaining non-Vietnamese words (rule-based)
    
    Example:
        >>> normalizer = VietnameseNormalizer()
        >>> normalizer.normalize("Hôm nay là 25/12/2023")
        'hôm nay là ngày hai mươi lăm tháng mười hai năm hai nghìn không trăm hai mươi ba'
    """
    
    def __init__(
        self,
        acronyms_path: Optional[str] = None,
        non_vietnamese_words_path: Optional[str] = None,
        data_dir: Optional[str] = None,
        enable_transliteration: bool = True
    ):
        """
        Initialize the Vietnamese normalizer.
        
        Args:
            acronyms_path: Path to acronyms CSV file. If None, uses default from package data.
            non_vietnamese_words_path: Path to non-Vietnamese words CSV file. If None, uses default.
            data_dir: Directory containing CSV files. If provided, will look for 'acronyms.csv' and
                     'non-vietnamese-words.csv' in this directory.
            enable_transliteration: If True, words not in dictionary and not Vietnamese
                                  will be transliterated to Vietnamese phonetics.
        """
        self.processor = VietnameseTextProcessor()
        self.enable_transliteration = enable_transliteration
        
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path(__file__).parent / "data"
        
        self.acronym_map = self._load_acronyms(acronyms_path)
        self.non_vietnamese_map = self._load_non_vietnamese_words(non_vietnamese_words_path)
        
        self._build_replacement_dict()
    
    def _load_acronyms(self, custom_path: Optional[str] = None) -> Dict[str, str]:
        """Load acronym mappings from CSV."""
        acronym_map = {}
        
        if custom_path:
            acronyms_path = Path(custom_path)
        else:
            possible_paths = [
                self.data_dir / "acronyms.csv",
            ]
            acronyms_path = None
            for path in possible_paths:
                if path.exists():
                    acronyms_path = path
                    break
        
        if acronyms_path and acronyms_path.exists():
            try:
                with open(acronyms_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        acronym = (
                            row.get("acronym", "") or 
                            row.get("word", "")
                        ).strip().lower()
                        transliteration = (
                            row.get("transliteration", "") or 
                            row.get("vietnamese_pronunciation", "")
                        ).strip()
                        if acronym and transliteration:
                            acronym_map[acronym] = transliteration
            except Exception:
                pass
        
        return dict(sorted(acronym_map.items(), key=lambda x: len(x[0]), reverse=True))
    
    def _load_non_vietnamese_words(self, custom_path: Optional[str] = None) -> Dict[str, str]:
        """Load non-Vietnamese word mappings from CSV."""
        word_map = {}
        
        if custom_path:
            words_path = Path(custom_path)
        else:
            possible_paths = [
                self.data_dir / "non-vietnamese-words.csv",
                self.data_dir / "non-vietnamese-words-20k.csv",
            ]
            words_path = None
            for path in possible_paths:
                if path.exists():
                    words_path = path
                    break
        
        if words_path and words_path.exists():
            try:
                with open(words_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        word = (
                            row.get("word", "") or 
                            row.get("original", "")
                        ).strip().lower()
                        pronunciation = (
                            row.get("vietnamese_pronunciation", "") or 
                            row.get("transliteration", "")
                        ).strip()
                        if word and pronunciation:
                            word_map[word] = pronunciation
            except Exception:
                pass
        
        return dict(sorted(word_map.items(), key=lambda x: len(x[0]), reverse=True))
    
    def _build_replacement_dict(self):
        """Build replacement dictionary from non-Vietnamese words only.
        Acronyms are handled separately by _handle_uppercase_codes (uppercase only)."""
        self.replacements = {}
        for word, pronunciation in self.non_vietnamese_map.items():
            self.replacements[word.lower()] = pronunciation
    
    def _spell_out_code(self, code: str) -> str:
        """Spell out an alphanumeric code letter by letter, digit groups as numbers.
        E.g. 'SE3' → 'ét ê ba', 'D19E' → 'đê mười chín ê'"""
        parts = []
        i = 0
        while i < len(code):
            if code[i].isdigit():
                # Collect consecutive digits
                j = i
                while j < len(code) and code[j].isdigit():
                    j += 1
                parts.append(self.processor.number_to_words(code[i:j]))
                i = j
            elif code[i].upper() in LETTER_NAMES:
                parts.append(LETTER_NAMES[code[i].upper()])
                i += 1
            else:
                i += 1
        return ' '.join(parts)
    
    def _handle_uppercase_codes(self, text: str) -> str:
        """Handle uppercase codes: check acronym dict first, else spell out letter by letter.
        Must be called BEFORE lowercasing."""
        def replace_code(match):
            code = match.group(1)
            code_lower = code.lower()
            # Check acronym dictionary first
            if code_lower in self.acronym_map:
                return self.acronym_map[code_lower]
            # Not in acronym dict → spell out
            return self._spell_out_code(code)
        return _UPPERCASE_CODE_PATTERN.sub(replace_code, text)
    
    def _apply_transliteration(self, text: str) -> str:
        """
        Apply transliteration to words not in the replacement map.
        Only processes words that weren't replaced by CSV and aren't Vietnamese.
        Matches the logic from nghitts/src/utils/text-cleaner.js applyTransliteration().
        """
        if not text:
            return text
        
        processed_words = set()
        replacements_to_make = []

        for match in _WORD_BOUNDARY_REGEX.finditer(text):
            word = match.group(0)
            word_lower = word.lower()
            
            if word_lower in processed_words:
                continue
            processed_words.add(word_lower)
            
            # Skip if word is in CSV replacement map
            if word_lower in self.replacements:
                continue
            
            # Skip if word is Vietnamese
            if is_vietnamese_word(word) or is_vietnamese_word(word_lower):
                continue
            
            # Skip single characters
            if len(word) <= 1:
                continue
            
            transliterated = transliterate_word(word)
            if transliterated != word:
                replacements_to_make.append((word, transliterated))
        
        # Apply replacements
        for original, transliterated in replacements_to_make:
            escaped = re.escape(original)
            not_word_char = r'[^\w\u00C0-\u1EFF]'
            pattern = re.compile(
                rf'(?:^|({not_word_char}))({escaped})(?={not_word_char}|$)',
                re.IGNORECASE
            )
            
            def make_replacer(trans):
                def replacer(m):
                    boundary = m.group(1) or ''
                    matched_word = m.group(2)
                    if matched_word and matched_word[0].isupper():
                        result = trans[0].upper() + trans[1:] if len(trans) > 1 else trans.upper()
                    else:
                        result = trans
                    return boundary + result
                return replacer
            
            text = pattern.sub(make_replacer(transliterated), text)
        
        return text
    
    def normalize(
        self,
        text: str,
        enable_preprocessing: bool = True,
        enable_transliteration: Optional[bool] = None
    ) -> str:
        """
        Normalize Vietnamese text.
        
        Processing pipeline:
        1. Clean text and process Vietnamese (numbers, dates, times, etc.)
        2. Lowercase normalization for consistent matching
        3. Replace acronyms from CSV
        4. Replace non-Vietnamese words from CSV
        5. Transliterate remaining non-Vietnamese words (if enabled)
        
        Args:
            text: Input text to normalize.
            enable_preprocessing: If True, applies full normalization pipeline.
                                 If False, only applies dictionary replacements.
            enable_transliteration: Override instance-level transliteration setting.
                                  If None, uses the value set during initialization.
            
        Returns:
            Normalized text string.
        """
        if not text:
            return ''
        
        if enable_preprocessing:
            # Step 1: Process Vietnamese text (numbers, dates, times, etc.)
            normalized = self.processor.process_vietnamese_text(text)
        else:
            import unicodedata
            normalized = unicodedata.normalize('NFC', text)
            normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Step 2: Handle uppercase codes (acronyms/abbreviations)
        # Must run BEFORE lowercasing to detect uppercase
        normalized = self._handle_uppercase_codes(normalized)
        
        # Step 3: Lowercase normalization for consistent matching
        normalized = normalized.lower()
        
        # Step 3 & 4: Replace words/acronyms using fast word-by-word lookup
        if self.replacements:
            def replace_word(match):
                word = match.group(0)
                word_lower = word.lower()
                if word_lower in self.replacements:
                    return self.replacements[word_lower]
                return word
            
            normalized = re.sub(r'\b\w+\b', replace_word, normalized)
        
        # Step 5: Transliterate remaining non-Vietnamese words
        should_transliterate = enable_transliteration if enable_transliteration is not None else self.enable_transliteration
        if should_transliterate:
            normalized = self._apply_transliteration(normalized)
        
        # Clean up whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def reload_dictionaries(
        self,
        acronyms_path: Optional[str] = None,
        non_vietnamese_words_path: Optional[str] = None
    ):
        """
        Reload dictionaries from CSV files.
        
        Args:
            acronyms_path: Path to acronyms CSV file. If None, uses default.
            non_vietnamese_words_path: Path to non-Vietnamese words CSV file. If None, uses default.
        """
        self.acronym_map = self._load_acronyms(acronyms_path)
        self.non_vietnamese_map = self._load_non_vietnamese_words(non_vietnamese_words_path)
        self._build_replacement_dict()
