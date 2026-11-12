# TurkicBridge AI

Someone asks a question in Kazakh. The best evidence exists, but only in Turkish or Uzbek, and in a different script. Can a retriever find it, and can it say "I found nothing" when there is nothing to find?

TurkicBridge v0.1 measures exactly that for five Turkic languages: Turkish, North Azerbaijani, Kazakh, Kyrgyz and Northern Uzbek. Two of them are written in Cyrillic and three in Latin script, so half of the language pairs cross scripts.

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

## Results

Not filled in yet. They are produced by the commands below and written to `results/`. No number is reported here until it comes from that run.

## Run it

Python 3.9 or newer. The lexical methods run on a laptop CPU in a few minutes.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -c "from huggingface_hub import login; login()"
python -m turkicbridge.cli download
python -m turkicbridge.cli run
```

FLORES+ is gated: first open https://huggingface.co/datasets/openlanguagedata/flores_plus while logged in and accept its conditions, then log in from the terminal with a Hugging Face read token (the `login()` line asks for it). `download` fetches only the ten files needed into `data/` and records the dataset revision. `run` writes `results/pairs.csv`, `results/summary.csv`, `results/tables.md` and `results/run_metadata.json`.

Optional sentence-embedding methods (downloads the models from Hugging Face on first use):

```bash
pip install -r requirements-dense.txt
python -m turkicbridge.cli run --methods word_raw char_raw char_latin char_folded e5_small labse
```

## Using the agent

```python
from turkicbridge.agent import TurkicBridgeAgent

corpus = [("Қазақстан астанасы Астана.", "doc-1"), ("Алматы ең үлкен қала.", "doc-2")]
agent = TurkicBridgeAgent(corpus, "kaz", method="char_folded", confidence="margin", threshold=0.05)
print(agent.answer("Kazakistan'ın başkenti Astana.", "tur"))
```

Use a threshold chosen on your own held-out data. The value above is only an example.

## Layout

```
turkicbridge/   languages, normalise, data, retrievers, evaluate, agent, experiment, cli
tests/          unit and pipeline tests on a small made-up fixture (no download needed)
docs/           protocol, data card, limitations and ethics, references
results/        output of the run above
```

## Limits

FLORES sentences are translations of the same English text, which makes retrieval easier than with documents written separately in each language. The transliteration is a simple hand-written mapping. See `docs/LIMITATIONS_AND_ETHICS.md`.

## Data and licence

Code: MIT. FLORES+: CC BY-SA 4.0, downloaded at run time and never stored in this repository.

## Citation

See `CITATION.cff`.
