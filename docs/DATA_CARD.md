# Data card

**Source:** FLORES+, the Open Language Data Initiative's maintained version of FLORES-200 (NLLB Team, 2022), from the gated Hugging Face dataset `openlanguagedata/flores_plus`. The exact dataset revision is written to `data/SOURCE.json` and `results/run_metadata.json`. The original FLORES-200 archive can be used instead with `download --source flores200`.

**Access conditions:** FLORES+ asks users not to re-host it where web crawlers can pick it up. This repository never stores the text: `data/` is git-ignored and results hold only metrics and sentence indices.

**Licence:** CC BY-SA 4.0. The raw text is not redistributed; `python -m turkicbridge.cli download` fetches it. Result files contain only metrics and sentence indices.

**Content:** professionally translated sentences from English Wikinews, Wikijunior and Wikivoyage articles. They are general-domain, not health, disaster or public-service text.

**Languages used:** Turkish (`tur_Latn`), North Azerbaijani (`azj_Latn`), Kazakh (`kaz_Cyrl`), Kyrgyz (`kir_Cyrl`), Northern Uzbek (`uzn_Latn`).

**Personal data:** none known.

**Known issue:** every sentence is a translation of the same English source, so the five versions are closer to each other than independently written text would be. Retrieval on FLORES is therefore easier than finding evidence in real documents written separately in each language.
