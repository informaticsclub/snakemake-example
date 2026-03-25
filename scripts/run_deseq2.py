"""
Run a minimal PyDESeq2 workflow on the GEO breast cancer dataset.

WHY: This script shows how to go from raw counts + sample metadata to a
simple differential expression table that we can reuse for plots in R.
We keep the logic small on purpose so club members can read it in one
pass.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Tuple

import pandas as pd
from pydeseq2.dds import DeseqDataSet
from pydeseq2.default_inference import DefaultInference
from pydeseq2.ds import DeseqStats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run PyDESeq2 on GSE240671 counts and metadata, write a "
            "results table and a small top-gene counts file."
        )
    )
    parser.add_argument(
        "counts_tsv",
        type=Path,
        help="Raw counts matrix (genes x samples, tab-separated).",
    )
    parser.add_argument(
        "metadata_csv",
        type=Path,
        help="Sample metadata CSV from GEO.",
    )
    parser.add_argument(
        "results_tsv",
        type=Path,
        help="Output path for the DE results table.",
    )
    parser.add_argument(
        "top_gene_tsv",
        type=Path,
        help=(
            "Output path for normalized counts of the top gene, used "
            "for a simple boxplot."
        ),
    )
    return parser.parse_args()


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def load_counts(counts_path: Path) -> pd.DataFrame:
    """
    Load counts with genes in rows and samples in columns.

    WHY: We keep the original matrix shape from GEO and transpose later
    so that it matches what PyDESeq2 expects (samples x genes).
    """
    logging.info("Reading counts from %s", counts_path)
    counts = pd.read_csv(counts_path, sep="\t")
    if "GeneID" not in counts.columns:
        raise ValueError("Counts file must have a 'GeneID' column.")
    counts = counts.set_index("GeneID")
    return counts


def load_and_prepare_metadata(
    metadata_path: Path, counts: pd.DataFrame
) -> pd.DataFrame:
    """
    Load metadata and build a simple two-group condition for DE.

    WHY: PyDESeq2 works best with a clear factor. Here we collapse the
    residual cancer burden category into:
      - pCR    (no residual disease)
      - residual (all other categories with residual disease)
    """
    logging.info("Reading metadata from %s", metadata_path)
    meta = pd.read_csv(metadata_path)

    if "Sample Name" not in meta.columns:
        raise ValueError("Metadata must have a 'Sample Name' column.")
    if "rcb_category" not in meta.columns:
        raise ValueError("Metadata must have an 'rcb_category' column.")
    if "timing_biopsies" not in meta.columns:
        raise ValueError("Metadata must have a 'timing_biopsies' column.")

    # Keep only pre-treatment biopsies so groups are easier to interpret.
    meta = meta.loc[meta["timing_biopsies"] == "pre-surgery"].copy()

    # Map residual cancer burden to a simple binary label.
    def map_rcb(value: str) -> str | None:
        if not isinstance(value, str):
            return None
        if value.strip() == "no residual disease":
            return "pCR"
        # Any residual disease is treated as one group for this demo.
        if "residual disease" in value:
            return "residual"
        return None

    meta["condition"] = meta["rcb_category"].map(map_rcb)
    meta = meta.loc[meta["condition"].notna()].copy()

    # Keep only samples that we actually have counts for.
    sample_names = meta["Sample Name"]
    common = [s for s in sample_names if s in counts.columns]
    if not common:
        raise ValueError("No overlap between metadata and count samples.")

    meta = meta.set_index("Sample Name").loc[common]

    # Sanity check: we want both groups present.
    groups = meta["condition"].unique().tolist()
    if len(groups) != 2:
        raise ValueError(
            f"Expected two conditions, found {len(groups)}: {groups}"
        )

    return meta[["condition"]]


def run_deseq2(
    counts: pd.DataFrame, meta: pd.DataFrame
) -> Tuple[DeseqDataSet, pd.DataFrame]:
    """
    Fit a DESeq2-style model using PyDESeq2 and return results.

    WHY: We keep the design to a single factor (~ condition) so people
    can focus on the structure of the workflow, not the statistics.
    """
    # Reorder counts to match metadata and switch to samples x genes.
    counts_for_dds = counts.loc[:, meta.index].T

    inference = DefaultInference()
    dds = DeseqDataSet(
        counts=counts_for_dds,
        metadata=meta,
        design="~condition",
        inference=inference,
    )

    logging.info("Running DESeq2-like model (PyDESeq2).")
    dds.deseq2()

    # Compare residual vs pCR.
    ds = DeseqStats(
        dds,
        contrast=["condition", "residual", "pCR"],
        inference=inference,
    )
    ds.summary()
    results = ds.results_df.copy()
    return dds, results


def write_results(results: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(path, sep="\t", index=True)
    logging.info("Wrote DE results to %s", path)


def write_top_gene_counts(
    dds: DeseqDataSet,
    results: pd.DataFrame,
    meta: pd.DataFrame,
    path: Path,
) -> None:
    """
    Extract normalized counts for the top gene by adjusted p-value.

    WHY: This gives us a small, tidy table that R can use to draw a
    simple boxplot of expression vs condition.
    """
    clean = results.dropna(subset=["padj"])
    if clean.empty:
        raise ValueError("No genes with non-NA adjusted p-values.")

    top_gene_id = clean.sort_values("padj").index[0]
    logging.info("Top gene by padj: %s", top_gene_id)

    norm_counts = dds.layers["normed_counts"]
    norm_df = pd.DataFrame(
        norm_counts,
        index=dds.obs_names,
        columns=dds.var_names,
    )

    top_series = norm_df[top_gene_id]
    out = pd.DataFrame(
        {
            "sample_id": top_series.index,
            "condition": meta.loc[top_series.index, "condition"],
            "gene_id": top_gene_id,
            "normalized_count": top_series.values,
        }
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, sep="\t", index=False)
    logging.info("Wrote top-gene counts to %s", path)


def main() -> None:
    args = parse_args()
    configure_logging()

    counts = load_counts(args.counts_tsv)
    meta = load_and_prepare_metadata(args.metadata_csv, counts)

    dds, results = run_deseq2(counts, meta)

    write_results(results, args.results_tsv)
    write_top_gene_counts(dds, results, meta, args.top_gene_tsv)


if __name__ == "__main__":
    main()

