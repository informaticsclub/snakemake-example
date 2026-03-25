# Snakemake Local Example

Minimal Snakemake workflow that:

- runs **PyDESeq2** on real RNA-seq counts from GSE240671
- uses **R + ggpubr** to make an MA-plot and a top-gene boxplot

## Setup

Create an environment with Snakemake and Conda (needed for `--use-conda`):

```sh
mamba env create -f environment.yml
mamba activate snakemake-example
```

This gives you a shell where you can run `snakemake`. When the workflow
runs, Snakemake will create the Python and R environments it needs from
the small files in `envs/`.

## Run the workflow

From the repo root:

```sh
snakemake --use-conda -j 1
```

To have Snakemake use mamba (faster) when creating rule envs, add
`--conda-frontend mamba`.

This will write:

- a DE results table for GSE240671
- an MA-plot PNG and a top-gene boxplot PNG

## Files in this example

- `Snakefile` – defines the rules.
- `config.yml` – small config with data paths.
- `envs/` – tiny Conda env files used by each rule.
- `scripts/` – Python and R scripts called by the rules.
- `results/` – output folder created by Snakemake.
- `logs/` – text logs and simple timing info for each rule.
