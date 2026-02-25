"""
Generate a mock gene expression count dataset for visualization.

This script creates a small, tidy TSV file suitable for teaching:
- two conditions (control vs treated),
- per-sample counts for a single marker gene,
- simple "biological" variation so the groups look different in a plot.
"""

from __future__ import annotations

import argparse
import csv
import logging
import math
import random
from pathlib import Path
from typing import Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a mock gene expression counts TSV."
    )
    parser.add_argument("output_tsv", type=Path, help="Path to output TSV.")
    parser.add_argument(
        "--n-per-group",
        type=int,
        default=30,
        help="Samples per condition (default: 30).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=123,
        help="Random seed for reproducibility (default: 123).",
    )
    return parser.parse_args()


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def simulate_counts(n: int, mean_log2: float, sd_log2: float) -> List[int]:
    """
    Simulate counts by sampling log2(count + 1) from a normal distribution.

    Using log-space makes it easy to generate right-skewed counts without
    non-stdlib numeric dependencies.
    """
    counts: List[int] = []
    for _ in range(n):
        log2_value = random.gauss(mean_log2, sd_log2)
        count = int(round(max(0.0, math.pow(2.0, log2_value) - 1.0)))
        counts.append(count)
    return counts


def write_tsv(rows: List[Dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    configure_logging()

    random.seed(args.seed)

    n = args.n_per_group
    gene_id = "GENE_X"

    control = simulate_counts(n=n, mean_log2=4.3, sd_log2=0.35)
    treated = simulate_counts(n=n, mean_log2=5.0, sd_log2=0.35)

    rows: List[Dict[str, str]] = []
    sample_index = 1

    for condition, counts in (("control", control), ("treated", treated)):
        for count in counts:
            rows.append(
                {
                    "sample_id": f"S{sample_index:03d}",
                    "condition": condition,
                    "gene_id": gene_id,
                    "count": str(count),
                }
            )
            sample_index += 1

    logging.info("Writing %d rows to %s", len(rows), args.output_tsv)
    write_tsv(rows, args.output_tsv)


if __name__ == "__main__":
    main()

