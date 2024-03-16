import sys
import argparse
import base64
import pathlib
import os
import logging
from multiprocessing import Pool

import pandas as pd

from .utils import get_summary_table, extract_line

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def get_parser():
    parser = argparse.ArgumentParser(
        prog="analyzetkn",
        description="Analyze cl100k tokenizer's text rank and convert base64 encoded binary into text for further analysis",
    )

    default_txtrank_fn = (
        pathlib.Path(__file__).parents[2]
        / "notebooks"
        / "data"
        / "cl100k_base.tiktoken"
    )

    parser.add_argument(
        "-t",
        "--textrank-file",
        type=str,
        help="The filename of the tokenizer's text rank. Default to notebooks/data/cl100k_base.tiktoken",
        default=default_txtrank_fn,
        required=False,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output directory to save the summary table and converted text table. Default to current directory.",
        default=".",
        required=False,
    )
    parser.add_argument(
        "-v", "--verbose", help="Print log for debugging", action="store_true"
    )

    return parser


def main() -> None:
    args = get_parser().parse_args(sys.argv[1:])

    if args.verbose:
        logger.addHandler(logging.StreamHandler(sys.stderr))
        logger.setLevel(logging.DEBUG)

    # Analyze token binary data
    bpes = pathlib.Path(args.textrank_file).read_text().splitlines()
    bpes_mapping = {
        rank: base64.b64decode(token).decode("utf-8", "replace")
        for token, rank in (line.split() for line in bpes if line)
    }

    with Pool(os.cpu_count()) as pool:
        char_ranks = list(pool.map(extract_line, list(bpes_mapping.items())))

    summary_df = get_summary_table(char_ranks)
    token_df = pd.DataFrame(char_ranks, columns=["token", "language", "rank"])
    logger.info("Num token by language summary\n%s\n\n", summary_df.head(20))
    logger.info(
        "Converted binary data to text table\n%s\n\n",
        token_df.sample(20, random_state=987),
    )

    # Save analyzed data
    output_dir = pathlib.Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(output_dir / "summary.csv", index=False)
    token_df.to_csv(output_dir / "token_text.csv", index=False)
    logger.info("save summary table to %s", output_dir / "summary.csv")
    logger.info("save token table to %s", output_dir / "token_text.csv")
