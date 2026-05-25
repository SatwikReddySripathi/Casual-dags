# Medhavi Reviewer-Response — Progress Report

**Author:** Sripathi (sripathi.sa@northeastern.edu)
**Date:** 2026-05-10
**Approach:** Finish every engineering item I can do solo *first*; surface human-input asks only after solo work is exhausted.

---

## TL;DR

The reviewer raised ten ranked concerns plus three under-developed sections. I scoped the engineering response to the items code can actually address, then **deliberately ordered the plan so the solo-doable work comes first** — there is more solo work than I initially recognized, and finishing it before surfacing human asks means the eventual asks are sharper, smaller, and harder to refuse.

**Done so far:**
- **V1** closed the two reviewer concerns named directly: classifier validation gap (#3 MAJOR, half) and DAG-as-figure gap (#7 MINOR, full).
- **V1.5** quantified how classifier error propagates into causal-estimate bias (the *deeper* concern behind #3) and prepared the Cohen's κ pipeline for the eventual second annotator.
- **V1.6** shipped the bandit-inference / winner's-curse demo (Phase A item #1) — directly answers the reviewer's "premature convergence on a false best arm" worry with synthetic-data evidence and a bootstrap-based debiasing correction.

**Solo plan from here:** six additional engineering items I can complete without external input — listed in §3 below in priority order. After all six ship I will have closed every reviewer concern engineering can touch except real κ from a second rater. Only then do I surface human asks.

**Test status:** 39 / 39 passing. **Repo:** all V1 + V1.5 + V1.6 work in working tree (V1 + V1.5 already pushed at `ff8646b`; V1.6 pending push).

---

## 1. What has been built (V1 + V1.5)

### 1.1 V1 — the foundational scaffold

| Track | Deliverable | File |
|---|---|---|
| Adherence | Policy-adherence rubric tied to the paper's named contrasts | [docs/adherence_rubric.md](docs/adherence_rubric.md) |
| Adherence | 30 hand-written tutor responses, 5 policy types × 6 examples | [data/sample_prompts.csv](data/sample_prompts.csv), [data/manual_labels.csv](data/manual_labels.csv) |
| Adherence | Rule-based classifier with reason strings per prediction | [src/adherence/rule_based_classifier.py](src/adherence/rule_based_classifier.py) |
| Adherence | Evaluator + baseline report with metrics, per-label scores, error analysis | [src/adherence/evaluate.py](src/adherence/evaluate.py), [outputs/adherence_baseline_report.md](outputs/adherence_baseline_report.md) |
| DAG | §2.2 mediation DAG — direct figure replacement of the paper's ASCII figure | [outputs/clarity_retention_dag.png](outputs/clarity_retention_dag.png) |
| DAG | Hattie variable taxonomy DAG visualizing the paper's centerpiece idea | [outputs/hattie_taxonomy_dag.png](outputs/hattie_taxonomy_dag.png) |

### 1.2 V1.5 — first push into the V2 frontier

| Module | Deliverable | File |
|---|---|---|
| Sensitivity | Synthetic randomized-trial generator + classifier-error injector | [src/sensitivity/simulate.py](src/sensitivity/simulate.py) |
| Sensitivity | Sweep over classifier-error settings, computes PP & ITT estimates | [src/sensitivity/run_analysis.py](src/sensitivity/run_analysis.py) |
| Sensitivity | Bias curve directly answering the reviewer's "classifier error propagation" concern | [outputs/sensitivity_curve.png](outputs/sensitivity_curve.png) |
| Interrater | Cohen's κ infrastructure; prints rater-2 workflow until data exists | [src/adherence/interrater.py](src/adherence/interrater.py) |
| DAG polish | SVG exports for both figures | `outputs/*_dag.svg` |
| Tests | 15 new tests (9 sensitivity + 6 interrater) | [tests/](tests/) |

### 1.3 V1.6 — bandit-inference / winner's-curse demo (Phase A item #1)

| Module | Deliverable | File |
|---|---|---|
| Bandit | Winner's-curse simulator (K i.i.d. arms → pick empirical best → measure selection bias) | [src/bandit/simulate.py](src/bandit/simulate.py) |
| Bandit | Softmax bandit with exact recorded propensities (so IPW is well-defined) | [src/bandit/simulate.py](src/bandit/simulate.py) |
| Bandit | Naive vs IPW arm-mean estimators + bootstrap winner-debiasing | [src/bandit/inference.py](src/bandit/inference.py) |
| Bandit | Two demos + curves + sweep table + report | [src/bandit/run_analysis.py](src/bandit/run_analysis.py) |
| Bandit | Winner's-curse curve: bias grows from +0.038 (K=2) to +0.131 (K=20) on identical arms | [outputs/bandit_winners_curse.png](outputs/bandit_winners_curse.png) |
| Bandit | IPW-vs-naive curve under increasing allocation concentration | [outputs/bandit_ipw_vs_naive.png](outputs/bandit_ipw_vs_naive.png) |
| Tests | 11 new bandit tests; full suite now 39 / 39 | [tests/test_bandit.py](tests/test_bandit.py) |

### 1.4 Headline numbers

| Metric | Value |
|---|---:|
| Labeled examples | 30 |
| Policy types | 5 (named per paper §3.1, §7) |
| Adherence baseline accuracy | 0.967 |
| Adherence baseline macro F1 | 0.967 |
| Sensitivity: per-protocol bias at 20% classifier error | −0.016 |
| Sensitivity: per-protocol bias at 50% classifier error | −0.068 |
| Winner's-curse bias at K=5 identical arms (3000 sims) | +0.081 |
| Winner's-curse bias at K=20 identical arms (3000 sims) | +0.131 |
| Bootstrap debias on one K=5 run: observed 0.60 → debiased 0.53 (true 0.50) | — |
| Tests passing | 39 / 39 |

---

## 2. Reviewer-concern coverage as of today

| # | Severity | Concern | Engineering-addressable? | Status |
|---|---|---|---|---|
| 1 | CRITICAL | Brown 2026 sourcing | No (paper) | — |
| 2 | CRITICAL | Split paper into 2–3 submissions | No (paper) | — |
| 3 | MAJOR | Classifier validation | Yes | 75% done (error rate ✅, sensitivity ✅, κ infra ✅; real κ pending Phase B) |
| 4 | MAJOR | Mode 2 ethics / adaptive allocation | Partly | Underpowering side ✅ in V1.6; ethics side pending A4, A5 |
| 5 | MAJOR | §6 g-methods / time-varying treatment | Partly | Pending Phase A item #2 |
| 6 | MAJOR | Citation coverage gaps | No (paper) | — |
| 7 | MINOR | DAG figures (§2.2 ASCII) | Yes | 100% done in V1 |
| 8 | MINOR | "Does not replace Hattie" repetition | No (paper) | — |
| 9 | MINOR | Declarative mood §3–§4 | No (paper) | — |
| 10 | MINOR | "Genuine Learning Probability" terminology | No (paper) | — |
| — | flagged | Bandit inference literature missing | Yes | **Done in V1.6** (winner's curse + IPW + bootstrap debiasing) |
| — | flagged | Multiple comparisons not addressed | Yes | Pending Phase A item #3 |
| — | flagged | Interrupted time series ("fourth pattern") thin | Yes | Pending Phase A item #6 |

---

## 3. Phase A — solo work (do this first, in this order)

Each item is something I can complete without external input. Ordered by leverage per day. All seven items together: ~3 weeks of focused solo work.

### A1. Bandit inference / winner's curse demo *(SHIPPED in V1.6)*

**Status:** ✅ Complete.

**Addresses:** reviewer-flagged "bandit inference literature missing" + concern #4 underpowering worry.

**What shipped:** Two demos in [src/bandit/](src/bandit/) — (1) winner's-curse sweep showing the bias of the empirical-best arm grows from +0.038 (K=2) to +0.131 (K=20) on identical arms, with bootstrap-based debiasing as the corrector; (2) softmax bandit with exact recorded propensities, comparing naive vs IPW arm-mean estimators across allocation concentration levels. Honest finding for stationary Bernoulli arms: per-arm sample means are already unbiased even under adaptive allocation, so IPW pays variance for negligible bias gain — IPW's value-add lives in winner selection (Demo 1), contextual settings, and non-stationary arms.

**Artifacts shipped:** [src/bandit/](src/bandit/), [outputs/bandit_winners_curse.png](outputs/bandit_winners_curse.png), [outputs/bandit_ipw_vs_naive.png](outputs/bandit_ipw_vs_naive.png), [outputs/bandit_inference_report.md](outputs/bandit_inference_report.md), 11 new tests in [tests/test_bandit.py](tests/test_bandit.py).

**Pitch line:** *"The paper proposes Mode 2 (bandit-based adaptive allocation). I've built a synthetic demo showing the winner's-curse selection bias the reviewer worried about, plus a bootstrap debiasing correction. The IPW comparison is honest about where IPW does and doesn't help."*

### A2. G-methods feasibility demo *(~3 days)*

**Addresses:** concern #5 — §6 punts on time-varying causal inference.

**Method:** Extend the sensitivity simulator to multi-period treatments (e.g., 5 sessions × 100 students with time-varying confounding). Show naive regression underestimates the effect. Implement a minimal IPW-based marginal structural model on the synthetic data; show it recovers the truth.

**Artifacts:** `src/longitudinal/`, `outputs/gmethods_demo.png`, `outputs/gmethods_report.md`, tests.

**Pitch line:** *"The paper says g-methods can handle time-varying confounding without showing it can be done on platform-realistic data. I've built that demo."*

### A3. Multiple-comparisons correction demo *(~1 day)*

**Addresses:** reviewer-flagged multiple-testing gap.

**Method:** Simulate diagnostic-trigger escalation under repeated testing across content units. Show the false-positive escalation rate without correction. Implement Benjamini-Hochberg adjustment; show the corrected rate.

**Artifacts:** Lives in `src/sensitivity/` as a sibling of the classifier-error analysis. New: `outputs/multiple_comparisons_report.md`, tests.

### A4. Differential-attrition monitor *(~1 day)*

**Addresses:** concern #4 — Mode 2 ethics.

**Method:** A stream-style detector that triggers an alert when per-arm attrition differs by more than a pre-specified threshold. Tested on synthetic dropout sequences. The paper §3.2 calls this out as a "primary safety signal" — I'll build it.

**Artifacts:** `src/safety/attrition_monitor.py`, tests, doc.

### A5. Early-stopping safeguard for bandits *(~1 day)*

**Addresses:** concern #4 — reviewer's "premature convergence on false best arm" worry.

**Method:** Implement a pre-registered sequential test that halts bandit exploration if concentration on one arm happens before the cumulative sample is large enough to justify it. Tested on the synthetic bandit from A1.

**Artifacts:** `src/safety/early_stopping.py`, tests, integrates with A1 simulator.

### A6. Interrupted time series demo for the "fourth pattern" *(~2 days)*

**Addresses:** the reviewer flag on §1.3's fourth pattern being too thin.

**Method:** Simulate an always-on variable (e.g., "teacher clarity") with a known intervention at time t. Run an interrupted time series analysis. Show the internal-validity threats the reviewer mentioned (history, maturation, regression-to-mean) by injecting confounded simulations and seeing where ITS gets fooled.

**Artifacts:** `src/longitudinal/its.py` (sibling of A2 inside `longitudinal/`), `outputs/its_report.md`, tests.

### A7. Intra-rater consistency self-relabel + LLM-judge stub *(~1 day)*

**Addresses:** strengthens the Phase B human ask by removing every workaround-doable item before asking.

**Method:**
- **Intra-rater:** wait 14+ days, blindly re-label the 30 V1 examples, compute Cohen's κ against rater-1 (myself). This is a documented-as-weaker workaround for real κ but produces a number.
- **LLM-judge stub:** scaffold an LLM-as-judge classifier that calls a model API when a key is present and falls back to the rule-based baseline when it isn't. Ready to plug in real API access whenever Phase C credits land.

**Artifacts:** `data/manual_labels_rater1_blind.csv`, `outputs/intra_rater_report.md`, `src/adherence/llm_judge.py`, tests.

### Phase A end-state

After A1–A7 ship:

- Every engineering-addressable reviewer concern has a corresponding artifact.
- The classifier comparison is set up (rule-based + LLM-judge stub) and just needs API access to be a real three-way comparison.
- The κ pipeline has either intra-rater consistency (workaround) or is fully primed for inter-rater κ the moment the second annotator's labels exist.
- The Mode-2 safety story has actual code (attrition + early-stopping), not just a paper claim.
- The longitudinal claims have at least a feasibility demo, not just a hand-wave.

The only remaining engineering deliverable is the consolidated final report (`docs/medhavi_engineering_final.md`) — written after Phase A so it can cite all the artifacts.

---

## 4. Phase B — human-input asks (surface AFTER Phase A is done)

These are deferred until the solo work is complete, on purpose. Asking with the full Phase A inventory in hand makes each ask sharper and harder to deflect:

| Ask | Why I'm waiting until Phase A is done |
|---|---|
| **Second annotator (~6–10 hours)** for real Cohen's κ | After A7, I have intra-rater consistency as a fallback number. The real κ ask becomes "we need this to upgrade the existing intra-rater number, here's exactly the file format" — concrete, low-effort, undeniable. |
| **30-minute meeting with paper authors** on production policy taxonomy | After A1–A6, I have empirical demos for every architectural claim the paper makes. The meeting becomes "here are six demos that need the actual policy names to be production-aligned" — they get the value first, then the ask. |
| **IRB conversation start** | After A4 and A5, I have the safety scaffolding code that goes with an IRB submission. The conversation becomes "here's what the safety machinery does, what's the IRB framing?" instead of "do we need IRB?" |
| **Causal-inference reviewer (~2 hours)** to sanity-check A2 | After A2 ships, the ask is "review this code and report" — concrete review, not open-ended consultation. |
| **Design help (~3 hours in yEd / Illustrator)** for figure typography | All figures already exist in SVG. Designer's job is typography polish on a finished artifact. |
| **~$5–20 API credits** for real LLM-judge | A7's stub already exists. The ask becomes "fund this for an afternoon of inference calls, here's the script" — trivial. |

---

## 5. Phase C — final deliverables (after Phase A + B converge)

- **Consolidated final report** organized by reviewer concern, one row per concern with status / evidence / artifact.
- **Slide deck** for committee / PI: 8–12 slides walking reviewer-concern → engineering-response → result.
- **Reproducibility check** — fresh clone, `pip install -r requirements.txt`, run every script, verify outputs. `scripts/run_all.py` for one-command end-to-end.
- **Optional interactive demo** — Streamlit / Gradio app for sensitivity-curve exploration.

---

## 6. Definition of done — engineering response complete when

- [x] DAG figures replace ASCII (#7) — *V1*
- [x] Classifier baseline + error analysis (#3 part 1) — *V1*
- [x] Classifier error → causal estimate sensitivity (#3 part 2) — *V1.5*
- [x] Interrater infrastructure ready (#3 part 3) — *V1.5*
- [x] Bandit inference bias demo + bootstrap debiasing (Phase A1) — *V1.6*
- [ ] G-methods feasibility on time-varying treatments (Phase A2)
- [ ] Multiple-comparisons correction demo (Phase A3)
- [ ] Differential-attrition monitor (Phase A4)
- [ ] Bandit early-stopping safeguard (Phase A5)
- [ ] Interrupted time series demo for "fourth pattern" (Phase A6)
- [ ] Intra-rater consistency + LLM-judge stub (Phase A7)
- [ ] Real κ from second rater (Phase B)
- [ ] Consolidated final report + slides + reproducibility check (Phase C)

---

## 7. How to look at the work

```bash
# Adherence baseline
python src/adherence/evaluate.py

# DAG figures (PNG + SVG + GraphML)
python src/dag/render_dag.py

# Classifier-error sensitivity
python src/sensitivity/run_analysis.py

# Bandit inference + winner's curse (V1.6)
python src/bandit/run_analysis.py

# Cohen's κ (prints workflow until rater-2 file exists)
python src/adherence/interrater.py

# Tests
pytest
```

All outputs land in `outputs/` and are committed for visibility. Repo: https://github.com/SatwikReddySripathi/Casual-dags (`main`, head `ff8646b`).

---

## 8. One-sentence end-state

> **There is more solo work left than the V1.5 update made visible; finishing all seven Phase A items first means the eventual human asks land with maximum leverage and minimum scope, and means the project does not stall on anyone else's calendar in the meantime.**
