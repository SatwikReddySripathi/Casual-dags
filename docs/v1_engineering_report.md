# Medhavi Reviewer-Response V1 — Engineering Report

**Author:** Sripathi (sripathi.sa@northeastern.edu)
**Date:** 2026-05-10
**Project:** Medhavi Reviewer-Response V1
**Repository:** `Casual dags/` (local working tree)

---

## TL;DR

The Medhavi framework paper received reviewer feedback raising ten concerns. Two were directly actionable as engineering work: the post-generation adherence classifier was "load-bearing but lacked validation," and the DAGs in the paper were "ASCII art rather than proper figures."

I built a V1 engineering artifact that addresses both. The repository runs end-to-end with two commands, has 13 passing tests, and produces five output artifacts ready to show in a meeting: a baseline classifier report with metrics and error analysis, a confusion matrix figure, and two publication-style DAG figures (one of which is a direct, like-for-like replacement of the ASCII DAG the reviewer specifically named).

This V1 is deliberately a scaffold, not a final classifier or a finished figure set. The point is to establish a measurable baseline against which future work — multiple raters, larger samples, model-based classifiers, sensitivity analysis — can be evaluated.

---

## 1. Context and scoping

### 1.1 The reviewer's two actionable engineering critiques

Of the ten concerns raised in the reviewer's report, two are pure engineering problems that can be addressed without revising the paper itself:

1. **Adherence classifier validation gap.** The paper claims (Section 7) that a post-generation classifier scores every LLM output for policy adherence, and treats this as the operational mechanism that makes the claim *"the LLM executed this policy"* true rather than aspirational. The reviewer's objection: validating that classifier is itself an unsolved problem, and the paper does not acknowledge that the validator needs validating.

2. **DAG visualization gap.** The paper formalizes its causal apparatus using Directed Acyclic Graphs, yet the only worked-example DAG in the paper (the clarity / grade-retention mediation in Section 2.2) is presented as ASCII art in running text. The reviewer's objection: for a framework built on DAGs, every DAG should be a proper figure with consistent styling, node labels, and edge annotations.

### 1.2 What I deliberately did not address

The remaining eight reviewer concerns require paper-level revision and are intentionally outside the V1 scope:

- Brown 2026 sourcing problem (CRITICAL — citation credibility for the GLP layer).
- Splitting the paper into 2–3 separate venues (CRITICAL — structural overreach).
- Mode 2 adaptive-allocation ethics treatment.
- Section 6 g-methods / time-varying causal inference implementation detail.
- Citation coverage gaps (Hattie critique literature, bandits in education, adaptive trial ethics, LLM-in-education).
- Writing-craft fixes ("does not replace Hattie" repetition, declarative mood in §3–§4, "Genuine Learning Probability" terminology).

These are documented in `docs/reviewer_response_notes.md` for transparency. None of them are something a V1 engineering sprint can resolve.

---

## 2. Deliverables

The V1 produces five reproducible artifacts in `outputs/`:

| Artifact | Reviewer concern addressed | What it shows |
|---|---|---|
| `adherence_baseline_report.md` | #1 Classifier validation | Dataset summary, metrics table, per-label scores, full error analysis, V1 interpretation, and next steps |
| `adherence_confusion_matrix.png` | #1 Classifier validation | 3×3 confusion matrix across `ADHERENT`, `PARTIAL`, `NON_ADHERENT` |
| `adherence_predictions.csv` | #1 Classifier validation | Per-row predictions with classifier reasons and feature flags — supports drill-down |
| `clarity_retention_dag.png` (+ `.graphml`) | #2 DAG visualization | Direct figure replacement for the paper's §2.2 ASCII DAG (Teacher Clarity → Meeting Grade-Level Standards → Grade Retention → Achievement) |
| `hattie_taxonomy_dag.png` (+ `.graphml`) | #2 DAG visualization | Broader visualization of the framework's intervention/diagnostic/context decomposition — what the reviewer called the paper's "best idea" |

GraphML exports accompany each PNG so the figures can be loaded into yEd, Gephi, or Cytoscape for further refinement before publication.

---

## 3. System architecture

### 3.1 Repository layout

