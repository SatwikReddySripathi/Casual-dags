# Medhavi Adherence Classifier V1 Baseline Report

## Purpose

This baseline responds to the reviewer concern that the post-generation adherence classifier is load-bearing but lacked validation.

## Dataset Summary

- Total examples: 30
- Policy types: immediate_reveal, partial_hint, scaffolded_question, socratic_only, worked_example
- Label set: ADHERENT, PARTIAL, NON_ADHERENT

## Metrics

| Metric | Value |
|---|---:|
| Accuracy | 0.967 |
| Macro Precision | 0.970 |
| Macro Recall | 0.967 |
| Macro F1 | 0.967 |

### Per-label scores

| Label | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| ADHERENT | 0.909 | 1.000 | 0.952 | 10 |
| PARTIAL | 1.000 | 0.900 | 0.947 | 10 |
| NON_ADHERENT | 1.000 | 1.000 | 1.000 | 10 |

## Confusion Matrix

See `adherence_confusion_matrix.png`.

## Error Analysis

Total misclassified examples: 1.

- **id=4** (policy: `partial_hint`) — human: `PARTIAL`, predicted: `ADHERENT`.
  - Response: First find a common denominator between 4 and 6. The least common multiple is 12. Then convert each fraction so both have denominator 12. After that add the numerators together over 12. Then simplify if possible by di...
  - Classifier reasoning: Short hint without direct answer language.

## Interpretation

This is not a final classifier. It is a validation scaffold that defines the construct, creates manually labeled examples, establishes measurable baseline error rates, and reveals where classifier errors may propagate into causal claims.

## Next Steps

1. Expand from 30 examples to 100+ examples.
2. Add two independent human raters.
3. Compute Cohen's kappa for interrater reliability.
4. Compare rule-based, LLM-as-judge, and fine-tuned classifier approaches.
5. Run sensitivity analysis showing how adherence classifier error affects causal estimates.
