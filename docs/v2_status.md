# Medhavi Reviewer-Response — V2 Status

**Author:** Sripathi (sripathi.sa@northeastern.edu)
**Date:** 2026-05-10
**Status:** V1 complete + V2 partial (Goals B partial-implemented; A and C scaffolded; D and E pending)

---

## TL;DR

V1 closed the two engineering-shaped reviewer concerns (adherence classifier validation gap, DAG ASCII figure). V1.5 — the work in this update — adds the two highest-value items that did **not** require external resources to start:

- **Goal B (sensitivity analysis) — implemented.** A synthetic randomized-trial simulator quantifies how adherence-classifier error propagates into causal-effect estimate bias. Produces a sweep curve, a results table, and a markdown report. This directly answers the reviewer's deeper concern.
- **Goal A (interrater reliability) — scaffolded.** A Cohen's κ script is ready to consume a second-rater label file the moment one exists. Tests for the κ implementation already pass.
- **Goal C (DAG polish, partial) — done.** SVG exports added for both DAG figures, alongside the existing PNG and GraphML outputs.

What still needs external input is documented in §4 (Blockers).

**Test status:** 28 / 28 passing (V1: 13; V2 additions: 15 — 9 sensitivity + 6 interrater).

---

## 1. What has been done — complete inventory

### 1.1 V1 deliverables (already shipped)

| Artifact | Purpose | File |
|---|---|---|
| Adherence rubric | Defines policy-by-policy adherence criteria using the paper's vocabulary | [docs/adherence_rubric.md](docs/adherence_rubric.md) |
| Labeled dataset | 30 hand-written tutor responses, 5 policy types × 6 examples | [data/sample_prompts.csv](data/sample_prompts.csv), [data/manual_labels.csv](data/manual_labels.csv) |
| Rule-based classifier | Transparent baseline with reason strings per prediction | [src/adherence/rule_based_classifier.py](src/adherence/rule_based_classifier.py) |
| Evaluator | Loads data, validates, classifies, computes metrics, writes artifacts | [src/adherence/evaluate.py](src/adherence/evaluate.py) |
| Baseline report | Metrics table, per-label scores, error analysis | [outputs/adherence_baseline_report.md](outputs/adherence_baseline_report.md) |
| Confusion matrix | 3×3 over ADHERENT / PARTIAL / NON_ADHERENT | [outputs/adherence_confusion_matrix.png](outputs/adherence_confusion_matrix.png) |
| §2.2 mediation DAG | Direct figure replacement of the paper's ASCII DAG | [outputs/clarity_retention_dag.png](outputs/clarity_retention_dag.png) |
| Taxonomy DAG | Visualizes the paper's intervention/diagnostic/context centerpiece | [outputs/hattie_taxonomy_dag.png](outputs/hattie_taxonomy_dag.png) |
| GraphML exports | Handoff format for yEd / Cytoscape typography refinement | `outputs/*.graphml` |

### 1.2 V1.5 deliverables (added in this update)

| Artifact | Purpose | File |
|---|---|---|
| Sensitivity simulator | Synthetic trial generator + classifier-error injector | [src/sensitivity/simulate.py](src/sensitivity/simulate.py) |
| Sensitivity sweep | PP & ITT estimates across 11 classifier-error settings | [src/sensitivity/run_analysis.py](src/sensitivity/run_analysis.py) |
| Sensitivity curve | Plot of estimated effect vs classifier error rate | [outputs/sensitivity_curve.png](outputs/sensitivity_curve.png) |
| Sensitivity sweep table | One row per error-rate setting, with PP/ITT means, SDs, and bias | [outputs/sensitivity_predictions.csv](outputs/sensitivity_predictions.csv) |
| Sensitivity report | Setup, headline results, interpretation, scope limits | [outputs/sensitivity_report.md](outputs/sensitivity_report.md) |
| Cohen's κ infrastructure | Two-rater agreement scoring with per-policy breakdown | [src/adherence/interrater.py](src/adherence/interrater.py) |
| SVG figure exports | Vector-format versions of both DAG figures | `outputs/*_dag.svg` |
| Sensitivity tests | 9 tests covering simulator, error injector, sweep logic | [tests/test_sensitivity.py](tests/test_sensitivity.py) |
| Interrater tests | 6 tests covering κ edge cases and Landis & Koch interpretation | [tests/test_interrater.py](tests/test_interrater.py) |