```
Casual dags/
├── CLAUDE.md                          # Build specification
├── README.md                          # How to run
├── requirements.txt
├── .gitignore
├── data/
│   ├── sample_prompts.csv             # 30 hand-labeled tutor responses
│   ├── manual_labels.csv              # human label + reason per id
│   └── hattie_variable_subset.csv     # 10 nodes for the taxonomy DAG
├── src/
│   ├── adherence/
│   │   ├── rubric.py                  # constants only: labels, policies, patterns
│   │   ├── rule_based_classifier.py   # per-policy decision functions + dispatch
│   │   ├── generate_report.py         # markdown report renderer
│   │   └── evaluate.py                # orchestrator (entry point)
│   └── dag/
│       ├── dag_schema.py              # hard-coded edge list
│       ├── build_dag.py               # CSV + schema → validated nx.DiGraph
│       └── render_dag.py              # matplotlib figures + GraphML (entry point)
├── tests/
│   ├── test_classifier.py             # 7 tests on the 5 policy branches
│   ├── test_dag.py                    # 6 tests on the taxonomy DAG
│   └── conftest.py
├── docs/
│   ├── adherence_rubric.md            # policy-by-policy rubric definitions
│   ├── progress_update.md             # meeting-ready short update
│   ├── reviewer_response_notes.md     # reviewer-concern → V1-status mapping
│   └── v1_engineering_report.md       # this document
└── outputs/                           # generated artifacts (committed for visibility)
```

### 3.2 Pipeline A — Adherence classifier

The adherence pipeline turns 30 hand-labeled prompts into a baseline error rate and an error-analyzed report.

```
data/sample_prompts.csv  ──┐
                           │
                           ├──► evaluate.py ──► outputs/adherence_predictions.csv
                           │           │   ──► outputs/adherence_confusion_matrix.png
data/manual_labels.csv   ──┘           │   ──► outputs/adherence_baseline_report.md
                                       │                  ▲
                                       │                  │
                          rule_based_classifier.py        │ written by
                              uses ▲                      │
                                   │              generate_report.py
                                   │
                              rubric.py
                          (LABELS, POLICY_TYPES,
                           DIRECT_ANSWER_PATTERNS,
                           REFUSAL_PATTERNS,
                           EXAMPLE_LANGUAGE_PATTERNS)
```

**Execution sequence** (`python src/adherence/evaluate.py`):

1. `_load_data()` — Reads both CSVs, validates required columns, validates label set, validates that prompt IDs and label IDs match exactly, and merges on `id`.
2. `_run_classifier(df)` — For each row, calls `classify_response(policy_type, tutor_response)`. The classifier returns a predicted label, a list of human-readable reason strings, and a dict of feature flags (word count, question count, sentence count, presence of direct-answer / refusal / example-language patterns).
3. `_compute_metrics(df)` — Computes accuracy, macro precision, macro recall, macro F1, and per-label precision/recall/F1/support using scikit-learn's `precision_recall_fscore_support`.
4. `_save_confusion_matrix(df, path)` — Renders a 3×3 confusion matrix as a matplotlib figure with counts overlaid.
5. `_collect_errors(df)` — Filters rows where `human_label != predicted_label` and packages them with their classifier reasons for the report's error analysis section.
6. `generate_markdown_report(metrics, errors, path)` — Pure rendering function. Takes the metrics dict and the errors list and writes the final markdown report.

**Classifier internals.** The classifier is a dispatch table mapping each of the five policy types to a dedicated decision function. Each function takes the precomputed feature flags and returns `(predicted_label, reasons)`:

```python
_DISPATCH = {
    "partial_hint":        _classify_partial_hint,
    "scaffolded_question": _classify_scaffolded_question,
    "immediate_reveal":    _classify_immediate_reveal,
    "socratic_only":       _classify_socratic_only,
    "worked_example":      _classify_worked_example,
}
```

The policy names match the named contrasts the paper deploys (§3.1, §7): `partial_hint` from the full-vs-partial hints contrast, `immediate_reveal` from the immediate-vs-delayed answer-reveal contrast, `worked_example` from the worked-examples lever in Hattie's inventory.

### 3.3 Pipeline B — DAG figures

