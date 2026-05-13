# Medhavi V1 GitHub And Call Prep

## What this repository is

This repository is a focused reviewer-response artifact for the Medhavi framework paper. It does not implement the full tutoring platform. It turns two reviewer criticisms from `medhavi_review.md` into concrete, inspectable work:

1. The paper's post-generation adherence classifier was load-bearing but not validated.
2. The paper's DAGs needed to move from informal ASCII-style sketches to proper figures.

That is why the repository has two main tracks:

- `src/adherence/` builds a first validation scaffold for policy-adherence checking.
- `src/dag/` builds a clean DAG figure from structured node and edge data.

## How the repo maps to the review

The central review document is `medhavi_review.md`. The implementation directly answers two specific ranked improvements:

- `Reviewer Concern 1`: the reviewer said the adherence classifier needs validation because it supports the claim that the LLM actually executed the assigned tutoring policy.
- `Reviewer Concern 2`: the reviewer said a DAG-based paper should show proper DAG figures, not ASCII art.

This repository is therefore intentionally narrow. Instead of trying to fix the whole paper at once, it creates a defendable V1 response on the two most actionable engineering items.

## Directory walkthrough

- `medhavi_review.md`
  The source critique. This is the reason the repo exists.

- `README.md`
  High-level framing, setup, commands, outputs, and scope.

- `docs/adherence_rubric.md`
  Human labeling criteria for whether a tutor response followed its assigned pedagogical policy.

- `docs/reviewer_response_notes.md`
  Short mapping from reviewer concern to implementation response and remaining gaps.

- `docs/progress_update.md`
  Plain-language progress summary suitable for meetings.

- `data/sample_prompts.csv`
  Small synthetic evaluation set with policy type, student prompt, and tutor response.

- `data/manual_labels.csv`
  Human labels and rationales for the same examples.

- `data/hattie_variable_subset.csv`
  Structured node metadata for the DAG figure.

- `src/adherence/rubric.py`
  Canonical label set, policy types, and pattern lists used by the rule-based baseline.

- `src/adherence/rule_based_classifier.py`
  Transparent heuristic classifier that turns response features into adherence labels.

- `src/adherence/evaluate.py`
  Evaluation pipeline that loads data, runs the classifier, computes metrics, writes predictions, plots the confusion matrix, and generates a Markdown report.

- `src/adherence/generate_report.py`
  Report writer for the baseline summary and error analysis.

- `src/dag/dag_schema.py`
  Declares the DAG edges explicitly.

- `src/dag/build_dag.py`
  Loads CSV node metadata, validates it, inserts edges, and checks acyclicity.

- `src/dag/render_dag.py`
  Renders the figure with taxonomy colors and exports both PNG and GraphML.

- `tests/`
  Smoke tests for classifier behavior and DAG integrity.

- `outputs/`
  Generated artifacts you can show in the call.

## Why these design decisions were taken

### 1. Small manual dataset instead of a large model-first approach

Reason:
The reviewer's criticism was about validation structure, not model sophistication. A small labeled set is enough to establish the construct, define the task clearly, and make the evaluation auditable.

How to explain it:
We prioritized a credible baseline over premature complexity. The immediate goal was to show that the validation problem is now measurable, not to claim production-grade classifier performance.

### 2. Transparent rule-based baseline instead of an opaque ML model

Reason:
For a reviewer response, transparency matters more than raw performance. Rules let people inspect why a label was produced and make error analysis easy.

How to explain it:
We chose the simplest baseline that a reviewer can audit line by line. If the baseline fails, we learn where the construct is ambiguous. If it succeeds, we have a reference point for stronger models later.

### 3. Three-label adherence scheme: `ADHERENT`, `PARTIAL`, `NON_ADHERENT`

Reason:
The reviewer explicitly raised the difficulty of pedagogical adherence judgments. A middle category avoids forcing borderline cases into an artificial binary.

How to explain it:
Pedagogical compliance is not always all-or-nothing. The `PARTIAL` label captures responses that mostly follow the policy but help too much or mix styles.

### 4. Rubric-first workflow

Reason:
Without a rubric, labeling is not stable and classifier evaluation is meaningless.

