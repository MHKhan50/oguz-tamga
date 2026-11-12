# Experimental protocol (v0.1.0)

## Question
Given a sentence in one Turkic language, can a retriever find the sentence with the same meaning in another Turkic language, and can it tell when no such sentence exists?

## Data
FLORES+ dev (997 sentences) and devtest (1,012 sentences) for `tur_Latn`, `azj_Latn`, `kaz_Cyrl`, `kir_Cyrl` and `uzn_Latn`. Line *i* is the same English source sentence translated into each language, so line *i* in the target language is the one correct piece of evidence for line *i* in the source language. The dataset revision is written to `results/run_metadata.json`. Sentences are aligned by their FLORES id.

## Pairs
All 20 directed pairs of the five languages, grouped as both Latin (6), both Cyrillic (2) and cross-script (12).

## Methods
| Name | What it does |
|---|---|
| `word_raw` | word TF-IDF on lowercased text |
| `char_raw` | character 2-4 gram TF-IDF on lowercased text |
| `char_latin` | as above after mapping Kazakh/Kyrgyz Cyrillic and Uzbek digraphs to one Latin spelling |
| `char_folded` | as above with remaining diacritics removed (ş→s, ı→i, q→k, ...) |
| `e5_small` | multilingual-e5-small sentence embeddings (optional) |
| `labse` | LaBSE sentence embeddings (optional) |

The lexical methods are fitted per pair on the union of the two sides. No method is trained on FLORES.

## Closed-set test
Every true sentence is in the pool. Metrics: Recall@1 and MRR on devtest. Ties count against the true sentence.

## Open-set test (abstention)
For half of the queries, chosen with a fixed seed, the true sentence is removed from the pool. The agent returns its top candidate if its confidence is at least a threshold, otherwise it abstains. Two confidence signals are compared: the top score (`top1`) and the gap between the top two scores (`margin`). The threshold is chosen on dev, with its own seeded mask, to maximise the share of right moves; it is then applied unchanged to devtest.

A right move is: answer with the true sentence when it exists, or abstain when it does not.

Reported on devtest: right-move rate, and separately for queries with evidence the share answered with the true sentence, answered with a wrong sentence and abstained; for queries without evidence the share that still got an answer.

## Seeds and uncertainty
Seeds 11, 23, 37, 41 and 53 control the masks (dev uses the seed, devtest uses seed + 1000). Values are averaged over pairs within a seed; the reported sd is across seeds. Closed-set metrics do not depend on the seed.

## What would count against the hypotheses
- H1: transliteration and folding raise cross-script Recall@1 of the character retriever. Refuted if `char_folded` is not above `char_raw` on cross-script pairs.
- H2: the margin is a better abstention signal than the top score. Refuted if `margin` does not give a higher right-move rate than `top1` for most methods.
- H3: sentence embeddings beat every lexical method on cross-script pairs. Refuted if a lexical method matches them.