```
data/hattie_variable_subset.csv ──► build_dag.py ──► validated nx.DiGraph
                                          ▲                       │
                                          │ uses                  │
                                  dag_schema.DAG_EDGES            │
                                                                  ▼
                                                         render_dag.py
                                                                  │
                                                                  ├──► outputs/hattie_taxonomy_dag.png
                                                                  ├──► outputs/hattie_taxonomy_dag.graphml
                                                                  ├──► outputs/clarity_retention_dag.png
                                                                  └──► outputs/clarity_retention_dag.graphml
```

**Execution sequence** (`python src/dag/render_dag.py`):

1. `build_graph(csv_path)` — Loads node metadata from CSV, attaches `label`, `taxonomy`, and `description` as node attributes, adds edges from `DAG_EDGES`, validates every edge references an existing node, validates acyclicity with `nx.is_directed_acyclic_graph`. Raises explicit errors on any validation failure.
2. `render_taxonomy_dag(graph, png_path, graphml_path)` — Renders the broader Hattie-style taxonomy DAG. Fixed node positions (no auto-layout), nodes colored by taxonomy (Context / Intervention / Diagnostic / Outcome), edges styled by source-taxonomy mechanism (treatment effect, context covariate, mediation to outcome). Two legends: node taxonomy and edge mechanism.
3. `render_mediation_dag(png_path, graphml_path)` — Builds the §2.2 mediation DAG inline (only four nodes), renders with sign annotations on every edge and Hattie's d ≈ −0.32 effect size on the grade-retention edge.

Both renderers write GraphML alongside the PNG so the graph can be reopened in dedicated graph-editing tools for final publication refinement.

---

## 4. Design decisions and rationale

When asked "why this and not that," here is how each design choice is defended.

| Decision | Rationale |
|---|---|
| **Rule-based classifier, not LLM-as-judge** | Auditability. Every prediction returns a human-readable reason string. An LLM judge gives a verdict you cannot inspect, which is the opposite of what "classifier validation" needs. The paper's §7 explicitly calls for a smaller fine-tuned model — listed as a future-work comparison. |
| **30 examples, 5 policies × 6** | Bounded by what one rater can label carefully and consistently in a single sitting. Scaling to 100+ examples is a labeling-workflow problem, not a code problem. |
| **Policy names match paper vocabulary** | `partial_hint`, `immediate_reveal`, `worked_example` map directly to the paper's named pedagogical contrasts. A reader of the paper can trace V1 policies back to specific sections (§3.1, §7). |
| **Manual labels live in a separate CSV from prompts** | A second rater can produce `manual_labels_rater2.csv` without ever seeing or touching the prompts file. This is the structure that enables Cohen's κ in the next sprint. |
| **Strict column validation at load time** | A bad CSV fails fast with a precise error message naming the missing column. The alternative — a stack trace 40 lines later inside scikit-learn — is hostile to whoever is debugging. |
| **`generate_report.py` separated from `evaluate.py`** | Report format will change as more raters, more metrics, and sensitivity analyses are added. Decoupling rendering from computation makes future report changes a one-file edit. |
| **Fixed DAG positions, not auto-layout** | Reproducibility. Same input CSV produces the same image byte-for-byte. Spring-layout algorithms shuffle on every run, which makes them useless for paper figures. |
| **Hard-coded edge list in `dag_schema.py`** | Causal structure is intent, not data. Putting it in code means a code review is required to change it, which is the right level of friction for a published claim. |
| **GraphML export alongside every PNG** | The PNG is the V1 deliverable; the GraphML is the handoff to yEd / Cytoscape for publication-grade typography and SVG export. |
| **`outputs/` committed to the repository** | The output IS the artifact. Anyone pulling the repository immediately sees the figures and report without needing to install dependencies or run anything. |
| **Edge mechanism encoded by source-node taxonomy** | Avoids a separate edge schema while still giving the reviewer the "edge annotations" they asked for — interventions style differently from context covariates, which style differently from mediation paths to the outcome. |

---

## 5. Baseline results

```
python src/adherence/evaluate.py
```

produces, on the V1 dataset:

