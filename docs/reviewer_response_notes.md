# Reviewer Response Notes — V1 Implementation

## Reviewer Concern 1: Adherence classifier validation

The reviewer noted that the post-generation adherence classifier is load-bearing because it supports the claim that the LLM executed the assigned pedagogical policy.

## V1 Response

We created a first validation scaffold:
- Defined a policy-adherence rubric using the paper's named pedagogical contrasts (`partial_hint`, `immediate_reveal`, `worked_example`, plus `scaffolded_question` and `socratic_only`). See `docs/adherence_rubric.md` for the contrast-to-policy mapping.
- Created a small manually labeled sample (30 examples, 5 policies x 6 examples).
- Implemented a transparent rule-based baseline classifier.
- Reported baseline metrics and errors.

## Remaining Work

- Increase sample size.
- Add multiple raters.
- Compute interrater reliability (Cohen's kappa).
- Compare rule-based and model-based classifiers — the paper §7 calls for a smaller, faster fine-tuned model.
- Add the contrast pair for every policy (e.g., `full_hint` to pair with `partial_hint`; `delayed_reveal` to pair with `immediate_reveal`; `specific_feedback` vs `generic_feedback`) so the classifier can score adherence on both arms of each experimental contrast.
- Analyze how classifier error affects downstream causal estimates.

## Reviewer Concern 2: DAG visualization quality

The reviewer noted that the DAG should be a proper figure rather than ASCII-style text, and specifically pointed at the clarity/grade-retention DAG in paper §2.2.

## V1 Response

Two figures are produced from `src/dag/render_dag.py`:

1. **`outputs/clarity_retention_dag.png`** — directly replaces the ASCII DAG in paper §2.2 (Teacher Clarity → Meeting Grade-Level Standards → Grade Retention → Achievement, plus the direct path from Meeting Grade-Level Standards to Achievement). Edges carry sign annotations and Hattie's effect size on the grade-retention edge.
2. **`outputs/hattie_taxonomy_dag.png`** — a broader figure that visualizes the framework's centerpiece (the intervention/diagnostic/context decomposition the reviewer called the paper's "best idea"). Edges are styled by source-taxonomy mechanism (treatment effect, context covariate, mediation) and the figure carries two legends: one for node taxonomy and one for edge mechanism.

GraphML exports are produced alongside each PNG so the figures can be loaded into yEd/Gephi/Cytoscape for further refinement before publication.

## Mapping of variables to GLP Y-components (paper §5.2)

The descriptions in `data/hattie_variable_subset.csv` now name the GLP overlap for the diagnostic nodes:

| V1 diagnostic | Paper's GLP component |
|---|---|
| `student_confidence` | Y4 Uncertainty Calibration |
| `error_rate` | Y2 Error Trajectory Coherence |
| `hint_dependency` | Y7 Scaffolding Response Curve |

This makes the relationship between the V1 diagnostics and the paper's outcome layer explicit without taking a position on the Brown 2026 sourcing concern the reviewer raised.

## Remaining Work

- Expand variable coverage.
- Add edge rationale text labels (not just mechanism color/style) to the taxonomy DAG.
- Create publication-ready vector graphics (SVG/PDF).
- Align DAG examples with the final paper scope as it stabilizes.

## Out-of-scope reviewer concerns (intentionally not addressed in V1)

Per the V1 spec in `CLAUDE.md`, this artifact addresses only the two actionable engineering critiques. The following concerns the reviewer raised require paper-level revision and are intentionally not in scope:

- Brown 2026 sourcing problem (CRITICAL).
- Splitting the paper into 2-3 venues (CRITICAL).
- Mode 2 adaptive-allocation ethics treatment.
- §6 g-methods / time-varying causal inference implementation detail.
- Citation coverage gaps (Hattie critique literature, bandits in education, adaptive trial ethics, LLM-in-education).
- Writing-craft fixes ("does not replace Hattie" repetition, declarative mood in §3-§4, "Genuine Learning Probability" terminology).
