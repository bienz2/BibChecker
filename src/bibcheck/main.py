import argparse
import sys

from .bibliography import Bibliography
from .utils import exclusions, load_source_patterns
from pathlib import Path
import csv


def run(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Parse bibcheck options")
    parser.add_argument("pdf_path", help="Path to the PDF file or folder containing files")
    parser.add_argument("-write_out", action="store_true", help="Save output to a .doc file")
    parser.add_argument("-stats", action="store_true", help="Output csv file listing stats per file")

    style_group = parser.add_mutually_exclusive_group()
    style_group.add_argument("-ieee", action="store_true", help="Parse IEEE style references")
    style_group.add_argument("-acm", action="store_true", help="Parse ACM style references")
    style_group.add_argument("-siam", action="store_true", help="Parse SIAM style references")
    style_group.add_argument("-springer", action="store_true", help="Parse Springer style references")


    parser.add_argument(
        "--exclude-file",
        action="append",
        default=[],
        metavar="PATH",
        help="JSON file with additional exclusions (can be passed multiple times).",
    )

    args = parser.parse_args(argv)

    exclusions = load_source_patterns(extra_files=args.exclude_file)

    pdf_path = Path(args.pdf_path).expanduser().resolve()
    folder = ""
    if pdf_path.is_file():
        pdf_files = [pdf_path]
        folder = pdf_path.parent
    elif pdf_path.is_dir():
        pdf_files = list(pdf_path.glob("*.pdf"))
        folder = pdf_path
        args.write_out = True
    else:
        print("Invalid path: ", path)
        return

    if not pdf_files:
        print("No PDF files in path: ", path)
        return

    if args.write_out:
        bibcheck_dir = folder / "bibcheck"
        bibcheck_dir.mkdir(exist_ok=True)

    stats_file = folder/"bibcheck"/"stats.csv"
    if args.stats:
        write_header = not stats_file.exists()
        with stats_file.open("a", newline="") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(["Paper", "Matches", "Excluded", "Incorrect Format", "Title Error", "Author Error", "DOI Found", "DOI Error"])
        

    for file in pdf_files:
        pdf_stem = file.stem
        doc_path = folder / "bibcheck" / f"{pdf_stem}.docx"
        if doc_path.exists():
            print(f"Skipping {file}, already processed");
            continue



        bib = Bibliography()
        if bib.parse(file, args):
            stats = bib.validate(args)
            if args.stats:
                with stats_file.open("a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([file.name] + stats)

if __name__ == "__main__":
    run()

