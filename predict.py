#!/usr/bin/env python3
"""
Cog prediction function for Vietnamese Piper TTS.
Implements comprehensive text normalization based on utils/text-cleaner.js
"""

"""
Runtime tuning (Replicate/Docker):
- Disable ONNX Runtime CPU thread affinity (avoids noisy pthread_setaffinity_np warnings)
- Cap CPU threads to reduce oversubscription on shared runners
"""

import os

os.environ.setdefault("ORT_DISABLE_AFFINITY", "1")
os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", os.environ.get("OMP_NUM_THREADS", "4"))

import warnings

# Keep logs readable on Replicate
warnings.filterwarnings("ignore")

import csv
import re
import unicodedata
import wave
from pathlib import Path
from typing import Dict, List

from cog import BasePredictor, Input, Path as CogPath
from piper import PiperVoice


class VietnameseTextProcessor:
    """Process Vietnamese text for TTS - ported from utils/vietnamese-processor.js"""
    
    DIGITS = {
        '0': 'không', '1': 'một', '2': 'hai', '3': 'ba', '4': 'bốn',
        '5': 'năm', '6': 'sáu', '7': 'bảy', '8': 'tám', '9': 'chín'
    }
    
    TEENS = {
        '10': 'mười', '11': 'mười một', '12': 'mười hai', '13': 'mười ba',
        '14': 'mười bốn', '15': 'mười lăm', '16': 'mười sáu', '17': 'mười bảy',
        '18': 'mười tám', '19': 'mười chín'
    }
    
    TENS = {
        '2': 'hai mươi', '3': 'ba mươi', '4': 'bốn mươi', '5': 'năm mươi',
        '6': 'sáu mươi', '7': 'bảy mươi', '8': 'tám mươi', '9': 'chín mươi'
    }
    
    def __init__(self):
        """Pre-compile regex patterns for performance."""
        # Emoji pattern
        self.emoji_pattern = re.compile(
            r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|'
            r'[\U0001F1E0-\U0001F1FF]|[\u2600-\u26FF]|[\u2700-\u27BF]|'
            r'[\U0001F900-\U0001F9FF]|[\U0001F018-\U0001F270]|[\u238C-\u2454]|'
            r'[\u20D0-\u20FF]|[\uFE0F]|[\u200D]',
            flags=re.UNICODE
        )
        
        # Pre-compile common patterns
        self.thousand_sep_pattern = re.compile(r'(\d{1,3}(?:\.\d{3})+)(?=\s|$|[^\d.,])')
        self.decimal_pattern = re.compile(r'(\d+),(\d+)(?=\s|$|[^\d,])')
        self.percentage_decimal_pattern = re.compile(r'(\d+),(\d+)\s*%')
        self.percentage_pattern = re.compile(r'(\d+)\s*%')
        self.standalone_number_pattern = re.compile(r'\b\d+\b')
        self.whitespace_pattern = re.compile(r'\s+')
        
        # Pre-compile time patterns
        self.time_hms_pattern = re.compile(r'(\d{1,2}):(\d{2})(?::(\d{2}))?')
        self.time_hhmm_pattern = re.compile(r'(\d{1,2})h(\d{2})(?![a-zà-ỹ])', re.IGNORECASE)
        self.time_h_pattern = re.compile(r'(\d{1,2})h(?![a-zà-ỹ\d])', re.IGNORECASE)
        self.time_giophut_pattern = re.compile(r'(\d+)\s*giờ\s*(\d+)\s*phút')
        self.time_giờ_pattern = re.compile(r'(\d+)\s*giờ(?!\s*\d)')
        
        # Pre-compile date patterns
        self.date_full_pattern = re.compile(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})')
        self.date_month_year_pattern = re.compile(r'(?:tháng\s+)?(\d{1,2})\s*[/-]\s*(\d{4})')
        self.date_day_month_pattern = re.compile(r'(\d{1,2})\s*[/-]\s*(\d{1,2})(?![\/-]\d)')
        
        # Pre-compile currency patterns
        self.currency_vnd_pattern1 = re.compile(r'(\d+(?:,\d+)?)\s*(?:đồng|VND|vnđ)\b', re.IGNORECASE)
        self.currency_vnd_pattern2 = re.compile(r'(\d+(?:,\d+)?)đ(?![a-zà-ỹ])', re.IGNORECASE)
        self.currency_usd_pattern1 = re.compile(r'\$\s*(\d+(?:,\d+)?)')
        self.currency_usd_pattern2 = re.compile(r'(\d+(?:,\d+)?)\s*(?:USD|\$)', re.IGNORECASE)
    
    def number_to_words(self, num_str: str) -> str:
        """Convert number string to Vietnamese words."""
        num_str = re.sub(r'^0+', '', num_str) or '0'
        
        if num_str.startswith('-'):
            return 'âm ' + self.number_to_words(num_str[1:])
        
        try:
            num = int(num_str)
        except ValueError:
            return num_str
        
        if num == 0:
            return 'không'
        if num < 10:
            return self.DIGITS[str(num)]
        if num < 20:
            return self.TEENS[str(num)]
        if num < 100:
            tens = num // 10
            units = num % 10
            if units == 0:
                return self.TENS[str(tens)]
            elif units == 1:
                return self.TENS[str(tens)] + ' mốt'
            elif units == 4:
                return self.TENS[str(tens)] + ' tư'
            elif units == 5:
                return self.TENS[str(tens)] + ' lăm'
            else:
                return self.TENS[str(tens)] + ' ' + self.DIGITS[str(units)]
        if num < 1000:
            hundreds = num // 100
            remainder = num % 100
            result = self.DIGITS[str(hundreds)] + ' trăm'
            if remainder == 0:
                return result
            elif remainder < 10:
                return result + ' lẻ ' + self.DIGITS[str(remainder)]
            else:
                return result + ' ' + self.number_to_words(str(remainder))
        if num < 1000000:
            thousands = num // 1000
            remainder = num % 1000
            result = self.number_to_words(str(thousands)) + ' nghìn'
            if remainder == 0:
                return result
            elif remainder < 100:
                if remainder < 10:
                    return result + ' không trăm lẻ ' + self.DIGITS[str(remainder)]
                else:
                    return result + ' không trăm ' + self.number_to_words(str(remainder))
            else:
                return result + ' ' + self.number_to_words(str(remainder))
        if num < 1000000000:
            millions = num // 1000000
            remainder = num % 1000000
            result = self.number_to_words(str(millions)) + ' triệu'
            if remainder == 0:
                return result
            elif remainder < 100:
                if remainder < 10:
                    return result + ' không trăm lẻ ' + self.DIGITS[str(remainder)]
                else:
                    return result + ' không trăm ' + self.number_to_words(str(remainder))
            else:
                return result + ' ' + self.number_to_words(str(remainder))
        if num < 1000000000000:
            billions = num // 1000000000
            remainder = num % 1000000000
            result = self.number_to_words(str(billions)) + ' tỷ'
            if remainder == 0:
                return result
            elif remainder < 100:
                if remainder < 10:
                    return result + ' không trăm lẻ ' + self.DIGITS[str(remainder)]
                else:
                    return result + ' không trăm ' + self.number_to_words(str(remainder))
            else:
                return result + ' ' + self.number_to_words(str(remainder))
        
        # For very large numbers, read digit by digit
        return ' '.join(self.DIGITS.get(d, d) for d in num_str)
    
    def remove_thousand_separators(self, text: str) -> str:
        """Remove thousand separators (dots) from numbers."""
        def replace(match):
            return match.group(0).replace('.', '')
        return self.thousand_sep_pattern.sub(replace, text)
    
    def convert_decimal(self, text: str) -> str:
        """Convert decimal numbers: 7,27 -> bảy phẩy hai mươi bảy"""
        def replace(match):
            integer_part = match.group(1)
            decimal_part = match.group(2)
            integer_words = self.number_to_words(integer_part)
            decimal_words = self.number_to_words(re.sub(r'^0+', '', decimal_part) or '0')
            return f"{integer_words} phẩy {decimal_words}"
        return self.decimal_pattern.sub(replace, text)
    
    def convert_percentage(self, text: str) -> str:
        """Convert percentages: 50% -> năm mươi phần trăm"""
        # Handle decimals first
        def replace_decimal(match):
            integer_part = match.group(1)
            decimal_part = match.group(2)
            integer_words = self.number_to_words(integer_part)
            decimal_words = self.number_to_words(re.sub(r'^0+', '', decimal_part) or '0')
            return f"{integer_words} phẩy {decimal_words} phần trăm"
        text = self.percentage_decimal_pattern.sub(replace_decimal, text)
        
        # Handle whole numbers
        def replace_whole(match):
            return self.number_to_words(match.group(1)) + ' phần trăm'
        return self.percentage_pattern.sub(replace_whole, text)
    
    def convert_currency(self, text: str) -> str:
        """Convert currency amounts"""
        def replace_vnd(match):
            num = match.group(1).replace(',', '')
            return self.number_to_words(num) + ' đồng'
        
        text = self.currency_vnd_pattern1.sub(replace_vnd, text)
        text = self.currency_vnd_pattern2.sub(replace_vnd, text)
        
        def replace_usd(match):
            num = match.group(1).replace(',', '')
            return self.number_to_words(num) + ' đô la'
        
        text = self.currency_usd_pattern1.sub(replace_usd, text)
        text = self.currency_usd_pattern2.sub(replace_usd, text)
        return text
    
    def convert_time(self, text: str) -> str:
        """Convert time expressions: 2:20 -> hai giờ hai mươi phút"""
        def replace_hms(match):
            hour = match.group(1)
            minute = match.group(2)
            second = match.group(3)
            result = self.number_to_words(hour) + ' giờ'
            if minute:
                result += ' ' + self.number_to_words(minute) + ' phút'
            if second:
                result += ' ' + self.number_to_words(second) + ' giây'
            return result
        text = self.time_hms_pattern.sub(replace_hms, text)
        
        def replace_hhmm(match):
            hour = match.group(1)
            minute = match.group(2)
            h, m = int(hour), int(minute)
            if 0 <= h <= 23 and 0 <= m <= 59:
                return self.number_to_words(hour) + ' giờ ' + self.number_to_words(minute)
            return match.group(0)
        text = self.time_hhmm_pattern.sub(replace_hhmm, text)
        
        def replace_h(match):
            hour = match.group(1)
            h = int(hour)
            if 0 <= h <= 23:
                return self.number_to_words(hour) + ' giờ'
            return match.group(0)
        text = self.time_h_pattern.sub(replace_h, text)
        
        def replace_giophut(match):
            hour = match.group(1)
            minute = match.group(2)
            return self.number_to_words(hour) + ' giờ ' + self.number_to_words(minute) + ' phút'
        text = self.time_giophut_pattern.sub(replace_giophut, text)
        
        def replace_giờ(match):
            return self.number_to_words(match.group(1)) + ' giờ'
        text = self.time_giờ_pattern.sub(replace_giờ, text)
        return text
    
    def convert_date(self, text: str) -> str:
        """Convert date expressions"""
        def is_valid_date(day: str, month: str, year: str = None) -> bool:
            d, m = int(day), int(month)
            if year:
                y = int(year)
                return 1 <= d <= 31 and 1 <= m <= 12 and 1000 <= y <= 9999
            return 1 <= d <= 31 and 1 <= m <= 12
        
        # DD/MM/YYYY or DD-MM-YYYY
        def replace_full_date(match):
            day, month, year = match.group(1), match.group(2), match.group(3)
            if is_valid_date(day, month, year):
                return f"ngày {self.number_to_words(day)} tháng {self.number_to_words(month)} năm {self.number_to_words(year)}"
            return match.group(0)
        text = self.date_full_pattern.sub(replace_full_date, text)
        
        # MM/YYYY
        def replace_month_year(match):
            month, year = match.group(1), match.group(2)
            if 1 <= int(month) <= 12 and 1000 <= int(year) <= 9999:
                return f"tháng {self.number_to_words(month)} năm {self.number_to_words(year)}"
            return match.group(0)
        text = self.date_month_year_pattern.sub(replace_month_year, text)
        
        # DD/MM
        def replace_day_month(match):
            day, month = match.group(1), match.group(2)
            if is_valid_date(day, month):
                return f"{self.number_to_words(day)} tháng {self.number_to_words(month)}"
            return match.group(0)
        text = self.date_day_month_pattern.sub(replace_day_month, text)
        
        return text
    
    def convert_standalone_numbers(self, text: str) -> str:
        """Convert remaining standalone numbers to words"""
        def replace_standalone(match):
            return self.number_to_words(match.group(0))
        return self.standalone_number_pattern.sub(replace_standalone, text)
    
    def clean_text_for_tts(self, text: str) -> str:
        """Clean text: remove emojis, special chars"""
        # Remove emojis
        text = self.emoji_pattern.sub('', text)
        
        # Remove special characters (combine multiple operations)
        text = re.sub(r'[\\()¯"""]', '', text)  # Combined pattern
        text = re.sub(r'\s—', '.', text)
        text = re.sub(r'\b_\b', ' ', text)
        # Remove dashes but preserve those between numbers
        text = re.sub(r'(?<!\d)-(?!\d)', ' ', text)
        # Keep only Latin, Vietnamese, numbers, punctuation, whitespace
        text = re.sub(r'[^\u0000-\u024F\u1E00-\u1EFF]', '', text)
        return text.strip()
    
    def process_vietnamese_text(self, text: str) -> str:
        """Main function to process Vietnamese text for TTS"""
        if not text:
            return ''
        
        # Step 1: Normalize Unicode
        text = unicodedata.normalize('NFC', text)
        
        # Step 2: Clean text
        text = self.clean_text_for_tts(text)
        
        # Step 3: Remove thousand separators
        text = self.remove_thousand_separators(text)
        
        # Step 4: Convert dates
        text = self.convert_date(text)
        
        # Step 5: Convert times
        text = self.convert_time(text)
        
        # Step 6: Convert currency
        text = self.convert_currency(text)
        
        # Step 7: Convert percentages
        text = self.convert_percentage(text)
        
        # Step 8: Convert decimals
        text = self.convert_decimal(text)
        
        # Step 9: Convert remaining standalone numbers
        text = self.convert_standalone_numbers(text)
        
        # Step 10: Clean whitespace
        text = self.whitespace_pattern.sub(' ', text).strip()
        
        return text


