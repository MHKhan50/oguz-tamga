import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from fixtures import corpus, fake_archive
from oguztamga.agent import OguzTamgaAgent
from oguztamga.data import download_flores200, find_data_file, load_split, read_records, read_source, records_to_lines
from oguztamga.evaluate import closed_set, missing_mask, open_set_predictions, open_set_report, pick_threshold
from oguztamga.experiment import run, script_pair
from oguztamga.languages import directed_pairs, flores_code
from oguztamga.normalise import prepare
from oguztamga.retrievers import score_matrix


class Normalise(unittest.TestCase):
    def test_turkish_dotted_i(self):
        self.assertEqual(prepare("İSTANBUL IŞIK", "tur", "raw"), "istanbul ışık")

    def test_kazakh_to_latin(self):
        self.assertEqual(prepare("Қазақстан", "kaz", "folded"), "kazakstan")

    def test_uzbek_apostrophe_letters(self):
        self.assertEqual(prepare("O'zbekiston shahri", "uzn", "folded"), "ozbekiston sahri")

    def test_unknown_mode(self):
        with self.assertRaises(ValueError):
            prepare("x", "tur", "nope")


class Languages(unittest.TestCase):
    def test_twenty_directed_pairs(self):
        self.assertEqual(len(directed_pairs()), 20)

    def test_unknown_language(self):
        with self.assertRaises(ValueError):
            flores_code("eng")

    def test_script_pairs(self):
        self.assertEqual(script_pair("tur", "kaz"), "cross_script")
        self.assertEqual(script_pair("kaz", "kir"), "both_cyrillic")
        self.assertEqual(script_pair("tur", "uzn"), "both_latin")


class Metrics(unittest.TestCase):
    def test_closed_set_perfect(self):
        m = closed_set(np.eye(4))
        self.assertEqual(m["recall_at_1"], 1.0)
        self.assertEqual(m["mrr"], 1.0)

    def test_closed_set_rank_two(self):
        s = np.array([[0.5, 0.9], [0.1, 0.8]])
        self.assertAlmostEqual(closed_set(s)["mrr"], 0.75)

    def test_mask_share_and_determinism(self):
        a = missing_mask(10, 1)
        self.assertEqual(a.sum(), 5)
        self.assertTrue((a == missing_mask(10, 1)).all())

    def test_hidden_gold_is_never_predicted(self):
        s = np.eye(6) + 0.01
        mask = missing_mask(6, 3)
        pred, _ = open_set_predictions(s, mask)
        self.assertFalse(np.any(pred[mask] == np.arange(6)[mask]))

    def test_threshold_separates_clean_case(self):
        s = np.eye(8) * 0.9 + 0.05
        mask = missing_mask(8, 0)
        pred, conf = open_set_predictions(s, mask)
        t = pick_threshold(pred, conf["margin"], mask)
        report = open_set_report(pred, conf["margin"], mask, t)
        self.assertEqual(report["right_move_rate"], 1.0)
        self.assertEqual(report["answered_when_no_evidence"], 0.0)


class Retrieval(unittest.TestCase):
    def test_transliteration_is_needed_across_scripts(self):
        c = corpus()
        raw = closed_set(score_matrix(c["tur"], "tur", c["kaz"], "kaz", "char_raw"))["recall_at_1"]
        folded = closed_set(score_matrix(c["tur"], "tur", c["kaz"], "kaz", "char_folded"))["recall_at_1"]
        self.assertGreater(folded, raw)
        self.assertEqual(folded, 1.0)

    def test_dense_needs_optional_package(self):
        try:
            import sentence_transformers  # noqa: F401
            self.skipTest("sentence-transformers is installed")
        except ImportError:
            pass
        with self.assertRaises(ImportError):
            score_matrix(["a"], "tur", ["b", "c"], "azj", "e5_small")

    def test_unknown_method(self):
        with self.assertRaises(ValueError):
            score_matrix(["a"], "tur", ["b"], "azj", "nope")


class Agent(unittest.TestCase):
    def setUp(self):
        c = corpus()
        self.agent = OguzTamgaAgent([(t, "fixture#%d" % i) for i, t in enumerate(c["kaz"])], "kaz",
                                       method="char_folded", confidence="margin", threshold=0.05)

    def test_answers_with_source(self):
        out = self.agent.answer("kitap mektep", "tur")
        self.assertEqual(out["status"], "answered")
        self.assertEqual(out["source"], "fixture#1")

    def test_abstains_without_evidence(self):
        self.assertEqual(self.agent.answer("qqq zzz", "tur")["status"], "abstain")


class Pipeline(unittest.TestCase):
    def test_download_extract_and_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            archive = tmp / "src.tar.gz"
            fake_archive(archive)
            source = download_flores200(tmp / "data", url=archive.resolve().as_uri())
            self.assertEqual(read_source(tmp / "data")["source"], "FLORES-200")
            dev = load_split("dev", tmp / "data")
            test = load_split("devtest", tmp / "data")
            self.assertEqual(len(dev["kaz"]), 12)
            summary = run(dev, test, ["word_raw", "char_folded"], [1, 2], tmp / "out", data_source=source, log=lambda *a: None)
            for name in ("pairs.csv", "summary.csv", "tables.md", "run_metadata.json"):
                self.assertTrue((tmp / "out" / name).exists())
            meta = json.loads((tmp / "out" / "run_metadata.json").read_text())
            self.assertEqual(meta["pairs"], 20)
            best = {r["method"]: r["recall_at_1"] for r in summary if r["pairs"] == "cross_script" and r["confidence"] == "margin"}
            self.assertGreater(best["char_folded"], best["word_raw"])

    def test_flores_plus_rows_are_aligned_by_id(self):
        ids, lines = records_to_lines([{"id": "10", "text": "b  x"}, {"id": 2, "text": "a"}])
        self.assertEqual(ids, [2, 10])
        self.assertEqual(lines, ["a", "b x"])

    def test_find_data_file_in_either_format(self):
        jsonl = ["dev/tur_Latn.jsonl", "devtest/tur_Latn.jsonl", "README.md"]
        nested = ["dev/parquet/tur_Latn.parquet", "dev/parquet/azj_Latn.parquet"]
        self.assertEqual(find_data_file(jsonl, "devtest", "tur_Latn"), "devtest/tur_Latn.jsonl")
        self.assertEqual(find_data_file(nested, "dev", "tur_Latn"), "dev/parquet/tur_Latn.parquet")
        with self.assertRaises(FileNotFoundError):
            find_data_file(jsonl, "dev", "kaz_Cyrl")

    def test_read_jsonl_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.jsonl"
            path.write_text('{"id": "2", "text": "b", "iso_639_3": "tur"}\n{"id": "1", "text": "a"}\n', encoding="utf-8")
            self.assertEqual(records_to_lines(read_records(path)), ([1, 2], ["a", "b"]))

    def test_flores_plus_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            records_to_lines([{"id": 1, "text": "a"}, {"id": 1, "text": "b"}])

    def test_missing_data_message(self):
        with self.assertRaises(FileNotFoundError):
            load_split("dev", "/nonexistent")


if __name__ == "__main__":
    unittest.main()
