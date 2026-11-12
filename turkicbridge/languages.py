"""The five languages in v0.1 and their FLORES-200 codes."""

LANGUAGES = {
    "tur": ("tur_Latn", "Turkish"),
    "azj": ("azj_Latn", "North Azerbaijani"),
    "kaz": ("kaz_Cyrl", "Kazakh"),
    "kir": ("kir_Cyrl", "Kyrgyz"),
    "uzn": ("uzn_Latn", "Northern Uzbek"),
}

CYRILLIC = {code for code, (flores, _) in LANGUAGES.items() if flores.endswith("Cyrl")}


def flores_code(lang):
    if lang not in LANGUAGES:
        raise ValueError("Unsupported language %r; choose from %s" % (lang, ", ".join(LANGUAGES)))
    return LANGUAGES[lang][0]


def directed_pairs():
    return [(a, b) for a in LANGUAGES for b in LANGUAGES if a != b]
