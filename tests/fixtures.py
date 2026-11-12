"""Tiny made-up parallel 'sentences' for tests. They are not real translations.

Kazakh and Kyrgyz lines are the Cyrillic spelling of the Turkish words, so a
retriever only matches them after transliteration.
"""
import io
import tarfile

WORDS = ["alma bala", "kitap mektep", "deniz kum", "taş yol", "su bulut", "at kuş",
         "dağ orman", "ev bahçe", "gün ay", "kar yağmur", "ekmek tuz", "yıldız gece"]
CYR = {"a": "а", "b": "б", "l": "л", "m": "м", "k": "к", "i": "и", "t": "т", "p": "п", "e": "е",
       "d": "д", "n": "н", "z": "з", "u": "у", "ş": "ш", "y": "й", "o": "о", "s": "с", "r": "р",
       "ğ": "ғ", "v": "в", "h": "һ", "ç": "ч", "g": "г", "ü": "ү", "ı": "ы", " ": " "}


def cyr(text):
    return "".join(CYR.get(ch, ch) for ch in text)


def corpus(n=12):
    lines = WORDS[:n]
    return {"tur": lines, "azj": [l + " ve" for l in lines], "uzn": [l.replace("ş", "sh") for l in lines],
            "kaz": [cyr(l) for l in lines], "kir": [cyr(l) + " да" for l in lines]}


def fake_archive(path):
    from oguztamga.languages import flores_code
    data = corpus()
    with tarfile.open(str(path), "w:gz") as tar:
        for split in ("dev", "devtest"):
            for lang, lines in data.items():
                raw = ("\n".join(lines) + "\n").encode("utf-8")
                info = tarfile.TarInfo("flores200_dataset/%s/%s.%s" % (split, flores_code(lang), split))
                info.size = len(raw)
                tar.addfile(info, io.BytesIO(raw))
