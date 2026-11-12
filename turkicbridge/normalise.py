"""Script and spelling normalisation for Turkic text.

Kazakh and Kyrgyz are written in Cyrillic, the other three in Latin script with
different spelling conventions. A lexical retriever cannot match words across
those differences, so `to_common_latin` maps everything to one rough Latin
spelling and `fold` drops the remaining diacritics. Both are deliberately simple
and lossy: they are a baseline, not a transliteration standard.
"""
import re
import unicodedata

_CYRILLIC_TO_LATIN = {
    "а": "a", "ә": "ä", "б": "b", "в": "v", "г": "g", "ғ": "ğ", "д": "d", "е": "e",
    "ё": "yo", "ж": "j", "з": "z", "и": "i", "й": "y", "к": "k", "қ": "q", "л": "l",
    "м": "m", "н": "n", "ң": "ñ", "о": "o", "ө": "ö", "п": "p", "р": "r", "с": "s",
    "т": "t", "у": "u", "ұ": "u", "ү": "ü", "ф": "f", "х": "x", "һ": "h", "ц": "ts",
    "ч": "ç", "ш": "ş", "щ": "şç", "ъ": "", "ы": "ı", "і": "i", "ь": "", "э": "e",
    "ю": "yu", "я": "ya",
}

# Uzbek Latin digraphs and apostrophe letters, mapped to the Turkish-style letter
_UZBEK = [("o'", "ö"), ("oʻ", "ö"), ("g'", "ğ"), ("gʻ", "ğ"), ("sh", "ş"), ("ch", "ç")]

_FOLD = str.maketrans({"ç": "c", "ş": "s", "ğ": "g", "ö": "o", "ü": "u", "ı": "i",
                       "ä": "e", "ə": "e", "ñ": "n", "q": "k", "x": "h", "w": "v"})


def lower(text):
    # Turkish dotted and dotless I: lowercase them before str.lower() adds a combining dot
    return text.replace("İ", "i").replace("I", "ı").lower()


def to_common_latin(text, lang):
    text = lower(text)
    if lang in ("kaz", "kir"):
        text = "".join(_CYRILLIC_TO_LATIN.get(ch, ch) for ch in text)
    elif lang == "uzn":
        for old, new in _UZBEK:
            text = text.replace(old, new)
    return text


def fold(text):
    text = unicodedata.normalize("NFC", text).translate(_FOLD)
    return re.sub(r"\s+", " ", text).strip()


def prepare(text, lang, mode):
    """mode: 'raw' (lowercase only), 'latin' (common Latin), 'folded' (common Latin, no diacritics)."""
    if mode == "raw":
        return lower(text)
    if mode == "latin":
        return to_common_latin(text, lang)
    if mode == "folded":
        return fold(to_common_latin(text, lang))
    raise ValueError("Unknown normalisation mode: %r" % mode)
