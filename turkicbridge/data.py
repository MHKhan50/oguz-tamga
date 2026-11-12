"""Download and load the FLORES sentences for the five languages.

Default source: FLORES+, the maintained continuation of FLORES-200 by the Open
Language Data Initiative, on Hugging Face (CC BY-SA 4.0). The dataset is gated:
accept its conditions on the dataset page and log in with a Hugging Face token
before downloading. Its conditions ask that the text is not re-hosted where web
crawlers can reach it, so `data/` is git-ignored and results never contain text.

The original FLORES-200 archive from Meta is kept as a second source.
Both are written to the same local layout: data/<split>/<code>.<split>, one
sentence per line, line i aligned across languages.
"""
import hashlib
import json
import tarfile
import urllib.request
from pathlib import Path

from .languages import LANGUAGES, flores_code

FLORES_PLUS_REPO = "openlanguagedata/flores_plus"
FLORES_URL = "https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz"
SPLITS = ("dev", "devtest")


def records_to_lines(records):
    """Turn FLORES+ rows ({'id', 'text'}) into a list ordered by id.

    Rows with the same id in the same split are translations of each other, so
    ordering by id is what aligns the languages.
    """
    ids = [int(r["id"]) for r in records]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate ids in FLORES+ split; more than one variant in the file?")
    ordered = sorted(zip(ids, (r["text"] for r in records)))
    return [i for i, _ in ordered], [" ".join(str(t).split()) for _, t in ordered]


DATA_EXTENSIONS = (".jsonl", ".parquet")


def find_data_file(files, split, code):
    """Locate the data file (JSON Lines or parquet) for one language and split."""
    hits = [f for f in files if f.endswith(DATA_EXTENSIONS) and f.split("/")[0] == split
            and f.rsplit("/", 1)[-1].startswith(code)]
    if len(hits) != 1:
        near = [f for f in files if code.split("_")[0] in f]
        raise FileNotFoundError("Expected one %s file for %s, found %s. Files mentioning %s: %s"
                                % (split, code, hits or "none", code.split("_")[0], near[:10]))
    return hits[0]


def read_records(path):
    """Rows with 'id' and 'text' from a .jsonl or .parquet file."""
    path = str(path)
    if path.endswith(".jsonl"):
        with open(path, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
        return [{"id": r["id"], "text": r["text"]} for r in rows]
    import pandas as pd
    return pd.read_parquet(path, columns=["id", "text"]).to_dict("records")


def download_flores_plus(data_dir="data", revision=None):
    """Fetch the ten data files for the five languages and write aligned text files."""
    try:
        from huggingface_hub import HfApi, hf_hub_download
    except ImportError as exc:
        raise ImportError("FLORES+ download needs: pip install -r requirements.txt") from exc
    data_dir = Path(data_dir)
    api = HfApi()
    sha = api.dataset_info(FLORES_PLUS_REPO, revision=revision).sha
    files = api.list_repo_files(FLORES_PLUS_REPO, repo_type="dataset", revision=sha)
    for split in SPLITS:
        reference = None
        for lang in LANGUAGES:
            code = flores_code(lang)
            remote = find_data_file(files, split, code)
            path = hf_hub_download(FLORES_PLUS_REPO, remote, repo_type="dataset", revision=sha)
            ids, lines = records_to_lines(read_records(path))
            if reference is None:
                reference = ids
            elif ids != reference:
                raise ValueError("%s %s ids do not match the other languages" % (split, code))
            target = data_dir / split / ("%s.%s" % (code, split))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    source = {"source": "FLORES+", "repo": FLORES_PLUS_REPO, "revision": sha}
    (data_dir / "SOURCE.json").write_text(json.dumps(source, indent=2) + "\n", encoding="utf-8")
    print("FLORES+ revision %s: wrote %d files" % (sha, len(SPLITS) * len(LANGUAGES)))
    return source


def download_flores200(data_dir="data", url=FLORES_URL):
    """Fetch the original FLORES-200 archive once and extract dev/devtest for the five languages.

    If the download fails (for example on a TLS error), place the archive at
    data/flores200_dataset.tar.gz by other means and run this again.
    """
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    archive = data_dir / "flores200_dataset.tar.gz"
    if not archive.exists():
        print("Downloading", url)
        tmp = archive.with_suffix(".part")
        urllib.request.urlretrieve(url, str(tmp))
        tmp.rename(archive)
    wanted = {"flores200_dataset/%s/%s.%s" % (split, flores_code(lang), split)
              for lang in LANGUAGES for split in SPLITS}
    with tarfile.open(str(archive), "r:gz") as tar:
        members = [m for m in tar.getmembers() if m.name in wanted and m.isfile()]
        missing = wanted - {m.name for m in members}
        if missing:
            raise RuntimeError("Archive is missing: " + ", ".join(sorted(missing)))
        for member in members:
            target = data_dir / Path(member.name).relative_to("flores200_dataset")
            target.parent.mkdir(parents=True, exist_ok=True)
            with tar.extractfile(member) as src:
                target.write_bytes(src.read())
    sha = hashlib.sha256(archive.read_bytes()).hexdigest()
    source = {"source": "FLORES-200", "url": url, "archive_sha256": sha}
    (data_dir / "SOURCE.json").write_text(json.dumps(source, indent=2) + "\n", encoding="utf-8")
    print("Extracted %d files. Archive sha256: %s" % (len(wanted), sha))
    return source


def read_source(data_dir="data"):
    path = Path(data_dir) / "SOURCE.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def load_split(split, data_dir="data", langs=None):
    """Return {lang: [sentence, ...]} with line i aligned across languages."""
    if split not in SPLITS:
        raise ValueError("split must be one of %s" % (SPLITS,))
    langs = list(langs or LANGUAGES)
    out = {}
    for lang in langs:
        path = Path(data_dir) / split / ("%s.%s" % (flores_code(lang), split))
        if not path.exists():
            raise FileNotFoundError("%s not found; run `python -m turkicbridge.cli download` first" % path)
        out[lang] = path.read_text(encoding="utf-8").rstrip("\n").split("\n")
    sizes = {len(v) for v in out.values()}
    if len(sizes) != 1:
        raise ValueError("Languages are not aligned: %s" % {k: len(v) for k, v in out.items()})
    return out
