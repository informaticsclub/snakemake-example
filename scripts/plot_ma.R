#!/usr/bin/env Rscript

# Make an MA-plot from PyDESeq2 results using ggpubr::ggmaplot.
#
# WHY: This matches common RNA-seq practice and shows how R can be
# plugged into a Snakemake pipeline after Python-based processing.

suppressPackageStartupMessages({
  library(ggplot2)
  library(ggpubr)
})

args <- commandArgs(trailingOnly = TRUE)

if (length(args) != 2) {
  stop("Usage: plot_ma.R <deseq_results_tsv> <output_png>")
}

results_path <- args[[1]]
output_path <- args[[2]]

res <- read.delim(
  file = results_path,
  header = TRUE,
  sep = "\t",
  stringsAsFactors = FALSE
)

if (!all(c("baseMean", "log2FoldChange", "padj") %in% names(res))) {
  stop("Results must contain baseMean, log2FoldChange, and padj columns.")
}

res_clean <- res[!is.na(res$padj), ]

p <- ggpubr::ggmaplot(
  data = res_clean,
  fdr = 0.05,
  fc = 1.5,
  main = "MA-plot: residual vs pCR",
  xlab = "Log2 mean expression",
  ylab = "Log2 fold change",
  ggtheme = ggplot2::theme_classic()
)

ggplot2::ggsave(
  filename = output_path,
  plot = p,
  width = 6,
  height = 4,
  dpi = 300
)

