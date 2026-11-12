# Limitations and responsible use

## Threats to validity
- **Translationese.** FLORES sentences share one English source, which helps every method. Results are an upper bound for evidence retrieval across independently written documents.
- **Sentence-level pools.** Each pool has about 1,000 sentences. Real collections are larger and noisier, and Recall@1 falls as pools grow.
- **Simulated missing evidence.** Removing the true sentence makes "no evidence" clean and balanced (50%). In practice the share is unknown and partial evidence is common.
- **Simple transliteration.** The Cyrillic-to-Latin and Uzbek mappings are hand-written and lossy, not an official standard.
- **No generation.** The agent returns a retrieved sentence or abstains. It does not write answers, so fluency and hallucination in generated text are not measured.
- **Two embedding models only,** used off the shelf.

## Responsible use
- The agent returns evidence, not advice. It must not be used for medical, legal or emergency decisions in v0.1.
- A low wrong-evidence rate on FLORES does not carry over to other domains without a new evaluation.
- The work covers five of the larger Turkic languages; results say nothing about lower-resource ones such as Uyghur, Turkmen, Tatar or Bashkir.
