#! /usr/bin/env snakemake

# Minimal Snakemake workflow for GEO series GSE240671.
# WHY: Tie together one Python DE step (PyDESeq2) and two R plots
# (ggpubr) in a small, readable pipeline for teaching.

# Keep data paths in a tiny config so they are easy to change.
configfile: "config.yml"

rule all:
    """
    Final targets for this example workflow.
    """
    input:
        "results/deseq2_results.tsv",
        "results/ma_plot.png",
        "results/top_gene_boxplot.png"


rule run_deseq2:
    """
    Run PyDESeq2 on the GSE240671 counts + metadata.
    This is the only step that touches the big count matrix.
    """
    # Use a dedicated Conda env so the DE code runs the same for everyone.
    conda:
        "envs/pydeseq2.yml"
    # Give PyDESeq2 a few threads for speed without overloading laptops.
    threads: 4
    message:
        "Running PyDESeq2 (residual vs pCR)."
    log:
        "logs/run_deseq2.log"
    input:
        counts=config["data"]["counts"],
        metadata=config["data"]["metadata"]
    output:
        results="results/deseq2_results.tsv",
        top_gene_counts="results/top_gene_counts.tsv"
    benchmark:
        "logs/run_deseq2.benchmark.tsv"
    shell:
        (
            "python scripts/run_deseq2.py "
            "{input.counts} {input.metadata} "
            "{output.results} {output.top_gene_counts}"
        )


rule plot_ma:
    """
    Make an MA-plot from the PyDESeq2 results using ggpubr::ggmaplot.
    """
    # Share the same R env between the two visualization rules.
    conda:
        "envs/r-ggpubr-viz.yml"
    threads: 2
    message:
        "Drawing MA-plot with ggpubr."
    log:
        "logs/plot_ma.log"
    input:
        "results/deseq2_results.tsv"
    output:
        "results/ma_plot.png"
    benchmark:
        "logs/plot_ma.benchmark.tsv"
    shell:
        "Rscript scripts/plot_ma.R {input} {output}"


rule plot_top_gene_boxplot:
    """
    Boxplot of the top DE gene's normalized counts across conditions.
    """
    conda:
        "envs/r-ggpubr-viz.yml"
    threads: 2
    message:
        "Drawing top-gene boxplot with ggpubr."
    log:
        "logs/plot_top_gene_boxplot.log"
    input:
        "results/top_gene_counts.tsv"
    output:
        "results/top_gene_boxplot.png"
    benchmark:
        "logs/plot_top_gene_boxplot.benchmark.tsv"
    shell:
        "Rscript scripts/plot_top_gene_boxplot.R {input} {output}"
