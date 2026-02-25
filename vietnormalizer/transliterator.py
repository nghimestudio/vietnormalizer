"""
English to Vietnamese Transliterator.

Ported from nghitts/src/utils/transliterator.js
Converts English words to Vietnamese phonetic transliteration using rule-based approach.
"""

import re
from .detector import is_vietnamese_word


# High priority rules: special endings and consonant clusters
HIGH_PRIORITY_RULES = [
    # Special word endings
    (re.compile(r'tion$'), 'ân'),
    (re.compile(r'sion$'), 'ân'),
    (re.compile(r'age$'), 'ây'),
    (re.compile(r'ing$'), 'ing'),
    (re.compile(r'ture$'), 'chờ'),
    (re.compile(r'cial$'), 'xô'),
    (re.compile(r'tial$'), 'xô'),

    # Complex vowel combinations
    (re.compile(r'aught'), 'ót'),
    (re.compile(r'ought'), 'ót'),
    (re.compile(r'ound'), 'ao'),
    (re.compile(r'ight'), 'ai'),
    (re.compile(r'eigh'), 'ây'),
    (re.compile(r'ough'), 'ao'),

    # Initial consonant clusters
    (re.compile(r'\bst(?!r)'), 't'),
    (re.compile(r'\bstr'), 'tr'),
    (re.compile(r'\bsch'), 'c'),
    (re.compile(r'\bsc(?=h)'), 'c'),
    (re.compile(r'\bsc|\bsk'), 'c'),
    (re.compile(r'\bsp'), 'p'),
    (re.compile(r'\btr'), 'tr'),
    (re.compile(r'\bbr'), 'r'),
    (re.compile(r'\bcr|\bpr|\bgr|\bdr|\bfr'), 'r'),
    (re.compile(r'\bbl|\bcl|\bsl|\bpl'), 'l'),
    (re.compile(r'\bfl'), 'ph'),

    # Double consonants
    (re.compile(r'ck'), 'c'),
    (re.compile(r'sh'), 's'),
    (re.compile(r'ch'), 'ch'),
    (re.compile(r'th'), 'th'),
    (re.compile(r'ph'), 'ph'),
    (re.compile(r'wh'), 'q'),
    (re.compile(r'qu'), 'q'),
    (re.compile(r'kn'), 'n'),
    (re.compile(r'wr'), 'r'),
]

