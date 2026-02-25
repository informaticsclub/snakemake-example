#!/usr/bin/env Rscript

# Visualize a mock count dataset with ggpubr.
#
# This script reads a tidy TSV file of counts, computes log2(count + 1),
# and generates a publication-style boxplot with overlaid points and a
# p-value annotation.

suppressPackageStartupMessages({
  library(ggplot2)
  library(ggpubr)
})

args <- commandArgs(trailingOnly = TRUE)

if (length(args) != 2) {
  stop("Usage: visualize_counts.R <input_counts_tsv> <output_plot_png>")
}

input_path <- args[[1]]
output_path <- args[[2]]

mock_counts <- read.delim(
  file = input_path,
  header = TRUE,
  sep = "\t",
  stringsAsFactors = FALSE
)

required_cols <- c("sample_id", "condition", "gene_id", "count")
missing_cols <- setdiff(required_cols, names(mock_counts))

if (length(missing_cols) > 0) {
  stop(paste("Missing required columns:", paste(missing_cols, collapse = ", ")))
}

mock_counts$count <- as.numeric(mock_counts$count)

if (any(is.na(mock_counts$count))) {
  stop("Counts contain NA after numeric conversion.")
}

mock_counts$log2_count <- log2(mock_counts$count + 1)

p <- ggpubr::ggboxplot(
  mock_counts,
  x = "condition",
  y = "log2_count",
  color = "condition",
  add = "jitter",
  ylab = "log2(count + 1)",
  xlab = "Condition"
) +
  ggpubr::stat_compare_means(
    method = "wilcox.test",
    label = "p.format"
  )

ggplot2::ggsave(
  filename = output_path,
  plot = p,
  width = 5,
  height = 4,
  dpi = 300
)

