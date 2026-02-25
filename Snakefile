rule all:
    """
    Final targets for this example workflow.
    """
    input:
        "results/mock_counts.tsv",
        "results/mock_counts_boxplot.png"


rule generate_mock_counts:
    """
    Use Python to generate mock count data.
    """
    output:
        "results/mock_counts.tsv"
    shell:
        "python scripts/generate_mock_counts.py {output}"


rule visualize_counts:
    """
    Use R and ggpubr to visualize mock count data from a TSV.
    """
    input:
        "results/mock_counts.tsv"
    output:
        "results/mock_counts_boxplot.png"
    shell:
        "Rscript scripts/visualize_counts.R {input} {output}"

