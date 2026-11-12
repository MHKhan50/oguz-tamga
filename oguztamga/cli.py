import argparse

from .data import download_flores200, download_flores_plus, load_split, read_source
from .experiment import run
from .retrievers import LEXICAL, METHODS


def main(argv=None):
    parser = argparse.ArgumentParser(prog="oguztamga", description="OğuzTamga experiments")
    sub = parser.add_subparsers(dest="command", required=True)
    d = sub.add_parser("download", help="fetch FLORES sentences for the five languages")
    d.add_argument("--data-dir", default="data")
    d.add_argument("--source", choices=("flores_plus", "flores200"), default="flores_plus")
    d.add_argument("--revision", default=None, help="FLORES+ git revision (default: latest)")
    r = sub.add_parser("run", help="run the retrieval and abstention experiment")
    r.add_argument("--data-dir", default="data")
    r.add_argument("--out", default="results")
    r.add_argument("--methods", nargs="+", default=list(LEXICAL), choices=METHODS)
    r.add_argument("--seeds", nargs="+", type=int, default=[11, 23, 37, 41, 53])
    args = parser.parse_args(argv)

    if args.command == "download":
        if args.source == "flores_plus":
            download_flores_plus(args.data_dir, args.revision)
        else:
            download_flores200(args.data_dir)
        return
    dev = load_split("dev", args.data_dir)
    devtest = load_split("devtest", args.data_dir)
    run(dev, devtest, args.methods, args.seeds, args.out, data_source=read_source(args.data_dir))
    print("Wrote %s/pairs.csv, summary.csv, tables.md, run_metadata.json" % args.out)


if __name__ == "__main__":
    main()