# Ending rules: only apply at end of word
ENDING_RULES = [
    (re.compile(r'le$'), 'ồ'),

    # Vowel + consonant endings
    (re.compile(r'ook$'), 'úc'),
    (re.compile(r'ood$'), 'út'),
    (re.compile(r'ool$'), 'un'),
    (re.compile(r'oom$'), 'um'),
    (re.compile(r'oon$'), 'un'),
    (re.compile(r'oot$'), 'út'),
    (re.compile(r'iend$'), 'en'),
    (re.compile(r'end$'), 'en'),
    (re.compile(r'eau$'), 'iu'),

    (re.compile(r'ail$'), 'ain'),
    (re.compile(r'ain$'), 'ain'),
    (re.compile(r'ait$'), 'ât'),

    (re.compile(r'oat$'), 'ốt'),
    (re.compile(r'oad$'), 'ốt'),
    (re.compile(r'oal$'), 'ôn'),

    (re.compile(r'eep$'), 'íp'),
    (re.compile(r'eet$'), 'ít'),
    (re.compile(r'eel$'), 'in'),

    # -TCH endings
    (re.compile(r'atch$'), 'át'),
    (re.compile(r'etch$'), 'éch'),
    (re.compile(r'itch$'), 'ích'),
    (re.compile(r'otch$'), 'ốt'),
    (re.compile(r'utch$'), 'út'),

    # -DGE endings
    (re.compile(r'edge$'), 'ét'),
    (re.compile(r'idge$'), 'ít'),
    (re.compile(r'odge$'), 'ót'),
    (re.compile(r'udge$'), 'út'),

    # -CK/-K endings
    (re.compile(r'ack$'), 'ác'),
    (re.compile(r'eck$'), 'éc'),
    (re.compile(r'ick$'), 'ích'),
    (re.compile(r'ock$'), 'óc'),
    (re.compile(r'uck$'), 'úc'),

    # -SH endings
    (re.compile(r'ash$'), 'át'),
    (re.compile(r'esh$'), 'ét'),
    (re.compile(r'ish$'), 'ít'),
    (re.compile(r'osh$'), 'ốt'),
    (re.compile(r'ush$'), 'út'),

    # -TH endings
    (re.compile(r'ath$'), 'át'),
    (re.compile(r'eth$'), 'ét'),
    (re.compile(r'ith$'), 'ít'),
    (re.compile(r'oth$'), 'ót'),
    (re.compile(r'uth$'), 'út'),

    # -TE endings (silent E)
    (re.compile(r'ate$'), 'ây'),
    (re.compile(r'ete$'), 'ét'),
    (re.compile(r'ite$'), 'ai'),
    (re.compile(r'ote$'), 'ốt'),
    (re.compile(r'ute$'), 'út'),

    # -DE endings
    (re.compile(r'ade$'), 'ây'),
    (re.compile(r'ede$'), 'ét'),
    (re.compile(r'ide$'), 'ai'),
    (re.compile(r'ode$'), 'ốt'),
    (re.compile(r'ude$'), 'út'),

    # Silent-E endings
    (re.compile(r'ake$'), 'ây'),
    (re.compile(r'ame$'), 'am'),
    (re.compile(r'ane$'), 'an'),
    (re.compile(r'ape$'), 'ếp'),
    (re.compile(r'eke$'), 'ét'),
    (re.compile(r'eme$'), 'êm'),
    (re.compile(r'ene$'), 'en'),
    (re.compile(r'ike$'), 'íc'),
    (re.compile(r'ime$'), 'am'),
    (re.compile(r'ine$'), 'ai'),
    (re.compile(r'oke$'), 'ốc'),
    (re.compile(r'ome$'), 'om'),
    (re.compile(r'one$'), 'oăn'),
    (re.compile(r'uke$'), 'ấc'),
    (re.compile(r'ume$'), 'uym'),
    (re.compile(r'une$'), 'uyn'),

    # -SE endings
    (re.compile(r'ase$'), 'ây'),
    (re.compile(r'ise$'), 'ai'),
    (re.compile(r'ose$'), 'âu'),

    # -LL endings
    (re.compile(r'all$'), 'âu'),
    (re.compile(r'ell$'), 'eo'),
    (re.compile(r'ill$'), 'iu'),
    (re.compile(r'oll$'), 'ôn'),
    (re.compile(r'ull$'), 'un'),

    # -NG endings
    (re.compile(r'ang$'), 'ang'),
    (re.compile(r'eng$'), 'ing'),
    (re.compile(r'ong$'), 'ong'),
    (re.compile(r'ung$'), 'âng'),

    # Complex vowel endings
    (re.compile(r'air$'), 'e'),
    (re.compile(r'ear$'), 'ia'),
    (re.compile(r'ire$'), 'ai'),
    (re.compile(r'ure$'), 'iu'),
    (re.compile(r'our$'), 'ao'),
    (re.compile(r'ore$'), 'o'),
    (re.compile(r'ound$'), 'ao'),
    (re.compile(r'ight$'), 'ai'),
    (re.compile(r'aught$'), 'ót'),
    (re.compile(r'ought$'), 'ót'),
    (re.compile(r'eigh$'), 'ây'),
    (re.compile(r'ork$'), 'ót'),

    # Double vowel endings
    (re.compile(r'ee$'), 'i'),
    (re.compile(r'ea$'), 'i'),
    (re.compile(r'oo$'), 'u'),
    (re.compile(r'oa$'), 'oa'),
    (re.compile(r'oe$'), 'oe'),
    (re.compile(r'ai$'), 'ai'),
    (re.compile(r'ay$'), 'ay'),
    (re.compile(r'au$'), 'au'),
    (re.compile(r'aw$'), 'â'),
    (re.compile(r'ei$'), 'ây'),
    (re.compile(r'ey$'), 'ây'),
    (re.compile(r'oi$'), 'oi'),
    (re.compile(r'oy$'), 'oi'),
    (re.compile(r'ou$'), 'u'),
    (re.compile(r'ow$'), 'ô'),
    (re.compile(r'ue$'), 'ue'),
    (re.compile(r'ui$'), 'ui'),
    (re.compile(r'ie$'), 'ai'),
    (re.compile(r'eu$'), 'iu'),

    # -R endings
    (re.compile(r'ar$'), 'a'),
    (re.compile(r'er$'), 'ơ'),
    (re.compile(r'ir$'), 'ơ'),
    (re.compile(r'or$'), 'o'),
    (re.compile(r'ur$'), 'ơ'),

    # -L endings
    (re.compile(r'al$'), 'an'),
    (re.compile(r'el$'), 'eo'),
    (re.compile(r'il$'), 'iu'),
    (re.compile(r'ol$'), 'ôn'),
    (re.compile(r'ul$'), 'un'),

    # Basic closed syllable endings
    (re.compile(r'ab$'), 'áp'),
    (re.compile(r'ad$'), 'át'),
    (re.compile(r'ag$'), 'ác'),
    (re.compile(r'ak$'), 'át'),
    (re.compile(r'ap$'), 'áp'),
    (re.compile(r'at$'), 'át'),
    (re.compile(r'eb$'), 'ép'),
    (re.compile(r'ed$'), 'ét'),
    (re.compile(r'eg$'), 'ét'),
    (re.compile(r'ek$'), 'éc'),
    (re.compile(r'ep$'), 'ép'),
    (re.compile(r'et$'), 'ét'),
    (re.compile(r'ib$'), 'íp'),
    (re.compile(r'id$'), 'ít'),
    (re.compile(r'ig$'), 'íc'),
    (re.compile(r'ik$'), 'íc'),
    (re.compile(r'ip$'), 'íp'),
    (re.compile(r'it$'), 'ít'),
    (re.compile(r'ob$'), 'óp'),
    (re.compile(r'od$'), 'ót'),
    (re.compile(r'og$'), 'óc'),
    (re.compile(r'ok$'), 'óc'),
    (re.compile(r'op$'), 'óp'),
    (re.compile(r'ot$'), 'ót'),
    (re.compile(r'ub$'), 'úp'),
    (re.compile(r'ud$'), 'út'),
    (re.compile(r'ug$'), 'úc'),
    (re.compile(r'uk$'), 'úc'),
    (re.compile(r'up$'), 'úp'),
    (re.compile(r'ut$'), 'út'),

    # -M/-N endings
    (re.compile(r'am$'), 'am'),
    (re.compile(r'an$'), 'an'),
    (re.compile(r'em$'), 'em'),
    (re.compile(r'en$'), 'en'),
    (re.compile(r'im$'), 'im'),
    (re.compile(r'in$'), 'in'),
    (re.compile(r'om$'), 'om'),
    (re.compile(r'on$'), 'on'),
    (re.compile(r'um$'), 'âm'),
    (re.compile(r'un$'), 'ân'),

    # -S endings
    (re.compile(r'as$'), 'ẹt'),
    (re.compile(r'es$'), 'ẹt'),
    (re.compile(r'is$'), 'ít'),
    (re.compile(r'os$'), 'ọt'),
    (re.compile(r'us$'), 'ợt'),

    # Double vowels
    (re.compile(r'aa$'), 'a'),
    (re.compile(r'ii$'), 'i'),
    (re.compile(r'uu$'), 'u'),
]

