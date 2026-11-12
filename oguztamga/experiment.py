"""Run every method on all 20 directed language pairs and write the results."""
import csv
import json
import platform
import statistics
import sys
from pathlib import Path

from . import __version__
from .evaluate import CONFIDENCE, closed_set, missing_mask, open_set_predictions, open_set_report, pick_threshold
from .languages import CYRILLIC, directed_pairs
from .retrievers import score_matrix

OPEN_METRICS = ("right_move_rate", "answered_with_true_evidence", "answered_with_wrong_evidence",
                "abstained_when_evidence_existed", "answered_when_no_evidence")


def script_pair(src, tgt):
    a, b = src in CYRILLIC, tgt in CYRILLIC
    if a == b:
        return "both_cyrillic" if a else "both_latin"
    return "cross_script"


def run(dev, devtest, methods, seeds, out_dir="results", data_source=None, log=print):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows, encoders = [], {}
    for method in methods:
        for src, tgt in directed_pairs():
            s_dev = score_matrix(dev[src], src, dev[tgt], tgt, method, encoders)
            s_test = score_matrix(devtest[src], src, devtest[tgt], tgt, method, encoders)
            closed = closed_set(s_test)
            for seed in seeds:
                dev_mask = missing_mask(len(s_dev), seed)
                test_mask = missing_mask(len(s_test), seed + 1000)
                dev_pred, dev_conf = open_set_predictions(s_dev, dev_mask)
                test_pred, test_conf = open_set_predictions(s_test, test_mask)
                for signal in CONFIDENCE:
                    t = pick_threshold(dev_pred, dev_conf[signal], dev_mask)
                    report = open_set_report(test_pred, test_conf[signal], test_mask, t)
                    rows.append(dict(method=method, source=src, target=tgt, script_pair=script_pair(src, tgt),
                                     seed=seed, confidence=signal, **closed, **report))
            log("%-12s %s->%s  R@1 %.3f" % (method, src, tgt, closed["recall_at_1"]))

    with (out / "pairs.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    summary = summarise(rows)
    with (out / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary)
    (out / "tables.md").write_text(tables(summary), encoding="utf-8")
    meta = {"project": "OğuzTamga", "version": __version__, "methods": list(methods), "seeds": list(seeds),
            "pairs": len(directed_pairs()), "dev_sentences": len(next(iter(dev.values()))),
            "devtest_sentences": len(next(iter(devtest.values()))), "data_source": data_source,
            "python": sys.version.split()[0], "platform": platform.platform()}
    (out / "run_metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return summary


def _mean_sd(values):
    return statistics.mean(values), (statistics.stdev(values) if len(values) > 1 else 0.0)


def summarise(rows):
    """Average over language pairs within each seed, then report mean and sd across seeds."""
    groups = {}
    for r in rows:
        for scope in ("all", r["script_pair"]):
            groups.setdefault((r["method"], r["confidence"], scope), {}).setdefault(r["seed"], []).append(r)
    out = []
    for (method, signal, scope), by_seed in sorted(groups.items()):
        item = {"method": method, "confidence": signal, "pairs": scope,
                "n_pairs": len(next(iter(by_seed.values()))), "n_seeds": len(by_seed)}
        for metric in ("recall_at_1", "mrr") + OPEN_METRICS:
            per_seed = [statistics.mean(r[metric] for r in rs) for rs in by_seed.values()]
            m, sd = _mean_sd(per_seed)
            item[metric] = round(m, 4)
            if metric in OPEN_METRICS:
                item[metric + "_sd"] = round(sd, 4)
        out.append(item)
    return out


def tables(summary):
    lines = ["# OğuzTamga results (FLORES devtest)", "",
             "## Closed set: true sentence always in the pool", "",
             "| Method | Pairs | Recall@1 | MRR |", "|---|---|---|---|"]
    for r in summary:
        if r["confidence"] == "margin":
            lines.append("| %s | %s | %.3f | %.3f |" % (r["method"], r["pairs"], r["recall_at_1"], r["mrr"]))
    lines += ["", "## Open set: true sentence removed for half the queries (all 20 pairs)", "",
              "| Method | Confidence | Right move | True evidence | Wrong evidence | Answered with no evidence |",
              "|---|---|---|---|---|---|"]
    for r in summary:
        if r["pairs"] == "all":
            lines.append("| %s | %s | %.3f ± %.3f | %.3f | %.3f | %.3f |" % (
                r["method"], r["confidence"], r["right_move_rate"], r["right_move_rate_sd"],
                r["answered_with_true_evidence"], r["answered_with_wrong_evidence"],
                r["answered_when_no_evidence"]))
    lines += ["", "True and wrong evidence are shares of queries whose true sentence was in the pool; "
              "the last column is the share of no-evidence queries that still got an answer. "
              "± is the sd across seeds of the pair-averaged value.", ""]
    return "\n".join(lines)