How to explain it:
The rubric defines the construct before the classifier tries to predict it. That keeps the work grounded in human criteria rather than reverse-engineering labels from model behavior.

### 5. Generated reports and confusion matrix

Reason:
The output needs to be meeting-ready and reproducible.

How to explain it:
We did not want a one-off notebook result. The repo regenerates predictions, metrics, and error analysis from source data so the progress is inspectable and repeatable.

### 6. Structured CSV plus schema-driven DAG build

Reason:
Separating node metadata from edge definitions makes the DAG easier to extend and validate.

How to explain it:
The DAG is not just a picture. It is a data structure with explicit node roles and causal assumptions, which is closer to what the paper is claiming conceptually.

### 7. Fixed node positions in the figure

Reason:
Automatic graph layouts can shift between runs and often do not preserve conceptual grouping.

How to explain it:
We fixed the layout so the taxonomy reads left-to-right in a stable way: context, intervention, diagnostic, then outcome. That makes the figure more publication-friendly and reproducible.

### 8. GraphML export in addition to PNG

Reason:
PNG is for presentation; GraphML preserves structure for later editing or integration with other graph tools.

How to explain it:
We wanted both a showable artifact and a reusable graph representation.

### 9. Tests for both tracks

Reason:
Even though this is a small prototype, reviewer-response work still needs to be trustworthy.

How to explain it:
The tests protect the baseline assumptions: valid classifier behavior, expected DAG nodes and edges, and acyclicity.

## What the current repo demonstrates

### Adherence track

- A defined construct for pedagogical adherence.
- A manually labeled starter dataset of 30 examples across five policy types.
- A rule-based baseline classifier.
- A reproducible evaluation pipeline.
- A baseline report with error analysis.

Current result:
- Accuracy: `0.967`
- Macro F1: `0.967`
- Misclassifications: `1/30`

Important caveat:
This performance should not be oversold. The dataset is small, synthetic, and single-rater. The real contribution is that the validation gap is now explicit and instrumented.

### DAG track

- A taxonomy-aligned subset of Hattie-style variables.
- Explicit node metadata.
- Explicit causal edges.
- Validation that the graph is a DAG.
- A clean color-coded figure and GraphML export.

Important caveat:
This is a V1 mockup, not the final paper DAG set. It proves that the paper can move from informal diagrams to reproducible publication-quality graphics.

## Suggested talk track for the call

## 30-second version

I took the reviewer comments and converted them into two concrete engineering deliverables. First, I built a validation scaffold for the load-bearing adherence classifier: rubric, labeled examples, transparent baseline, metrics, and error analysis. Second, I replaced the weak DAG sketching approach with a reproducible graph pipeline that generates a clean figure and a reusable graph file.

## 2-minute version

The review made it clear that two parts of the paper needed concrete backing. The first was the adherence classifier, because the paper relies on it to claim that the LLM actually followed the assigned pedagogy. So I created a V1 validation scaffold rather than jumping straight to a more complex model. That includes a rubric, 30 manually labeled examples, a transparent rule-based baseline, and a script that regenerates predictions, metrics, a confusion matrix, and a Markdown report. The current score is strong on the toy dataset, but the main point is not the number. The point is that the validation problem is now explicit, measurable, and ready for expansion with multiple raters and larger samples.

The second issue was the DAG presentation. The review called out that a DAG-heavy paper should not rely on ASCII-style diagrams. I built a structured DAG pipeline using CSV node metadata, an explicit edge schema, graph validation, and a rendering step that outputs both a presentation-ready PNG and GraphML. That gives us a cleaner figure now and a base we can expand later for the final paper.

## Points to emphasize if someone challenges scope

- This is intentionally a reviewer-response V1, not the full Medhavi platform.
- The goal was to answer the two most actionable implementation critiques first.
- I chose transparency and reproducibility over sophistication.
- The repo creates a path to stronger evidence rather than pretending the validation problem is solved.

## Likely questions and good answers

### Why use a rule-based classifier first?

Because the immediate need was a transparent baseline that makes the validation problem auditable. A more advanced model would be harder to interpret before the rubric and labels were stable.