# General rules for single characters or mid-word positions
GENERAL_RULES = [
    (re.compile(r'j'), 'd'),
    (re.compile(r'z'), 'd'),
    (re.compile(r'w'), 'u'),
    (re.compile(r'x'), 'x'),
    (re.compile(r'v'), 'v'),
    (re.compile(r'f'), 'ph'),
    (re.compile(r's'), 'x'),
    (re.compile(r'c'), 'k'),
    (re.compile(r'q'), 'ku'),

    (re.compile(r'a'), 'a'),
    (re.compile(r'e'), 'e'),
    (re.compile(r'i'), 'i'),
    (re.compile(r'o'), 'o'),
    (re.compile(r'u'), 'u'),
]

_VOWELS = 'aeiouăâêôơưáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ'
_SYLLABLE_PATTERN = re.compile(f'([^{_VOWELS}]*[{_VOWELS}]+[ptcmngs]?(?![{_VOWELS}]))')
_CONSONANT_Y_PATTERN = re.compile(r'([bcdfghjklmnpqrstvwxz])y')
_Y_END_PATTERN = re.compile(r'y$')
_DOUBLE_CONSONANT_PATTERN = re.compile(r'([brlptdgmnckxsvfzjwqh])\1+')
_VALID_CONSONANT_PAIRS = {'ch', 'th', 'ph', 'sh', 'ng', 'tr', 'nh', 'gh', 'kh'}
_CONSONANTS = set('bcdfghjklmnpqrstvwxz')
_VALID_ENDINGS = {'p', 't', 'c', 'm', 'n', 'g', 's'}


