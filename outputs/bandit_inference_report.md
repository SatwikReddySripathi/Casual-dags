# Bandit Inference Demos — V2 Module A1

## Purpose

Two phenomena flagged by the reviewer are demonstrated here on synthetic data so they are no longer hand-waves in the paper:

1. **Winner's curse / premature convergence on a false best arm** — the reviewer's specific Mode 2 worry. When K arms are i.i.d. with the same true mean and you select the empirical best one, the selected arm's observed mean is biased upward purely by selection.
2. **Adaptive collection bias correction** — the reviewer's note that the paper proposes bandit-based allocation and then retrospective causal analysis without engaging the bandit-inference literature. The IPW estimator (Horvitz-Thompson-style, using recorded propensities) is the correction; this report shows it works on data the simulator generates.

## Demo 1 — Winner's curse vs K

K arms, each with identical true mean μ = 0.5. For each simulation we draw n_per_arm Bernoulli outcomes per arm, pick the empirical-best arm, and record its observed mean. Averaged across simulations the difference between observed-winner-mean and true mean is the winner's-curse bias.

| K | n per arm | n sims | Observed winner mean | Bias vs μ=0.5 |
|---:|---:|---:|---:|---:|
| 2 | 50 | 3000 | 0.5383 | +0.0383 |
| 3 | 50 | 3000 | 0.5589 | +0.0589 |
| 4 | 50 | 3000 | 0.5720 | +0.0720 |
| 5 | 50 | 3000 | 0.5814 | +0.0814 |
| 7 | 50 | 3000 | 0.5946 | +0.0946 |
| 10 | 50 | 3000 | 0.6082 | +0.1082 |
| 15 | 50 | 3000 | 0.6216 | +0.1216 |
| 20 | 50 | 3000 | 0.6311 | +0.1311 |

See `bandit_winners_curse.png` for the curve.

**Interpretation.** Even with K = 2 there is positive selection bias; the
bias grows with K because the maximum of more i.i.d. estimates is further from
their common true value. This is the rigorous form of the reviewer's
'premature convergence on a false best arm' concern.

### Bootstrap-based correction on one run

Treat the observed sample as truth, resample within each arm with replacement, recompute the winner each bootstrap iteration, and the mean (winner_observed - winner_resample) approximates the upward selection bias. Subtract it from the observed winner mean to get the debiased estimate.

- Selected winner index: 2
- Winner observed mean: 0.6000
- Bootstrap-debiased estimate: 0.5316
- True mean of selected arm: 0.5000

## Demo 2 — IPW vs naive estimator under adaptive collection

A softmax bandit allocates batches with probability proportional to exp(temperature · observed_mean). Higher temperature concentrates on the apparent-best arm earlier. For each temperature we run many trials and compute the mean absolute error of naive sample-mean and IPW estimators against the true means.

| Temperature | Naive MAE | IPW MAE | Runs |
|---:|---:|---:|---:|
| 0.0 | 0.0372 | 0.0372 | 300 |
| 1.0 | 0.0376 | 0.0376 | 300 |
| 3.0 | 0.0387 | 0.0388 | 300 |
| 6.0 | 0.0421 | 0.0421 | 300 |
| 10.0 | 0.0524 | 0.0533 | 300 |
| 15.0 | 0.0649 | 0.0718 | 300 |

See `bandit_ipw_vs_naive.png` for the curve.

**Interpretation — honest reading of the numbers.**

For stationary Bernoulli arms, naive per-arm sample means are approximately unbiased even under adaptive allocation, because each arm's reward distribution does not change when the bandit chooses to sample it more or less often. IPW preserves this unbiasedness but pays a variance cost from up-weighting rounds where the chosen arm had low propensity. In the simple Bernoulli setting the variance cost can match or exceed the bias gain — which is why IPW's MAE in the table above sits at or slightly above naive's.

Where IPW (and the broader bandit-inference literature) genuinely matters:

- **Winner-selection bias** — Demo 1 above is the live case. Reporting the empirical-best arm's observed mean overstates that arm's true performance. The bootstrap or IPW-style debiasing is what produces the honest number.
- **Contextual settings** — when the allocator depends on student covariates that also affect reward, naive sample means are biased and IPW (or g-computation) restores unbiasedness. This is the setting Medhavi will actually deploy in.
- **Non-stationary arms** — when arm reward distributions drift, the rounds an arm was chosen on are correlated with that arm's reward at that time. Naive averaging mixes regimes; IPW with the right weighting separates them.
- **Confidence intervals** — naive intervals on bandit-collected data are anti-conservative; the bandit-inference literature provides corrected CIs via sandwich variance or martingale bounds.

The takeaway for the Medhavi paper is twofold: (1) when reporting 'the best policy works at level X', use Demo 1's debiasing; (2) when running retrospective causal analysis on bandit-collected data with covariates, the per-round propensities must be logged so IPW (or a doubly-robust variant) can correct the resulting biases.

## What is intentionally simplified

- Bernoulli arms only. Real-world rewards are richer (continuous GLP scores).
- Softmax allocator with known propensities. Real Thompson sampling needs Monte Carlo for exact propensities; the simplification keeps IPW well-defined.
- No context features. Contextual bandits would use IPW conditioned on student covariates.
- Stationary arms. The platform's true means may drift with content updates.

## Next within Phase A

- A2: G-methods feasibility demo (time-varying treatments).
- A3: Multiple-comparisons correction demo.
- A4: Differential-attrition monitor.
- A5: Early-stopping safeguard for bandits (integrates with this module's simulator).