### Does 96.7% accuracy mean the classifier problem is solved?

No. The dataset is small and synthetic, so that metric is only a baseline signal. The real contribution is the evaluation framework, not a claim of final validity.

### Why include a `PARTIAL` class?

Because pedagogical adherence has gray areas. Some responses mostly follow policy but help too much or mix styles, and collapsing those into a binary label would distort the task.

### Why build the DAG from files instead of drawing it manually?

Because the paper's claim is structural and causal, not purely visual. Encoding nodes and edges in data makes the figure reproducible, testable, and extensible.

### What still remains weak?

The classifier still needs more data, multiple raters, interrater reliability, and sensitivity analysis. The DAG still covers only a small subset and should eventually move to vector-first publication assets.

## GitHub preparation

This directory has now been initialized locally as a Git repository. The remaining GitHub steps are to create the first commit, attach a remote, and push.

### Suggested local commands

```bash
git branch -M main
git add .
git commit -m "Initial Medhavi reviewer-response V1 baseline"
```

### Then connect GitHub

Create an empty GitHub repository and run:

```bash
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

### Suggested repository name

- `medhavi-reviewer-response-v1`
- `medhavi-adherence-dag-baseline`
- `medhavi-v1-review-response`

### Suggested GitHub description

Reviewer-response prototype for Medhavi: adherence-classifier validation scaffold and reproducible DAG figure pipeline.

## What to say while showing the repo

Start at `README.md` to frame scope.

Then show:

1. `medhavi_review.md`
   Explain that the repo is grounded in explicit reviewer criticism.
2. `docs/adherence_rubric.md`
   Show that the construct was defined before modeling.
3. `data/sample_prompts.csv` and `data/manual_labels.csv`
   Show the evaluation data and human labeling.
4. `src/adherence/rule_based_classifier.py`
   Emphasize transparency and baseline intent.
5. `outputs/adherence_baseline_report.md` and the confusion matrix
   Show measurable results and error analysis.
6. `src/dag/render_dag.py` and `outputs/hattie_taxonomy_dag.png`
   Show the move from informal diagrams to clean figures.
7. `tests/`
   End by showing that the artifact is runnable and checked.

## Detailed next-step plan

### Phase 1: Strengthen the adherence evidence

1. Expand the labeled set from 30 to at least 100 to 200 examples.
2. Add at least one independent second rater for every example.
3. Compute interrater reliability such as Cohen's kappa.
4. Refine the rubric where raters disagree.
5. Split data into development and held-out evaluation sets.
6. Add per-policy metrics so weak policy categories are visible.
7. Compare the rule baseline against an LLM-as-judge baseline and a lightweight supervised model.
8. Run sensitivity analysis showing how classifier error would affect downstream causal claims.

### Phase 2: Improve the DAG artifacts

1. Expand beyond the small Hattie subset to the variables most relevant to the paper's final framing.
2. Add written rationale for each edge so the graph is defensible in the manuscript.
3. Export SVG or PDF versions for publication use.
4. Create one or two paper-specific DAGs instead of one generic taxonomy mockup.
5. Align node names and edge assumptions tightly with the manuscript language.

### Phase 3: Tighten the paper-repo connection

1. Add a short matrix mapping each reviewer criticism to a repo artifact.
2. Quote the relevant reviewer lines directly in a response memo.
3. Clarify in the manuscript that the adherence classifier is now under active validation rather than assumed valid.
4. Reframe the DAG contribution as reproducible visual support for the taxonomy and causal claims.

### Phase 4: Prepare for stronger research claims

1. Add discussion of how classifier error propagates into ITT versus per-protocol analyses.
2. Define what deployment-time human oversight would look like for borderline adherence cases.
3. Add governance notes for data collection, rater protocols, and versioned labeling.
4. Decide whether the next milestone is a better baseline model, a bigger labeled dataset, or a manuscript revision pass.

## Best one-sentence summary

I translated two reviewer criticisms into a small but reproducible engineering artifact: a measurable baseline for policy-adherence validation and a proper DAG generation pipeline that supports the paper's causal framing.