def _apply_rules(w, rules):
    for pattern, replacement in rules:
        w = pattern.sub(replacement, w)
    return w


def _clean_consonant_clusters(p):
    """Remove invalid consonant clusters, keeping only valid Vietnamese pairs."""
    p = _DOUBLE_CONSONANT_PATTERN.sub(r'\1', p)

    result = []
    i = 0
    while i < len(p):
        if i < len(p) - 1 and p[i] in _CONSONANTS and p[i + 1] in _CONSONANTS:
            pair = p[i] + p[i + 1]
            if pair in _VALID_CONSONANT_PAIRS:
                result.append(pair)
                i += 2
            else:
                result.append(p[i + 1])
                i += 2
        else:
            result.append(p[i])
            i += 1
    return ''.join(result)


def _apply_ck_rule(p):
    """Apply C/K rule: use K before i, e, y."""
    if p.startswith(('ch', 'th', 'ph', 'sh')):
        return p
    if p.startswith(('k', 'c')):
        next_char = p[1:2]
        use_k = next_char in ('i', 'e', 'y')
        return ('k' if use_k else 'c') + p[1:]
    return p


def _filter_ending(p):
    """Filter invalid ending consonants."""
    if len(p) > 1 and p[-1] not in _VOWELS:
        last = p[-1]
        if last not in _VALID_ENDINGS:
            if last == 'l':
                return p[:-1] + 'n'
            return p[:-1]
    return p


def _process_syllable(s):
    """Process a single syllable: apply all rules and clean up."""
    if not s:
        return ""
    s = s.strip()
    if not s:
        return ""

    if s.startswith('y'):
        s = 'd' + s[1:]

    s = _apply_rules(s, HIGH_PRIORITY_RULES)
    s = _apply_rules(s, ENDING_RULES)
    s = _apply_rules(s, GENERAL_RULES)

    s = _CONSONANT_Y_PATTERN.sub(r'\1i', s)
    s = _Y_END_PATTERN.sub('i', s)

    s = _clean_consonant_clusters(s)
    s = _apply_ck_rule(s)
    s = _filter_ending(s)

    return s


def english_to_vietnamese(word: str) -> str:
    """Convert an English word to Vietnamese transliteration."""
    if not word:
        return ""

    w = word.lower().strip()

    if w.startswith('y'):
        w = 'd' + w[1:]
    if w.startswith('d'):
        w = 'đ' + w[1:]

    w = _apply_rules(w, HIGH_PRIORITY_RULES)
    w = _apply_rules(w, ENDING_RULES)
    w = _apply_rules(w, GENERAL_RULES)

    w = _CONSONANT_Y_PATTERN.sub(r'\1i', w)
    w = _Y_END_PATTERN.sub('i', w)

    parts = _SYLLABLE_PATTERN.findall(w)
    if not parts:
        return w

    final_parts = [_process_syllable(p) for p in parts]
    final_parts = [p for p in final_parts if p]

    return '-'.join(final_parts)


def transliterate_word(word: str) -> str:
    """
    Transliterate a word from English to Vietnamese.
    If the word is already Vietnamese, returns it unchanged.
    """
    if not word or not isinstance(word, str):
        return word or ''

    if is_vietnamese_word(word):
        return word

    return english_to_vietnamese(word)
