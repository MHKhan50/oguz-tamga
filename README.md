# OğuzTamga

*Evidence-stamped cross-lingual retrieval for Turkic languages*

Someone asks a question in Kazakh. The best evidence exists, but only in Turkish or Uzbek, and in a different script. Can a retriever find it, and can it say "I found nothing" when there is nothing to find?

OğuzTamga v0.1 measures exactly that for five Turkic languages: Turkish, North Azerbaijani, Kazakh, Kyrgyz and Northern Uzbek. Two of them are written in Cyrillic and three in Latin script, so 12 of the 20 directed language pairs cross scripts.

The agent never writes an answer. It returns a sentence from the target language with its source, or it abstains.

## What is tested

- **Closed set:** for each of the 20 directed language pairs, find the parallel FLORES+ sentence among about 1,000 candidates. Recall@1 and MRR.
- **Open set:** the true sentence is removed for half the queries. The agent must answer when evidence exists and abstain when it does not. The abstention threshold is set on the dev split and applied unchanged to devtest, over 5 seeds.

Methods:

| Method | Idea |
|---|---|
| `word_raw` | word TF-IDF |
| `char_raw` | character n-gram TF-IDF |
| `char_latin` | character n-grams after mapping Cyrillic and Uzbek spelling to one Latin form |
| `char_folded` | as above, diacritics removed |
| `e5_small`, `labse` | multilingual sentence embeddings (optional) |

Full protocol and hypotheses: `docs/EXPERIMENTAL_PROTOCOL.md`.

## Results (v0.1.0, lexical methods)

FLORES+ devtest, 1,012 sentences per language, 20 directed pairs, 5 seeds for the open-set test. Sentence-embedding results are not in yet.

**Closed set, Recall@1** (true sentence ranked first among about 1,000)

| Method | All pairs | Both Latin | Both Cyrillic | Cross-script |
|---|---|---|---|---|
| word_raw | 0.273 | 0.410 | 0.519 | 0.163 |
| char_raw | 0.398 | 0.703 | 0.831 | 0.173 |
| char_latin | 0.686 | 0.722 | 0.855 | 0.640 |
| char_folded | 0.725 | 0.768 | 0.899 | 0.674 |

- Mapping Kazakh and Kyrgyz Cyrillic to Latin and removing diacritics raised cross-script Recall@1 from 0.173 to 0.674 for the character retriever.
- It also helped pairs that share a script. For Latin pairs, the Uzbek spelling mapping took Recall@1 from 0.703 to 0.722 and removing diacritics to 0.768; for the Kazakh–Kyrgyz pairs it went from 0.831 to 0.899.

**Open set** (true sentence removed for half the queries; threshold set on dev)

| Method | Confidence | Right move | True evidence | Wrong evidence | Answered with no evidence |
|---|---|---|---|---|---|
| char_folded | margin | 0.715 ± 0.006 | 0.537 | 0.012 | 0.107 |
| char_folded | top1 | 0.696 ± 0.007 | 0.525 | 0.024 | 0.132 |
| char_latin | margin | 0.689 ± 0.006 | 0.482 | 0.013 | 0.105 |
| char_raw | margin | 0.608 ± 0.005 | 0.278 | 0.011 | 0.062 |
| word_raw | margin | 0.561 ± 0.004 | 0.188 | 0.016 | 0.065 |

- With the margin as its confidence, the best setup made the right move 71.5% of the time and returned a wrong sentence for 1.2% of answerable queries.
- It is cautious: when the evidence existed it still abstained on about 45% of queries, and when it did not exist it answered 10.7% of the time.
- The margin beat the top score for all three character methods; for word TF-IDF the two were level (0.561 against 0.564).

All rows, including `top1` for every method, are in `results/tables.md` and `results/summary.csv`.

## Run it

Python 3.9 or newer. The lexical methods run on a laptop CPU in a few minutes.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -c "from huggingface_hub import login; login()"
python -m oguztamga.cli download
python -m oguztamga.cli run
```

FLORES+ is gated: first open https://huggingface.co/datasets/openlanguagedata/flores_plus while logged in and accept its conditions, then log in from the terminal with a Hugging Face read token (the `login()` line asks for it). `download` fetches only the ten files needed into `data/` and records the dataset revision. `run` writes `results/pairs.csv`, `results/summary.csv`, `results/tables.md` and `results/run_metadata.json`.

Optional sentence-embedding methods (downloads the models from Hugging Face on first use):

```bash
pip install -r requirements-dense.txt
python -m oguztamga.cli run --methods word_raw char_raw char_latin char_folded e5_small labse
```

## Using the agent

```python
from oguztamga.agent import OguzTamgaAgent

corpus = [("Қазақстан астанасы Астана.", "doc-1"), ("Алматы ең үлкен қала.", "doc-2")]
agent = OguzTamgaAgent(corpus, "kaz", method="char_folded", confidence="margin", threshold=0.05)
print(agent.answer("Kazakistan'ın başkenti Astana.", "tur"))
```

Use a threshold chosen on your own held-out data. The value above is only an example.

## Layout

```
oguztamga/   languages, normalise, data, retrievers, evaluate, agent, experiment, cli
tests/          unit and pipeline tests on a small made-up fixture (no download needed)
docs/           protocol, data card, limitations and ethics, references
results/        output of the run above
```

## About the name

**Oğuz** honours Oğuz Kağan, remembered in Turkic tradition as a common forefather of the Turks. A **tamga** is the seal or mark a Turkic tribe used as its signature; Mahmud al-Kashgari's eleventh-century *Dīwān Lughāt al-Turk* records the tamgas of the Oghuz tribes. The agent works the same way: every answer carries the mark of its source, and where there is no evidence it leaves no mark.

The name is a tribute, not a linguistic grouping. The languages here come from three branches of the Turkic family: Oghuz (Turkish, Azerbaijani), Kipchak (Kazakh, Kyrgyz) and Karluk (Uzbek).

## Limits

FLORES sentences are translations of the same English text, which makes retrieval easier than with documents written separately in each language. The transliteration is a simple hand-written mapping. See `docs/LIMITATIONS_AND_ETHICS.md`.

## Data and licence

Code: MIT. FLORES+: CC BY-SA 4.0, downloaded at run time and never stored in this repository.

## Citation

See `CITATION.cff`.
