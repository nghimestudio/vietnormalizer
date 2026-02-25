"""
Vietnamese Text Processor - Core text processing functionality.

Ported from nghitts/src/utils/vietnamese-processor.js
Provides conversion for numbers, dates, times, currency, percentages,
measurement units, ordinals, phone numbers, and text cleaning.
"""

import re
import unicodedata
from typing import Dict


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

    UNIT_MAP = {
        # Length
        'cm': 'xăng-ti-mét', 'mm': 'mi-li-mét', 'km': 'ki-lô-mét',
        'dm': 'đề-xi-mét', 'hm': 'héc-tô-mét', 'dam': 'đề-ca-mét',
        'm': 'mét', 'inch': 'in',
        # Weight
        'kg': 'ki-lô-gam', 'mg': 'mi-li-gam', 'g': 'gam',
        't': 'tấn', 'tấn': 'tấn', 'yến': 'yến', 'lạng': 'lạng',
        # Volume
        'ml': 'mi-li-lít', 'l': 'lít', 'lít': 'lít',
        # Area
        'm²': 'mét vuông', 'm2': 'mét vuông',
        'km²': 'ki-lô-mét vuông', 'km2': 'ki-lô-mét vuông',
        'ha': 'héc-ta',
        'cm²': 'xăng-ti-mét vuông', 'cm2': 'xăng-ti-mét vuông',
        # Cubic
        'm³': 'mét khối', 'm3': 'mét khối',
        'cm³': 'xăng-ti-mét khối', 'cm3': 'xăng-ti-mét khối',
        'km³': 'ki-lô-mét khối', 'km3': 'ki-lô-mét khối',
        # Time
        's': 'giây', 'sec': 'giây', 'min': 'phút',
        'h': 'giờ', 'hr': 'giờ', 'hrs': 'giờ',
        # Speed
        'km/h': 'ki-lô-mét trên giờ', 'kmh': 'ki-lô-mét trên giờ',
        'm/s': 'mét trên giây', 'ms': 'mét trên giây',
        'mm/h': 'mi-li-mét trên giờ', 'cm/s': 'xăng-ti-mét trên giây',
        # Temperature
        '°C': 'độ C', '°F': 'độ F', '°K': 'độ K',
        '°R': 'độ R', '°Re': 'độ Re', '°Ro': 'độ Ro',
        '°N': 'độ N', '°D': 'độ D',
    }
    
    def __init__(self):
        """Pre-compile regex patterns for performance."""
        self.emoji_pattern = re.compile(
            r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|'
            r'[\U0001F1E0-\U0001F1FF]|[\u2600-\u26FF]|[\u2700-\u27BF]|'
            r'[\U0001F900-\U0001F9FF]|[\U0001F018-\U0001F270]|[\u238C-\u2454]|'
            r'[\u20D0-\u20FF]|[\uFE0F]|[\u200D]',
            flags=re.UNICODE
        )
        
        self.thousand_sep_pattern = re.compile(r'(\d{1,3}(?:\.\d{3})+)(?=\s|$|[^\d.,])')
        self.decimal_pattern = re.compile(r'(\d+),(\d+)(?=\s|$|[^\d,])')
        self.percentage_range_pattern = re.compile(r'(\d+)\s*[-–—]\s*(\d+)\s*%')
        self.percentage_decimal_pattern = re.compile(r'(\d+),(\d+)\s*%')
        self.percentage_pattern = re.compile(r'(\d+)\s*%')
        self.standalone_number_pattern = re.compile(r'\b\d+\b')
        self.whitespace_pattern = re.compile(r'\s+')
        
        # Time patterns
        self.time_hms_pattern = re.compile(r'(\d{1,2}):(\d{2})(?::(\d{2}))?')
        self.time_hhmm_pattern = re.compile(r'(\d{1,2})h(\d{2})(?![a-zà-ỹ])', re.IGNORECASE)
        self.time_h_pattern = re.compile(r'(\d{1,2})h(?![a-zà-ỹ\d])', re.IGNORECASE)
        self.time_giophut_pattern = re.compile(r'(\d+)\s*giờ\s*(\d+)\s*phút')
        self.time_gio_pattern = re.compile(r'(\d+)\s*giờ(?!\s*\d)')
        
        # Date patterns (including ranges)
        self.date_ngay_range_pattern = re.compile(
            r'ngày\s+(\d{1,2})\s*[-–—]\s*(\d{1,2})\s*[/-]\s*(\d{1,2})(?:\s*[/-]\s*(\d{4}))?'
        )
        self.date_range_pattern = re.compile(
            r'(\d{1,2})\s*[-–—]\s*(\d{1,2})\s*[/-]\s*(\d{1,2})(?:\s*[/-]\s*(\d{4}))?'
        )
        self.month_range_pattern = re.compile(r'(\d{1,2})\s*[-–—]\s*(\d{1,2})\s*[/-]\s*(\d{4})')
        self.date_sinh_pattern = re.compile(
            r'(Sinh|sinh)\s+ngày\s+(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
        )
        self.date_full_pattern = re.compile(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})')
        self.date_month_year_pattern = re.compile(
            r'(?:tháng\s+)?(\d{1,2})\s*[/-]\s*(\d{4})(?![\/-]\d)'
        )
        self.date_day_month_pattern = re.compile(
            r'(\d{1,2})\s*[/-]\s*(\d{1,2})(?![\/-]\d)(?!\d+\s*%)'
        )
        self.date_x_thang_y_pattern = re.compile(r'(\d+)\s*tháng\s*(\d+)')
        self.date_thang_x_pattern = re.compile(r'tháng\s*(\d+)')
        self.date_ngay_x_pattern = re.compile(r'ngày\s*(\d+)')
        
        # Currency patterns
        self.currency_vnd_pattern1 = re.compile(r'(\d+(?:,\d+)?)\s*(?:đồng|VND|vnđ)\b', re.IGNORECASE)
        self.currency_vnd_pattern2 = re.compile(r'(\d+(?:,\d+)?)đ(?![a-zà-ỹ])', re.IGNORECASE)
        self.currency_usd_pattern1 = re.compile(r'\$\s*(\d+(?:,\d+)?)')
        self.currency_usd_pattern2 = re.compile(r'(\d+(?:,\d+)?)\s*(?:USD|\$)', re.IGNORECASE)
        
        # Year range pattern
        self.year_range_pattern = re.compile(r'(\d{4})\s*[-–—]\s*(\d{4})')
        
        # Ordinal pattern
        self.ordinal_pattern = re.compile(r'(thứ|lần|bước|phần|chương|tập|số)\s*(\d+)', re.IGNORECASE)
        self.ordinal_map = {
            '1': 'nhất', '2': 'hai', '3': 'ba', '4': 'tư', '5': 'năm',
            '6': 'sáu', '7': 'bảy', '8': 'tám', '9': 'chín', '10': 'mười'
        }
        
        # Phone number patterns
        self.phone_vn_pattern = re.compile(r'0\d{9,10}')
        self.phone_intl_pattern = re.compile(r'\+84\d{9,10}')
        
        # Roman numeral pattern: 2+ uppercase [IVXLC] at word boundaries
        self.roman_numeral_pattern = re.compile(r'\b([IVXLC]{2,})\b')
        self.roman_values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100}
        
        # Pre-compile measurement unit patterns (sorted longest first)
        self._compile_unit_patterns()
    
    def _compile_unit_patterns(self):
        """Pre-compile measurement unit regex patterns."""
        sorted_units = sorted(self.UNIT_MAP.keys(), key=len, reverse=True)
        self.unit_patterns = []
        
        for unit in sorted_units:
            escaped = re.escape(unit)
            if len(unit) == 1:
                pattern = re.compile(
                    rf'(\d+)\s*{escaped}(?!\s*[a-zA-Zà-ỹ])(?=\s*[^a-zA-Zà-ỹ]|$)',
                    re.IGNORECASE
                )
            else:
                pattern = re.compile(
                    rf'(\d+)\s*{escaped}(?=\s|[^\w]|$)',
                    re.IGNORECASE
                )
            self.unit_patterns.append((unit, pattern))
    
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
        """Convert percentages: 50% -> năm mươi phần trăm, 3-5% -> ba đến năm phần trăm"""
        # Handle percentage ranges first (e.g., "3-5%")
        def replace_range(match):
            num1, num2 = match.group(1), match.group(2)
            return f"{self.number_to_words(num1)} đến {self.number_to_words(num2)} phần trăm"
        text = self.percentage_range_pattern.sub(replace_range, text)
        
        # Handle decimals (e.g., "3,2%")
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
        """Convert currency amounts."""
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
            hour, minute, second = match.group(1), match.group(2), match.group(3)
            result = self.number_to_words(hour) + ' giờ'
            if minute:
                result += ' ' + self.number_to_words(minute) + ' phút'
            if second:
                result += ' ' + self.number_to_words(second) + ' giây'
            return result
        text = self.time_hms_pattern.sub(replace_hms, text)
        
        def replace_hhmm(match):
            hour, minute = match.group(1), match.group(2)
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
            hour, minute = match.group(1), match.group(2)
            return self.number_to_words(hour) + ' giờ ' + self.number_to_words(minute) + ' phút'
        text = self.time_giophut_pattern.sub(replace_giophut, text)
        
        def replace_gio(match):
            return self.number_to_words(match.group(1)) + ' giờ'
        text = self.time_gio_pattern.sub(replace_gio, text)
        return text
    
    def convert_year_range(self, text: str) -> str:
        """Convert year ranges: 1873-1907 -> một nghìn... đến một nghìn..."""
        def replace(match):
            return self.number_to_words(match.group(1)) + ' đến ' + self.number_to_words(match.group(2))
        return self.year_range_pattern.sub(replace, text)
    
    def convert_date(self, text: str) -> str:
        """Convert date expressions including date ranges."""
        def is_valid_date(day: str, month: str, year: str = None) -> bool:
            d, m = int(day), int(month)
            if year:
                y = int(year)
                return 1 <= d <= 31 and 1 <= m <= 12 and 1000 <= y <= 9999
            return 1 <= d <= 31 and 1 <= m <= 12
        
        def is_valid_month(month: str) -> bool:
            return 1 <= int(month) <= 12
        
        # Date range with "ngày" prefix: ngày dd-dd/mm or ngày dd-dd/mm/yyyy
        def replace_ngay_range(match):
            day1, day2, month, year = match.group(1), match.group(2), match.group(3), match.group(4)
            if is_valid_date(day1, month, year) and is_valid_date(day2, month, year):
                result = f"ngày {self.number_to_words(day1)} đến {self.number_to_words(day2)} tháng {self.number_to_words(month)}"
                if year:
                    result += f" năm {self.number_to_words(year)}"
                return result
            return match.group(0)
        text = self.date_ngay_range_pattern.sub(replace_ngay_range, text)
        
        # Date range without "ngày": dd-dd/mm or dd-dd/mm/yyyy
        def replace_date_range(match):
            day1, day2, month, year = match.group(1), match.group(2), match.group(3), match.group(4)
            if is_valid_date(day1, month, year) and is_valid_date(day2, month, year):
                result = f"{self.number_to_words(day1)} đến {self.number_to_words(day2)} tháng {self.number_to_words(month)}"
                if year:
                    result += f" năm {self.number_to_words(year)}"
                return result
            return match.group(0)
        text = self.date_range_pattern.sub(replace_date_range, text)
        
        # Month ranges: mm-mm/yyyy
        def replace_month_range(match):
            month1, month2, year = match.group(1), match.group(2), match.group(3)
            if is_valid_month(month1) and is_valid_month(month2):
                y = int(year)
                if 1000 <= y <= 9999:
                    return f"tháng {self.number_to_words(month1)} đến tháng {self.number_to_words(month2)} năm {self.number_to_words(year)}"
            return match.group(0)
        text = self.month_range_pattern.sub(replace_month_range, text)
        
        # "Sinh ngày DD/MM/YYYY"
        def replace_sinh(match):
            prefix, day, month, year = match.group(1), match.group(2), match.group(3), match.group(4)
            if is_valid_date(day, month, year):
                return f"{prefix} ngày {self.number_to_words(day)} tháng {self.number_to_words(month)} năm {self.number_to_words(year)}"
            return match.group(0)
        text = self.date_sinh_pattern.sub(replace_sinh, text)
        
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
        
        # DD/MM (with percentage exclusion check)
        def replace_day_month(match):
            day, month = match.group(1), match.group(2)
            if is_valid_date(day, month):
                return f"{self.number_to_words(day)} tháng {self.number_to_words(month)}"
            return match.group(0)
        text = self.date_day_month_pattern.sub(replace_day_month, text)
        
        # X tháng Y
        def replace_x_thang_y(match):
            day, month = match.group(1), match.group(2)
            if is_valid_date(day, month):
                return f"ngày {self.number_to_words(day)} tháng {self.number_to_words(month)}"
            return match.group(0)
        text = self.date_x_thang_y_pattern.sub(replace_x_thang_y, text)
        
        # tháng X
        def replace_thang_x(match):
            month = match.group(1)
            if is_valid_month(month):
                return 'tháng ' + self.number_to_words(month)
            return match.group(0)
        text = self.date_thang_x_pattern.sub(replace_thang_x, text)
        
        # ngày X
        def replace_ngay_x(match):
            day = match.group(1)
            d = int(day)
            if 1 <= d <= 31:
                return 'ngày ' + self.number_to_words(day)
            return match.group(0)
        text = self.date_ngay_x_pattern.sub(replace_ngay_x, text)
        
        return text
    
    def convert_ordinal(self, text: str) -> str:
        """Convert ordinals: thứ 2 -> thứ hai"""
        def replace(match):
            prefix, num = match.group(1), match.group(2)
            word = self.ordinal_map.get(num)
            if word:
                return prefix + ' ' + word
            return prefix + ' ' + self.number_to_words(num)
        return self.ordinal_pattern.sub(replace, text)
    
    def convert_phone_number(self, text: str) -> str:
        """Read phone numbers digit by digit."""
        def replace_phone(match):
            digits = re.findall(r'\d', match.group(0))
            return ' '.join(self.DIGITS.get(d, d) for d in digits)
        
        text = self.phone_vn_pattern.sub(replace_phone, text)
        text = self.phone_intl_pattern.sub(replace_phone, text)
        return text
    
    def convert_measurement_units(self, text: str) -> str:
        """Convert measurement units to Vietnamese names."""
        for unit, pattern in self.unit_patterns:
            def make_replacer(u):
                def replacer(match):
                    return match.group(1) + ' ' + self.UNIT_MAP[u]
                return replacer
            text = pattern.sub(make_replacer(unit), text)
        return text
    
    def _roman_to_int(self, s: str) -> int:
        """Convert a Roman numeral string to integer. Returns -1 if invalid."""
        if not s or not all(c in self.roman_values for c in s):
            return -1
        total = 0
        prev = 0
        for c in reversed(s):
            val = self.roman_values[c]
            if val < prev:
                total -= val
            else:
                total += val
            prev = val
        return total
    
    def convert_roman_numerals(self, text: str) -> str:
        """Convert uppercase Roman numerals (< 100) to Vietnamese words.
        Only matches sequences of 2+ uppercase Roman numeral characters."""
        def replace_roman(match):
            roman = match.group(1)
            value = self._roman_to_int(roman)
            if 1 <= value < 100:
                return self.number_to_words(str(value))
            return match.group(0)
        return self.roman_numeral_pattern.sub(replace_roman, text)
    
    def convert_standalone_numbers(self, text: str) -> str:
        """Convert remaining standalone numbers to words."""
        def replace_standalone(match):
            return self.number_to_words(match.group(0))
        return self.standalone_number_pattern.sub(replace_standalone, text)
    
    def remove_special_chars(self, text: str) -> str:
        """Remove or replace special characters that can't be spoken."""
        text = text.replace('&', ' và ')
        text = text.replace('@', ' a còng ')
        text = text.replace('#', ' thăng ')
        text = text.replace('*', '')
        text = text.replace('_', ' ')
        text = text.replace('~', '')
        text = text.replace('`', '')
        text = text.replace('^', '')
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'www\.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        return text
    
    def normalize_punctuation(self, text: str) -> str:
        """Normalize punctuation marks."""
        text = re.sub(r'[""„‟]', '"', text)
        text = re.sub(r'[''‚‛]', "'", text)
        text = re.sub(r'[–—−]', '-', text)
        text = re.sub(r'\.{3,}', '...', text)
        text = text.replace('…', '...')
        text = re.sub(r'([!?.]){2,}', r'\1', text)
        return text
    
    def clean_text_for_tts(self, text: str) -> str:
        """Clean text: remove emojis, special chars."""
        text = self.emoji_pattern.sub('', text)
        text = re.sub(r'[\\()¯"""]', '', text)
        text = re.sub(r'\s—', '.', text)
        text = re.sub(r'\b_\b', ' ', text)
        # Remove dashes but preserve those between numbers
        text = re.sub(r'(?<!\d)-(?!\d)', ' ', text)
        # Keep only Latin, Vietnamese, numbers, punctuation, whitespace
        text = re.sub(r'[^\u0000-\u024F\u1E00-\u1EFF]', '', text)
        return text.strip()
    
    def process_vietnamese_text(self, text: str) -> str:
        """
        Main function to process Vietnamese text for TTS.
        Applies all normalization steps in the correct order matching the source.
        """
        if not text:
            return ''
        
        # Step 1: Normalize Unicode
        text = unicodedata.normalize('NFC', text)
        
        # Step 2: Remove special characters (& -> và, @ -> a còng, URLs, emails)
        text = self.remove_special_chars(text)
        
        # Step 3: Normalize punctuation
        text = self.normalize_punctuation(text)
        
        # Step 4: Clean text (emojis, non-Latin chars)
        text = self.clean_text_for_tts(text)
        
        # Step 5: Convert year ranges (before other number conversions)
        text = self.convert_year_range(text)
        
        # Step 6: Convert percentage ranges BEFORE dates to avoid "3-5%" being matched as date
        text = self.percentage_range_pattern.sub(
            lambda m: f"{self.number_to_words(m.group(1))} đến {self.number_to_words(m.group(2))} phần trăm",
            text
        )
        
        # Step 7: Convert dates (including date ranges)
        text = self.convert_date(text)
        
        # Step 8: Convert times
        text = self.convert_time(text)
        
        # Step 9: Convert ordinals (thứ 2 -> thứ hai)
        text = self.convert_ordinal(text)
        
        # Step 10: Remove thousand separators
        text = self.remove_thousand_separators(text)
        
        # Step 11: Convert currency
        text = self.convert_currency(text)
        
        # Step 12: Convert percentages (decimals and whole numbers - ranges already handled)
        text = self.convert_percentage(text)
        
        # Step 13: Convert phone numbers
        text = self.convert_phone_number(text)
        
        # Step 14: Convert decimals
        text = self.convert_decimal(text)
        
        # Step 15: Convert measurement units
        text = self.convert_measurement_units(text)
        
        # Step 16: Convert Roman numerals (uppercase only, < 100)
        text = self.convert_roman_numerals(text)
        
        # Step 17: Convert remaining standalone numbers
        text = self.convert_standalone_numbers(text)
        
        # Step 18: Clean whitespace
        text = self.whitespace_pattern.sub(' ', text).strip()
        
        return text