| Metric | Value |
|---|---:|
| Total examples | 30 |
| Accuracy | 0.967 |
| Macro Precision | 0.970 |
| Macro Recall | 0.967 |
| Macro F1 | 0.967 |

| Label | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| ADHERENT | 0.909 | 1.000 | 0.952 | 10 |
| PARTIAL | 1.000 | 0.900 | 0.947 | 10 |
| NON_ADHERENT | 1.000 | 1.000 | 1.000 | 10 |

**Honest framing of the 0.967 number.** The examples were deliberately written to exercise the rule patterns used by the classifier. This metric measures the classifier's internal consistency against examples designed for it — not its real-world accuracy on unseen tutor responses. The number is high because the V1 dataset is internally calibrated; the validation gap the reviewer raised is *not* closed by this number. What this baseline does establish is the structure: a labeled dataset, a measurable error rate, a per-example error analysis, and a clear pipeline that can be re-run against larger datasets with multiple raters.

**The one misclassification** is an example that lies exactly on the 60-word threshold the `partial_hint` rule uses. The classifier called it `ADHERENT` (≤ 60 words); the human label was `PARTIAL` (response is verbose and walks through too many steps). This is a real threshold-brittleness case and is the kind of finding the V1 baseline is designed to expose.

---

## 6. Tests

13 tests pass (`pytest -q`):

| File | What it protects |
|---|---|
| `tests/test_classifier.py` | (1) invalid policy raises `ValueError`; (2) direct-answer language under `partial_hint` → `NON_ADHERENT`; (3) Socratic response with questions classifies as ADHERENT or PARTIAL; (4) `immediate_reveal` response is not unfairly marked NON_ADHERENT; (5) empty response does not crash; (6) focused scaffolded question is ADHERENT; (7) worked-example language is ADHERENT |
| `tests/test_dag.py` | (1) graph builds successfully; (2) graph is directed; (3) graph is acyclic; (4) all expected nodes exist; (5) all expected edges exist; (6) every node has `label`, `taxonomy`, and `description` attributes |

These tests protect the system against regressions: any change to the classifier dispatch, the policy logic, the graph schema, or the variable CSV will be caught immediately.

---

## 7. What V1 does not claim

For scope discipline, the V1 report explicitly does not claim any of the following:

