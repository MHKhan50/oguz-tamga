"""A small evidence-grounded agent on top of one retriever and one threshold."""
import numpy as np

from .languages import LANGUAGES
from .retrievers import score_matrix


class TurkicBridgeAgent:
    """Answers a question in one language with a sentence found in another, or abstains.

    The corpus is a list of (sentence, source_id) in the target language. The agent
    never generates text: every answer is a sentence from the corpus with its source.
    """

    def __init__(self, corpus, corpus_lang, method="char_folded", confidence="margin", threshold=0.0):
        if corpus_lang not in LANGUAGES:
            raise ValueError("Unsupported language: %r" % corpus_lang)
        if confidence not in ("top1", "margin"):
            raise ValueError("confidence must be 'top1' or 'margin'")
        if len(corpus) < 2:
            raise ValueError("The corpus needs at least two sentences")
        self.texts = [t for t, _ in corpus]
        self.sources = [s for _, s in corpus]
        self.lang = corpus_lang
        self.method = method
        self.confidence = confidence
        self.threshold = threshold

    def answer(self, query, query_lang):
        row = score_matrix([query], query_lang, self.texts, self.lang, self.method)[0]
        order = np.argsort(-row)
        top1, top2 = float(row[order[0]]), float(row[order[1]])
        conf = top1 if self.confidence == "top1" else top1 - top2
        if conf < self.threshold:
            return {"status": "abstain", "confidence": conf,
                    "reason": "no candidate passed the evidence threshold"}
        best = int(order[0])
        return {"status": "answered", "evidence": self.texts[best], "source": self.sources[best],
                "language": self.lang, "confidence": conf}
