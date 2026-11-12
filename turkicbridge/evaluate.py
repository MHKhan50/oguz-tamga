"""Closed-set retrieval metrics and the open-set test with abstention.

Open-set test: for a seeded half of the queries the true parallel sentence is
removed from the candidates, so the only right move is to abstain. The agent
answers when its confidence is at least a threshold chosen on the dev split and
abstains otherwise.
"""
import numpy as np

CONFIDENCE = ("top1", "margin")


def closed_set(scores):
    """Recall@1 and mean reciprocal rank when every true answer is in the pool."""
    n = scores.shape[0]
    gold = scores[np.arange(n), np.arange(n)]
    # ties count against the true sentence: a retriever that scores everything 0 gets rank n, not 1
    rank = (scores >= gold[:, None]).sum(axis=1)
    return {"recall_at_1": float(np.mean(rank == 1)), "mrr": float(np.mean(1.0 / rank))}


def missing_mask(n, seed, share=0.5):
    """Boolean mask, True where the true parallel is removed for that query."""
    rng = np.random.default_rng(seed)
    mask = np.zeros(n, dtype=bool)
    mask[rng.choice(n, size=int(round(n * share)), replace=False)] = True
    return mask


def open_set_predictions(scores, mask):
    """Top candidate and two confidence signals per query, with gold hidden where mask is True."""
    s = scores.astype(float).copy()
    idx = np.arange(s.shape[0])
    s[idx[mask], idx[mask]] = -np.inf
    order = np.argsort(-s, axis=1)[:, :2]
    top1 = s[idx, order[:, 0]]
    top2 = s[idx, order[:, 1]]
    # a tie at the top means no single piece of evidence was found
    pred = np.where(top1 > top2, order[:, 0], -1)
    return pred, {"top1": top1, "margin": top1 - top2}


def outcome(pred, conf, mask, threshold):
    """Per-query outcome under one threshold."""
    answered = conf >= threshold
    hit = pred == np.arange(len(pred))
    right = np.where(mask, ~answered, answered & hit)
    return answered, hit, right


def pick_threshold(pred, conf, mask):
    """Threshold that maximises the share of right moves (answer with the true sentence, or abstain)."""
    candidates = np.unique(np.quantile(conf, np.linspace(0, 1, 201)))
    best_t, best = candidates[0], -1.0
    for t in candidates:
        score = outcome(pred, conf, mask, t)[2].mean()
        if score > best:
            best_t, best = t, score
    return float(best_t)


def open_set_report(pred, conf, mask, threshold):
    answered, hit, right = outcome(pred, conf, mask, threshold)
    has_gold = ~mask
    return {
        "right_move_rate": float(right.mean()),
        "answered_with_true_evidence": float((answered & hit)[has_gold].mean()),
        "answered_with_wrong_evidence": float((answered & ~hit)[has_gold].mean()),
        "abstained_when_evidence_existed": float((~answered)[has_gold].mean()),
        "answered_when_no_evidence": float(answered[mask].mean()),
        "threshold": threshold,
    }
