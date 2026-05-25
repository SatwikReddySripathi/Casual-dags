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

## Run Adherence Baseline (V1)

```bash
python src/adherence/evaluate.py
```

## Render DAG figures (V1)

```bash
python src/dag/render_dag.py
```

## Run classifier-error sensitivity analysis (V1.5)

```bash
python src/sensitivity/run_analysis.py
```

Produces a curve showing how classifier error rate propagates into causal-estimate bias — directly addresses the reviewer's deeper concern about classifier error propagation.

## Run bandit-inference / winner's-curse demo (V1.6)

```bash
python src/bandit/run_analysis.py
```

Two demos: (1) winner's-curse selection bias for K identical Bernoulli arms (addresses the reviewer's "premature convergence on false best arm" worry) with bootstrap-based debiasing; (2) IPW vs naive arm-mean estimators under increasingly concentrated allocation.

## Compute interrater reliability when a second rater exists (V1.5)

```bash
python src/adherence/interrater.py
```

Will print the second-rater workflow if `data/manual_labels_rater2.csv` is missing; otherwise computes Cohen's κ overall and per-policy.

## Run Tests

```bash
pytest
```

28 tests cover classifier logic, DAG construction, sensitivity simulation, and κ computation.

## Outputs

Generated files appear in `outputs/`:

**Adherence baseline (V1)**
- `adherence_baseline_report.md`
- `adherence_predictions.csv`
- `adherence_confusion_matrix.png`

**DAG figures (V1, with V1.5 SVG additions)**
- `hattie_taxonomy_dag.png` / `.svg` / `.graphml` — broader taxonomy DAG
- `clarity_retention_dag.png` / `.svg` / `.graphml` — paper §2.2 mediation DAG

**Sensitivity analysis (V1.5)**
- `sensitivity_curve.png`
- `sensitivity_predictions.csv`
- `sensitivity_report.md`

**Bandit inference (V1.6)**
- `bandit_winners_curse.png`
- `bandit_ipw_vs_naive.png`
- `bandit_inference_table.csv`
- `bandit_inference_report.md`

**Interrater (V1.5, produced when rater-2 data exists)**
- `interrater_report.md`

## Scope

This project does not claim to fully validate the classifier. It creates the first measurable baseline and a structure for future validation with more examples, multiple raters, and interrater reliability.
