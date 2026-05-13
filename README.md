# Medhavi Reviewer-Response V1

This project is a lightweight engineering and data-science prototype responding to two concrete reviewer concerns in the Medhavi framework paper:

1. The post-generation adherence classifier was load-bearing but lacked validation.
2. DAG visualizations needed to be converted from weak/ASCII-style representations into publication-ready figures.

## What This Is

This is a V1 validation scaffold, not the full Medhavi tutoring platform.

It includes:
- A policy-adherence rubric.
- A small manually labeled dataset.
- A transparent rule-based baseline classifier.
- Baseline metrics and error analysis.
- A clean DAG visualization of a small Hattie-style variable subset.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# On Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
```

## Run Adherence Baseline

```bash
python src/adherence/evaluate.py
```

## Render DAG

```bash
python src/dag/render_dag.py
```

## Run Tests

```bash
pytest
```

## Outputs

Generated files appear in `outputs/`:

- `adherence_baseline_report.md`
- `adherence_predictions.csv`
- `adherence_confusion_matrix.png`
- `hattie_taxonomy_dag.png` — broader Hattie variable taxonomy DAG
- `hattie_taxonomy_dag.graphml`
- `clarity_retention_dag.png` — paper §2.2 mediation DAG (replaces ASCII)
- `clarity_retention_dag.graphml`

## Scope

This project does not claim to fully validate the classifier. It creates the first measurable baseline and a structure for future validation with more examples, multiple raters, and interrater reliability.