### 1.3 Tests (28 total, all passing)

| File | Count | Protects |
|---|---:|---|
| [tests/test_classifier.py](tests/test_classifier.py) | 7 | Per-policy decision logic, invalid input, empty input |
| [tests/test_dag.py](tests/test_dag.py) | 6 | Graph construction, directedness, acyclicity, expected nodes/edges/attrs |
| [tests/test_sensitivity.py](tests/test_sensitivity.py) | 9 | Simulator shapes, seed reproducibility, error-injection edge cases, PP recovers θ when classifier is perfect, ITT attenuation, sweep monotonicity |
| [tests/test_interrater.py](tests/test_interrater.py) | 6 | κ at perfect/zero/chance/negative agreement, schema validation, interpretation buckets |

---

## 2. Headline V1.5 result — sensitivity analysis

The sensitivity simulator generates synthetic randomized-trial data with:

- Binary treatment T ~ Bernoulli(0.5)
- True adherence A ~ Bernoulli(0.85)
- Outcome Y = θ · T · A + N(0, 1), with true effect θ = 0.5
- 1,000 units per trial, 200 trials per error-rate setting, 11 settings across [0, 0.5]

**What the curve shows:**

| Scenario | Classifier error rate | PP estimate | Bias vs θ |
|---|---:|---:|---:|
| Perfect classifier | 0.000 | 0.504 | +0.004 |
| Moderate error (10%) | 0.100 | 0.495 | −0.005 |
| Moderate error (20%) | 0.200 | 0.484 | −0.016 |
| High error (50%) | 0.500 | 0.432 | −0.068 |

The intent-to-treat estimate is constant at ≈0.43 because the classifier does not affect ITT. The per-protocol estimate is unbiased at zero classifier error and drifts toward the ITT estimate as classifier error rises — exactly the mechanism the reviewer asked to see quantified.

**Why this is useful in the meeting:** when someone asks *"so does classifier error actually matter?"*, the answer is now *"here is the bias drift curve as a function of classifier error rate, and here is where the V1 baseline sits on it."*

---

## 3. What needs to be done — the V2 roadmap

Phrased as **goal → unblocking work**, in priority order. Each goal lists the *minimal* next step that produces a meaningful artifact.

### Goal A — Real classifier validation (single biggest priority)

**Status:** Cohen's κ infrastructure ready ([src/adherence/interrater.py](src/adherence/interrater.py)); awaiting a second rater.

**Minimal next step:**
1. Recruit a second annotator with pedagogy or learning-science background.
2. Share [docs/adherence_rubric.md](docs/adherence_rubric.md) and [data/sample_prompts.csv](data/sample_prompts.csv) (NOT the labels).
3. Produce `data/manual_labels_rater2.csv` with the same schema as the rater-1 file.
4. Re-run `python src/adherence/interrater.py` to produce κ overall and per-policy.

**Then expand:** label 70 more examples (target 100 total) with the second rater in the loop from the start so all new data is dual-labeled.

**Estimated effort:** 6–10 hours for the second rater on the existing 30; 1–2 days for the expansion to 100.

### Goal B — Sensitivity analysis extensions

**Status:** Base case implemented. Three useful extensions remain.

**Minimal next steps:**
1. **Asymmetric error model.** Replace the symmetric flip with separate false-positive and false-negative rates. Real classifiers are rarely symmetric.
2. **Variable adherence rate sweep.** Currently fixed at 0.85; sweep across [0.5, 0.95] to see how the bias surface depends on baseline adherence.
3. **Sweep grounded in the V2 empirical error rate.** Once Goal A produces a real κ-based error estimate, pin the sweep around that point and quote the resulting bias as a confidence interval rather than a synthetic curve.

