"""
Vietnamese Text Normalizer - Main normalization class with CSV dictionary support.

This module provides the VietnameseNormalizer class which combines text processing
with dictionary-based replacements (acronyms and non-Vietnamese words).
"""

import csv
import re
from pathlib import Path
from typing import Dict, Optional

from .processor import VietnameseTextProcessor


class VietnameseNormalizer:
    """
    Vietnamese text normalizer with dictionary support.
    
    This class provides comprehensive Vietnamese text normalization including:
    - Number to word conversion
    - Date and time conversion
    - Currency and percentage conversion
    - Acronym expansion
    - Non-Vietnamese word transliteration
    
    Example:
        >>> normalizer = VietnameseNormalizer()
        >>> normalizer.normalize("Hôm nay là 25/12/2023")
        'Hôm nay là ngày hai mươi lăm tháng mười hai năm hai nghìn không trăm hai mươi ba'
    """
    
    def __init__(
        self,
        acronyms_path: Optional[str] = None,
        non_vietnamese_words_path: Optional[str] = None,
        data_dir: Optional[str] = None
    ):
        """
        Initialize the Vietnamese normalizer.
        
        Args:
            acronyms_path: Path to acronyms CSV file. If None, uses default from package data.
            non_vietnamese_words_path: Path to non-Vietnamese words CSV file. If None, uses default from package data.
            data_dir: Directory containing CSV files. If provided, will look for 'acronyms.csv' and 
                     'non-vietnamese-words.csv' in this directory.
        """
        # Initialize text processor
        self.processor = VietnameseTextProcessor()
        
        # Determine data directory
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            # Use package data directory as default
            self.data_dir = Path(__file__).parent / "data"
        
        # Load dictionaries
        self.acronym_map = self._load_acronyms(acronyms_path)
        self.non_vietnamese_map = self._load_non_vietnamese_words(non_vietnamese_words_path)
        
        # Pre-compile regex patterns for performance
        self._compile_regex_patterns()
    
    def _load_acronyms(self, custom_path: Optional[str] = None) -> Dict[str, str]:
        """Load acronym mappings from CSV."""
        acronym_map = {}
        
        # Determine path
        if custom_path:
            acronyms_path = Path(custom_path)
        else:
            # Try multiple possible filenames
            possible_paths = [
                self.data_dir / "acronyms.csv",
                self.data_dir / "non-vietnamese-words.csv",  # fallback
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
                        # Support different CSV column names
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
            except Exception as e:
                # Silently fail if CSV can't be loaded
                pass
        
        # Sort by length (longest first) for proper matching priority
        return dict(sorted(acronym_map.items(), key=lambda x: len(x[0]), reverse=True))
    
    def _load_non_vietnamese_words(self, custom_path: Optional[str] = None) -> Dict[str, str]:
        """Load non-Vietnamese word mappings from CSV."""
        word_map = {}
        
        # Determine path
        if custom_path:
            words_path = Path(custom_path)
        else:
            # Try multiple possible filenames
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
                        word = row.get("word", "").strip().lower()
                        pronunciation = row.get("vietnamese_pronunciation", "").strip()
                        if word and pronunciation:
                            word_map[word] = pronunciation
            except Exception as e:
                # Silently fail if CSV can't be loaded
                pass
        
        # Sort by length (longest first) for proper matching priority
        return dict(sorted(word_map.items(), key=lambda x: len(x[0]), reverse=True))
    
    def _compile_regex_patterns(self):
        """Pre-compile regex patterns for faster text normalization."""
        # Create a single combined pattern for all replacements
        # This is much faster than doing 100+ separate regex scans
        all_patterns = []
        replacements = {}
        
        # Add non-Vietnamese words
        for word, pronunciation in self.non_vietnamese_map.items():
            escaped_word = re.escape(word)
            pattern_str = rf'\b{escaped_word}\b'
            all_patterns.append(pattern_str)
            replacements[word.lower()] = pronunciation
        
        # Add acronyms
        for acronym, transliteration in self.acronym_map.items():
            escaped_acronym = re.escape(acronym)
            pattern_str = rf'\b{escaped_acronym}\b'
            all_patterns.append(pattern_str)
            replacements[acronym.lower()] = transliteration
        
        # Combine all patterns into one regex (using alternation)
        # Sort by length (longest first) to match longer patterns first
        if all_patterns:
            # Sort patterns by length descending to match longer ones first
            sorted_patterns = sorted(all_patterns, key=len, reverse=True)
            combined_pattern = '|'.join(f'({p})' for p in sorted_patterns)
            self.combined_regex = re.compile(combined_pattern, re.IGNORECASE)
            self.replacements = replacements
        else:
            self.combined_regex = None
            self.replacements = {}
    
    def normalize(
        self,
        text: str,
        enable_preprocessing: bool = True
    ) -> str:
        """
        Normalize Vietnamese text.
        
        Args:
            text: Input text to normalize
            enable_preprocessing: If True, applies full normalization pipeline.
                                 If False, only applies dictionary replacements.
            
        Returns:
            Normalized text string
        """
        if not text:
            return ''
        
        if enable_preprocessing:
            # Step 1: Process Vietnamese text (numbers, dates, times, etc.)
            # This also includes text cleaning
            normalized = self.processor.process_vietnamese_text(text)
        else:
            # Skip preprocessing - just normalize Unicode and clean whitespace
            import unicodedata
            normalized = unicodedata.normalize('NFC', text)
            normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Step 2: Normalize to lowercase for consistent matching
        mapping_input = normalized.lower()
        
        # Step 3 & 4: Replace all words/acronyms in a SINGLE pass using combined regex
        # This is MUCH faster than 100+ separate regex scans
        if self.combined_regex:
            def replace_func(match):
                matched = match.group(0).lower()
                replacement = self.replacements.get(matched, matched)
                # Preserve original case if first letter was uppercase
                if match.group(0) and match.group(0)[0].isupper():
                    return replacement[0].upper() + replacement[1:] if len(replacement) > 1 else replacement.upper()
                return replacement
            
            mapping_input = self.combined_regex.sub(replace_func, mapping_input)
        
        # Clean up whitespace
        normalized = re.sub(r'\s+', ' ', mapping_input).strip()
        
        return normalized
    
    def reload_dictionaries(
        self,
        acronyms_path: Optional[str] = None,
        non_vietnamese_words_path: Optional[str] = None
    ):
        """
        Reload dictionaries from CSV files.
        
        Useful when dictionaries are updated without recreating the normalizer.
        
        Args:
            acronyms_path: Path to acronyms CSV file. If None, uses default.
            non_vietnamese_words_path: Path to non-Vietnamese words CSV file. If None, uses default.
        """
        self.acronym_map = self._load_acronyms(acronyms_path)
        self.non_vietnamese_map = self._load_non_vietnamese_words(non_vietnamese_words_path)
        self._compile_regex_patterns()

