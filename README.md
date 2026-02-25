# Snakemake Local Example

This repository provides a very small example of running a Snakemake
workflow **locally** that calls Python and R code to generate a simple
visualization.

The workflow:

- **Python**: generate a mock gene expression count table (TSV).
- **R + ggpubr**: visualize the mock counts as a boxplot with a p-value.

## Table of Contents

- [Project Background](#project-background)
- [Install & Setup](#install--setup)
- [Usage](#usage)
- [Directory Structure](#directory-structure)

## Project Background

This example is intended for teaching and local experimentation. It is kept
intentionally simple so that you can focus on the Snakemake concepts:

- how rules declare input and output files,
- how Snakemake tracks dependencies, and
- how to integrate small Python and R scripts.

## Install & Setup

You need:

- Python (3.9+ recommended),
- R (any modern version),
- Snakemake installed in some environment, and
- the R package `ggpubr` (plus its dependencies such as `ggplot2`) for
  the visualization rule.

### Create the mamba/conda environment

This repo includes an `environment.yml` that installs Snakemake, base R,
and `r-ggpubr` for visualization:

```sh
mamba env create -f environment.yml
mamba activate snakemake-example
```

If you use `conda` instead of `mamba`, replace `mamba` with `conda`.

If you do not already have `mamba` installed, see the
[Mamba installation guide](https://mamba.readthedocs.io/en/latest/installation.html),
then return to the [Install & Setup](#install--setup) section here.


## Usage

From the top level of this repository:

```sh
snakemake -j 1
```

Snakemake will:

1. Use Python to generate a mock counts table in `results/mock_counts.tsv`.
2. Use R and `ggpubr` to generate a mock counts boxplot in
   `results/mock_counts_boxplot.png`.

You can re-run the command and Snakemake will only recompute steps whose
inputs have changed.

## Directory Structure

```sh
$ tree -a snakemake-example/
snakemake-example/
├── README.md
├── Snakefile
├── environment.yml
├── requirements.txt
├── results
│   ├── mock_counts.tsv            # created by Snakemake (Python step)
│   └── mock_counts_boxplot.png    # created by Snakemake (R + ggpubr step)
└── scripts
    ├── generate_mock_counts.py
    └── visualize_counts.R
```

The files under `results/` are created by Snakemake and can be deleted
and regenerated at any time.