**Estimated effort:** ~1 day for the asymmetric model and adherence sweep; depends on Goal A for the empirical pinning.

### Goal C — Publication-grade DAGs (partial complete)

**Status:** SVG export done. Typography refinement and edge text labels still pending.

**Minimal next steps:**
1. Open `outputs/hattie_taxonomy_dag.svg` in yEd or Adobe Illustrator.
2. Tighten typography: consistent font family across labels, edge-label positioning that does not overlap nodes, balanced node sizes.
3. Add textual edge labels (currently the taxonomy DAG carries mechanism-by-color + legend; the published version should name each mechanism explicitly per-edge for readers who do not consult the legend).
4. Export final SVG and PDF for the manuscript.

**Estimated effort:** ~3 hours with someone who has design judgment. The GraphML files exist specifically for this handoff.

### Goal D — Scale policy taxonomy to A-vs-B contrasts

**Status:** Not started. Requires alignment with paper authors.

**Minimal next steps:**
1. **30-minute meeting** with the paper authors to confirm which named contrasts (full-vs-partial hint, immediate-vs-delayed reveal, specific-vs-generic feedback) are actually deployed.
2. Extend `POLICY_TYPES` in [src/adherence/rubric.py](src/adherence/rubric.py) to include both arms of each confirmed contrast (e.g., add `full_hint`, `delayed_reveal`, `specific_feedback`, `generic_feedback`).
3. Add 6 labeled examples per new policy arm to [data/sample_prompts.csv](data/sample_prompts.csv) and [data/manual_labels.csv](data/manual_labels.csv).
4. Implement classifier dispatch for each new arm.
5. Re-run evaluate and document the new baseline.

**Estimated effort:** ~2 days after the alignment meeting.

### Goal E — Model-based classifier comparison

**Status:** Not started. Easy to start; requires API credits.

**Minimal next steps:**
1. Add `src/adherence/llm_judge.py` with a small interface that calls an LLM (Claude / GPT-4 / a local Llama via Ollama) with rubric + tutor response + assigned policy, returns predicted label.
2. Run the LLM judge over the V1 dataset; compare against rule-based baseline and (when available) consensus human labels.
3. **Once Goal A produces consensus labels for 100+ examples**, fine-tune a small open-weights classifier (DistilBERT or similar) and add it to the comparison.
4. Report all three classifier variants side-by-side in `outputs/classifier_comparison.md`.

**Estimated effort:** ~1 day for the LLM judge scaffold; ~2 days for the fine-tune once Goal A data exists.

### Goal F — Connect classifier error to the Medhavi paper's causal estimands

**Status:** Not started. This is the long-term goal.

**Minimal next steps:**
1. Take the actual causal estimand the paper claims (e.g., the ATE for a specific Mode-3 RCT contrast).
2. Replace the synthetic sensitivity simulator with a model using the paper's actual variable taxonomy and DAG.
3. Inject empirically-measured classifier error rates (from Goal A) and report bias bounds on the paper's actual claims.

This is what genuinely closes the reviewer loop in a way that survives a careful second review.

**Estimated effort:** 1–2 weeks, dependent on Goals A, D, and possibly a g-methods consultation.

---

## 4. Blockers — what I cannot do alone

Ranked by **what unblocks the most for the smallest ask**.

### Tier 1 — Critical path (one ask, biggest unblock)

