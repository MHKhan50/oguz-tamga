"""Retrievers that score every candidate sentence for every query sentence.

Each retriever returns a dense score matrix S where S[i, j] is how well candidate j
(in the target language) supports query i (in the source language).
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .normalise import prepare

LEXICAL = {
    # name: (analyzer, ngram range, normalisation)
    "word_raw": ("word", (1, 1), "raw"),
    "char_raw": ("char_wb", (2, 4), "raw"),
    "char_latin": ("char_wb", (2, 4), "latin"),
    "char_folded": ("char_wb", (2, 4), "folded"),
}
DENSE = {
    "e5_small": ("intfloat/multilingual-e5-small", "query: ", "query: "),
    "labse": ("sentence-transformers/LaBSE", "", ""),
}
METHODS = tuple(LEXICAL) + tuple(DENSE)


def lexical_scores(queries, q_lang, candidates, c_lang, method):
    analyzer, ngrams, mode = LEXICAL[method]
    q = [prepare(t, q_lang, mode) for t in queries]
    c = [prepare(t, c_lang, mode) for t in candidates]
    # Fit on both sides so shared n-grams get one weight; sublinear tf keeps long sentences in check.
    vec = TfidfVectorizer(analyzer=analyzer, ngram_range=ngrams, sublinear_tf=True, min_df=1)
    vec.fit(q + c)
    return (vec.transform(q) @ vec.transform(c).T).toarray()


class DenseEncoder:
    """Optional sentence encoder. Needs `pip install sentence-transformers`."""

    def __init__(self, method, device=None, batch_size=64):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError("Dense methods need: pip install sentence-transformers") from exc
        name, self.q_prefix, self.c_prefix = DENSE[method]
        self.model = SentenceTransformer(name, device=device)
        self.batch_size = batch_size
        self._cache = {}

    def encode(self, texts, prefix):
        key = (prefix, tuple(texts))
        if key not in self._cache:
            self._cache[key] = self.model.encode([prefix + t for t in texts], batch_size=self.batch_size,
                                                 normalize_embeddings=True, show_progress_bar=False)
        return self._cache[key]

    def scores(self, queries, candidates):
        # float64 keeps the dot products exact and avoids spurious BLAS warnings on some Macs
        q = np.asarray(self.encode(queries, self.q_prefix), dtype=np.float64)
        c = np.asarray(self.encode(candidates, self.c_prefix), dtype=np.float64)
        out = q @ c.T
        if not np.all(np.isfinite(out)):
            raise FloatingPointError("Non-finite similarity scores from the encoder")
        return out


def score_matrix(queries, q_lang, candidates, c_lang, method, encoders=None):
    if method in LEXICAL:
        return lexical_scores(queries, q_lang, candidates, c_lang, method)
    if method in DENSE:
        encoders = encoders if encoders is not None else {}
        if method not in encoders:
            encoders[method] = DenseEncoder(method)
        return np.asarray(encoders[method].scores(queries, candidates))
    raise ValueError("Unknown method %r; choose from %s" % (method, ", ".join(METHODS)))