- That the classifier is production-ready or finished.
- That the DAG figures are publication-grade (they are scaffolds; final figures need typography refinement and possibly vector-format conversion).
- That the reviewer feedback is fully resolved (only the two engineering-shaped concerns are addressed; eight others require paper-level work).
- That classifier error has been quantitatively connected to downstream causal estimates (this is Next Step #5 and is non-trivial).
- That the V1 classifier represents the eventual production architecture (Section 7 of the paper calls for a small, fast, fine-tuned model; the rule-based baseline exists for transparency and to be beaten).

---

## 8. Next steps

Phrased as **goals → unblocking work**, in priority order.

### Goal A — Defend the "we validated the classifier" claim against a careful reviewer

The single biggest weakness of V1 is that it has one rater. The strongest single thing we can do next is add a second rater.

1. **Recruit a second annotator.** Ideally someone with pedagogy or learning-science background; minimally, someone who can apply the rubric consistently.
2. **Have the second rater produce `data/manual_labels_rater2.csv`** without seeing rater 1's labels.
3. **Compute Cohen's κ** between rater 1 and rater 2. The result tells us how interpretable the rubric actually is. Low κ on a particular policy means the rubric for that policy needs sharpening; high κ means we have ground truth worth defending.
4. **Expand from 30 to 100+ examples** with rater 2 already in the loop, so all new examples are dual-labeled from the start.
5. **Recompute classifier metrics against the consensus labels** (or against majority vote, depending on κ). This becomes the V2 baseline.

### Goal B — Show the reviewer how classifier error affects downstream causal estimates

The reviewer's deeper concern is not just "validate the classifier" — it is "show how classifier error propagates into the causal claims it gates." This is what genuinely closes their argument.

1. **Set up a synthetic causal experiment.** Take a known synthetic effect size; generate fake "LLM outputs" with known adherence; inject classifier error at a rate matching the V1 baseline.
2. **Measure how the estimated effect drifts** as classifier error rate varies. This produces a sensitivity curve.
3. **Add the sensitivity analysis to the baseline report** as a new section. This is what genuinely answers the reviewer.

### Goal C — Promote DAG figures from V1 to publication-grade

1. **Load both GraphML files into yEd**, refine typography, export SVG and PDF.
2. **Add textual edge rationale labels** (currently the taxonomy DAG carries only mechanism-by-color; the published version should name each mechanism explicitly per-edge).
3. **Have the Medhavi paper authors confirm** the §2.2 figure is the canonical version going forward, and update the manuscript to reference it.

### Goal D — Scale the policy taxonomy to match the paper's experimental design

The V1 has five policy types. The paper actually frames policies as *contrasts* (A vs B). To run real Mode-2 (adaptive) or Mode-3 (RCT) experiments, both arms of each contrast need to be labeled, classified, and adherence-checked.

1. **Add the missing pair-arms**: `full_hint` to pair with `partial_hint`; `delayed_reveal` to pair with `immediate_reveal`; `specific_feedback` vs `generic_feedback` as a new contrast; `error_location_only` as the paper's verbatim policy.
2. **Generate labeled examples for each new arm**, following the same 6-per-policy structure.
3. **Update the classifier dispatch** to score adherence to each new policy.

This is a labeling-and-rubric expansion, not architecture work, but it is the bridge from "we can score adherence" to "we can run the platform's experimental modes."

### Goal E — Replace the rule-based baseline with a model-based classifier

The rule-based classifier is intentionally a baseline. Paper §7 calls for a smaller, faster fine-tuned model.

1. **Build an LLM-as-judge classifier** (zero-shot, then few-shot) against the same labeled dataset; compare to the rule-based baseline.
2. **Fine-tune a small classifier** (e.g., DistilBERT or a small open-weights LLM) on the V2 dataset with consensus labels.
3. **Report all three side-by-side** in the V2 evaluation: rule-based, LLM-judge, fine-tuned. Whichever wins is the V2 production classifier; the others remain as ablations.

---

## 9. How to run

From the repository root:

```bash
# One-time setup
python -m venv .venv
.venv\Scripts\activate            # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# Run the adherence baseline
python src/adherence/evaluate.py

# Render both DAG figures
python src/dag/render_dag.py

# Run all tests
pytest
```

All outputs land in `outputs/`. The repository commits these outputs so a reader does not need to run anything to see the artifacts.

---

## 10. Appendix — File inventory by purpose

**Data (3 files)**
- `data/sample_prompts.csv` — 30 tutor responses with policy assignments
- `data/manual_labels.csv` — human labels with one-line reasons
- `data/hattie_variable_subset.csv` — 10 DAG nodes with taxonomy and description

**Source (7 files + `__init__.py`)**
- `src/adherence/rubric.py` — constants
- `src/adherence/rule_based_classifier.py` — per-policy decision logic
- `src/adherence/generate_report.py` — markdown report renderer
- `src/adherence/evaluate.py` — orchestrator
- `src/dag/dag_schema.py` — edge list
- `src/dag/build_dag.py` — graph constructor
- `src/dag/render_dag.py` — figure renderer

**Tests (2 test files + `conftest.py`)**
- `tests/test_classifier.py` — 7 tests
- `tests/test_dag.py` — 6 tests

**Documentation (5 files)**
- `README.md` — quick-start
- `docs/adherence_rubric.md` — policy-by-policy adherence definitions
- `docs/progress_update.md` — short meeting-ready update
- `docs/reviewer_response_notes.md` — reviewer-concern → V1-status mapping
- `docs/v1_engineering_report.md` — this document

**Generated outputs (5 files)**
- `outputs/adherence_baseline_report.md`
- `outputs/adherence_predictions.csv`
- `outputs/adherence_confusion_matrix.png`
- `outputs/hattie_taxonomy_dag.png` (+ `.graphml`)
- `outputs/clarity_retention_dag.png` (+ `.graphml`)

---

## 11. The one-sentence end-state

> *This V1 closes the two engineering-shaped reviewer concerns; the path from here to a fully validated classifier and publication-grade figures is a labeling and refinement problem, not an architecture problem.*