- **Second annotator (~6–10 hours of someone's time).** Without this, "validated classifier" stays a one-rater claim and Cohen's κ cannot be computed. The infrastructure is ready and waiting in [src/adherence/interrater.py](src/adherence/interrater.py); it just needs a `manual_labels_rater2.csv` to consume.
  - Workaround if blocked: I can perform a delayed-blind self-relabel for intra-rater consistency, documented as such. Weaker than κ but better than nothing.

### Tier 2 — Genuine blockers on specific goals

- **Decision: does the Medhavi platform exist as runnable code?** The 30 V1 examples are hand-written, not real LLM output. To produce a defensible baseline at scale we need actual platform output. Gates Goals A and E.
- **30 minutes with the paper authors** to confirm the production policy taxonomy. Gates Goal D.
- **IRB clarification** if any V2 work is expected to touch real student data. Timelines are months, so worth starting the conversation early.

### Tier 3 — Accelerators (not blocking, but speed things up)

- Causal-inference reviewer (~2 hours) to sanity-check Goal B's simulation design and propose richer estimands for Goal F.
- Design help (~3 hours in yEd) for Goal C's typography pass.
- ~$5–20 API credits for the LLM-judge comparison in Goal E (or set up a local Llama).

### What is *not* a blocker

To save the PI's time, the following are NOT things I am waiting on:

- More engineering time on V1 itself. V1 is done; V1.5 is in.
- A larger model / fancier infrastructure. Rule-based is intentional for transparency.
- A new repo / refactor. Current structure absorbs V2 cleanly.
- A web UI or dashboard. Out of scope per the original V1 spec.

---

## 5. How to look at the work

```bash
# Adherence baseline (V1)
python src/adherence/evaluate.py

# DAG figures + GraphML + SVG (V1 + V1.5)
python src/dag/render_dag.py

# Classifier-error sensitivity analysis (V1.5)
python src/sensitivity/run_analysis.py

# Cohen's kappa (will print workflow if rater-2 file is missing)
python src/adherence/interrater.py

# All tests
pytest
```

All outputs land in `outputs/` and are committed for visibility.

---

## 6. One-sentence end-state

> **V1 closed the two engineering-shaped reviewer concerns; V1.5 quantifies how classifier error propagates into causal estimates and prepares the κ pipeline for the second rater; the remaining work is bounded by external inputs (a second annotator, a 30-minute alignment meeting, an IRB clarification) rather than by engineering capacity.**

---

## 7. Appendix — Full file inventory by purpose

**Data (3 files)**
- `data/sample_prompts.csv`
- `data/manual_labels.csv`
- `data/hattie_variable_subset.csv`
- *(future)* `data/manual_labels_rater2.csv` — pickled up by the κ script when present

**Source (V1: 7 files | V1.5: +3 files)**
- `src/adherence/rubric.py`
- `src/adherence/rule_based_classifier.py`
- `src/adherence/generate_report.py`
- `src/adherence/evaluate.py`
- `src/adherence/interrater.py` *(V1.5)*
- `src/dag/dag_schema.py`
- `src/dag/build_dag.py`
- `src/dag/render_dag.py` *(extended in V1.5 for SVG)*
- `src/sensitivity/simulate.py` *(V1.5)*
- `src/sensitivity/run_analysis.py` *(V1.5)*

**Tests (V1: 2 files / 13 tests | V1.5: +2 files / +15 tests = 28 total)**
- `tests/test_classifier.py`
- `tests/test_dag.py`
- `tests/test_sensitivity.py` *(V1.5)*
- `tests/test_interrater.py` *(V1.5)*

**Generated outputs (V1: 5 files | V1.5: +5 files)**
- V1: `adherence_baseline_report.md`, `adherence_predictions.csv`, `adherence_confusion_matrix.png`, `hattie_taxonomy_dag.png` + `.graphml`, `clarity_retention_dag.png` + `.graphml`
- V1.5: `sensitivity_curve.png`, `sensitivity_predictions.csv`, `sensitivity_report.md`, `hattie_taxonomy_dag.svg`, `clarity_retention_dag.svg`

**Documentation (5 files)**
- `README.md`
- `docs/adherence_rubric.md`
- `docs/progress_update.md`
- `docs/reviewer_response_notes.md`
- `docs/v1_engineering_report.md`
- `docs/v2_status.md` *(this document)*
