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

## Results (v0.1.0)

FLORES+ devtest, 1,012 sentences per language, 20 directed pairs; open-set test over 5 seeds.

**Closed set, Recall@1** (true sentence ranked first among about 1,000)

| Method | All pairs | Both Latin | Both Cyrillic | Cross-script |
|---|---|---|---|---|
| word_raw | 0.273 | 0.410 | 0.519 | 0.163 |
| char_raw | 0.398 | 0.703 | 0.831 | 0.173 |
| char_latin | 0.686 | 0.722 | 0.855 | 0.640 |
| char_folded | 0.725 | 0.768 | 0.899 | 0.674 |
| e5_small | 0.968 | 0.956 | 0.994 | 0.969 |
| labse | 0.998 | 0.998 | 0.998 | 0.998 |

**Open set** (true sentence removed for half the queries; threshold set on dev)

| Method | Confidence | Right move | True evidence | Wrong evidence | Answered with no evidence |
|---|---|---|---|---|---|
| word_raw | margin | 0.561 ± 0.004 | 0.188 | 0.016 | 0.065 |
| char_raw | margin | 0.608 ± 0.005 | 0.278 | 0.011 | 0.062 |
| char_folded | margin | 0.715 ± 0.006 | 0.537 | 0.012 | 0.107 |
| e5_small | top1 | 0.913 ± 0.002 | 0.889 | 0.012 | 0.063 |
| labse | margin | 0.980 ± 0.001 | 0.974 | 0.000 | 0.014 |

Each method is shown with its better confidence signal; every row is in `results/tables.md`.

What the numbers say:

- **Sentence embeddings win by a wide margin.** LaBSE found the right sentence 99.8% of the time in every script setting, e5-small 96.8%. The best lexical method reached 72.5%.
- **For lexical retrieval, transliteration matters a lot.** Mapping Kazakh and Kyrgyz Cyrillic to Latin and removing diacritics took cross-script Recall@1 of the character retriever from 0.173 to 0.674. For Latin pairs the Uzbek spelling mapping took it from 0.703 to 0.722, and removing diacritics to 0.768.
- **Abstention works when retrieval is strong.** With LaBSE the agent made the right move 98.0% of the time, returned a wrong sentence for 0.000 (to three decimals) of queries whose true sentence existed, and answered 1.4% of no-evidence queries.
- **Which confidence signal is better depends on the retriever.** The top-two margin beat the raw top score for all three character methods, tied for word TF-IDF and LaBSE, and was worse for e5-small (0.901 against 0.913).
- **Turkish as the target was hardest for e5-small:** Recall@1 into Turkish ranged from 0.872 to 0.942, against 0.950 or more for every other target. LaBSE showed no such gap. The cause is not tested here.

**What this does and does not show.** FLORES sentences are translations of the same English text, which makes them easy for embedding models trained on translation pairs; LaBSE is close to the ceiling here. These results say little about finding evidence in documents written separately in each language. That harder setting is the next version.

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
