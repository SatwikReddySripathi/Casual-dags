# Classifier-error Sensitivity Analysis — V2

## Purpose

This analysis directly answers the reviewer's deeper concern about the adherence classifier: not just whether the classifier is validated, but how classifier error propagates into the causal estimates the classifier gates. A per-protocol estimate that filters on a noisy adherence prediction is biased; this sweep quantifies that bias as a function of classifier error rate.

## Simulation setup

- True treatment effect θ = 0.5
- Synthetic randomized trial: T ~ Bernoulli(0.5), A ~ Bernoulli(adherence_rate), Y = (θ · T if A=1 else 0) + N(0, 1).
- 200 independent trials of 1000 units per error-rate setting.
- Symmetric classifier error model: each true label is flipped independently with probability `classifier_error_rate`.

## Headline results

| Scenario | Classifier error rate | PP estimate (mean) | PP bias vs θ |
|---|---:|---:|---:|
| Perfect classifier | 0.000 | 0.505 | +0.005 |
| V1 baseline-rate match (~1/30) | 0.050 | 0.501 | +0.001 |
| Worst case in sweep | 0.500 | 0.433 | -0.067 |

## Full sweep

| Classifier error | PP mean | PP SD | PP bias | ITT mean | ITT bias |
|---:|---:|---:|---:|---:|---:|
| 0.000 | 0.505 | 0.068 | +0.005 | 0.429 | -0.071 |
| 0.050 | 0.501 | 0.070 | +0.001 | 0.429 | -0.071 |
| 0.100 | 0.496 | 0.072 | -0.004 | 0.429 | -0.071 |
| 0.150 | 0.491 | 0.073 | -0.009 | 0.429 | -0.071 |
| 0.200 | 0.485 | 0.074 | -0.015 | 0.429 | -0.071 |
| 0.250 | 0.475 | 0.075 | -0.025 | 0.429 | -0.071 |
| 0.300 | 0.467 | 0.076 | -0.033 | 0.429 | -0.071 |
| 0.350 | 0.460 | 0.082 | -0.040 | 0.429 | -0.071 |
| 0.400 | 0.454 | 0.084 | -0.046 | 0.429 | -0.071 |
| 0.450 | 0.444 | 0.086 | -0.056 | 0.429 | -0.071 |
| 0.500 | 0.433 | 0.090 | -0.067 | 0.429 | -0.071 |

See `sensitivity_curve.png` for the figure.

## Interpretation

The intent-to-treat estimate is biased toward zero because non-adherent units carry no treatment effect — this is mechanical and is the reason the framework needs an adherence classifier at all. The per-protocol estimate approaches the true treatment effect θ when classifier error is zero and drifts toward the ITT estimate as classifier error increases, because the per-protocol subset becomes increasingly contaminated by non-adherers (false positives) and shrinks (false negatives).

**For the reviewer's purposes:** the V1 baseline classifier's misclassification rate sits in the low-bias region of this sweep, but the V1 dataset is internally calibrated and not a true error-rate estimate. The real classifier error rate, measured against held-out human-rated data with multiple raters, is the input this curve needs to make a quantitative claim about how much causal-estimate bias the platform actually carries.

## What this analysis intentionally simplifies

- Single binary treatment. The Medhavi platform has multiple policy contrasts.
- Symmetric classifier error. Real classifiers typically have asymmetric error rates.
- No covariate adjustment. A real analysis would use covariates to reduce variance.
- Static adherence. The paper §6 discusses time-varying treatments where adherence patterns evolve.
- No interrater disagreement model. The current sweep treats classifier error as a single quantity; a full model would propagate disagreement between human raters into classifier-error uncertainty.