class Predictor(BasePredictor):
    """Vietnamese TTS predictor using Piper."""

    def setup(self):
        """Load models and normalization dictionaries."""
        # Load ONNX models
        self.models = {
            "ngochuyen": "ngochuyen.onnx",
            "tranthanh": "tranthanh3870.onnx",
        }
        
        # Load voices (lazy loading)
        self.voices = {}
        
        # Load normalization dictionaries
        self.acronym_map = self._load_acronyms()
        self.non_vietnamese_map = self._load_non_vietnamese_words()
        
        # Pre-compile regex patterns for performance
        self._compile_regex_patterns()
        
        # Cache model configs
        self.model_configs = {}
        for model_name, model_path in self.models.items():
            config_path = Path(model_path).with_suffix('.onnx.json')
            if config_path.exists():
                import json
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.model_configs[model_name] = json.load(f)
        
        # Initialize Vietnamese text processor
        self.vn_processor = VietnameseTextProcessor()
    
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
            escaped_acronym = re.sub(r'[+?^${}()|[\]\\]', r'\\\g<0>', acronym)
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
    
    def _load_acronyms(self) -> Dict[str, str]:
        """Load acronym mappings from CSV."""
        acronym_map = {}
        acronyms_path = Path("public/acronyms.csv")
        
        if acronyms_path.exists():
            with open(acronyms_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    acronym = row.get("acronym", "").strip().lower()
                    transliteration = row.get("transliteration", "").strip()
                    if acronym and transliteration:
                        acronym_map[acronym] = transliteration
        
        # Sort by length (longest first) for proper matching priority
        return dict(sorted(acronym_map.items(), key=lambda x: len(x[0]), reverse=True))
    
    def _load_non_vietnamese_words(self) -> Dict[str, str]:
        """Load non-Vietnamese word mappings from CSV."""
        word_map = {}
        words_path = Path("public/non-vietnamese-words.csv")
        
        if words_path.exists():
            with open(words_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word = row.get("word", "").strip().lower()
                    pronunciation = row.get("vietnamese_pronunciation", "").strip()
                    if word and pronunciation:
                        word_map[word] = pronunciation
        
        # Sort by length (longest first) for proper matching priority
        return dict(sorted(word_map.items(), key=lambda x: len(x[0]), reverse=True))
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text following the pipeline from text-cleaner.js:
        1. Clean text (remove emojis, special chars)
        2. Process Vietnamese text (numbers, dates, times, etc.)
        3. Replace non-Vietnamese words from CSV
        4. Convert acronyms
        """
        if not text:
            return ''
        
        # Step 1: Process Vietnamese text (numbers, dates, times, etc.)
        # This also includes text cleaning
        normalized = self.vn_processor.process_vietnamese_text(text)
        
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
    
    def _get_voice(self, model_name: str) -> PiperVoice:
        """Get or load voice model."""
        if model_name not in self.voices:
            model_path = self.models.get(model_name)
            if not model_path or not Path(model_path).exists():
                raise ValueError(f"Model {model_name} not found: {model_path}")
            
            # Load model - Piper automatically finds and uses the .onnx.json config file
            # The config specifies "espeak": {"voice": "vi"} which tells Piper
            # to use Vietnamese phonemization internally
            self.voices[model_name] = PiperVoice.load(model_path)
        
        return self.voices[model_name]
    
    def predict(
        self,
        text: str = Input(description="Text to synthesize (Vietnamese)"),
        model: str = Input(
            description="Voice model to use",
            default="ngochuyen",
            choices=["ngochuyen", "tranthanh"]
        ),
        enable_preprocessing: bool = Input(
            description="Enable text preprocessing (normalization, number conversion, etc.). Set to false for faster processing if text is already normalized.",
            default=True
        ),
    ) -> CogPath:
        """
        Synthesize Vietnamese text to speech.
        
        Args:
            text: Input text to synthesize
            model: Voice model to use (ngochuyen or tranthanh)
            enable_preprocessing: If True, applies text normalization (numbers, dates, acronyms, etc.). 
                                  If False, uses text as-is for faster processing.
            
        Returns:
            Path to generated WAV file
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Normalize text using comprehensive pipeline (or skip if disabled)
        if enable_preprocessing:
            normalized_text = self._normalize_text(text)
        else:
            # Skip preprocessing - use text as-is (faster)
            normalized_text = text.strip()
        
        # Get voice model
        voice = self._get_voice(model)
        
        # Synthesize to WAV file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            wav_path = tmp_file.name
        
        try:
            # Synthesize to WAV file
            # Piper will handle phonemization internally using the voice from config
            with wave.open(wav_path, "wb") as wav_file:
                voice.synthesize_wav(normalized_text, wav_file)
            
            return CogPath(wav_path)
        except Exception as e:
            # Clean up on error
            if os.path.exists(wav_path):
                os.unlink(wav_path)
            raise
