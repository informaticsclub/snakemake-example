#!/usr/bin/env Rscript

# Draw a simple boxplot for the top DE gene from PyDESeq2.
#
# WHY: This gives a quick visual of how expression differs between
# conditions for the strongest hit, using the same ggpubr style as the
# MA-plot.

suppressPackageStartupMessages({
  library(ggplot2)
  library(ggpubr)
})

args <- commandArgs(trailingOnly = TRUE)

if (length(args) != 2) {
  stop("Usage: plot_top_gene_boxplot.R <top_gene_counts_tsv> <output_png>")
}

counts_path <- args[[1]]
output_path <- args[[2]]

df <- read.delim(
  file = counts_path,
  header = TRUE,
  sep = "\t",
  stringsAsFactors = FALSE
)

required_cols <- c("sample_id", "condition", "gene_id", "normalized_count")
missing_cols <- setdiff(required_cols, names(df))

if (length(missing_cols) > 0) {
  stop(paste("Missing required columns:", paste(missing_cols, collapse = ", ")))
}

gene_label <- unique(df$gene_id)
title_text <- if (length(gene_label) == 1L) {
  paste("Top DE gene:", gene_label)
} else {
  "Top DE gene"
}

p <- ggpubr::ggboxplot(
  df,
  x = "condition",
  y = "normalized_count",
  color = "condition",
  add = "jitter",
  ylab = "Normalized counts (log2 scale)",
  xlab = "Condition",
  title = title_text
) +
  ggplot2::scale_y_continuous(trans = "log2")

ggplot2::ggsave(
  filename = output_path,
  plot = p,
  width = 5,
  height = 4,
  dpi = 300
)

