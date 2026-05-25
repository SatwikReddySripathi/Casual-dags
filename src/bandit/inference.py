"""Estimators for arm means from bandit-collected data.

Two estimators are implemented:

- ``naive_arm_means``: simple sample mean of rewards per arm. Unbiased for
  per-arm mean reward in the strict mathematical sense for a stationary
  Bernoulli arm, but does not address selection-based bias when the *winner*
  is reported.

- ``ipw_arm_means``: inverse-propensity-weighted mean. Re-weights each
  observation by 1 / P(this arm was chosen at this round | history). When the
  propensities are exact (as in ``run_softmax_bandit``), this restores
  unbiasedness for the marginal arm mean even under heavy adaptive allocation.

A simple bootstrap-style debiasing for the winner's-curse setting is also
provided.
"""

from __future__ import annotations

import numpy as np


def naive_arm_means(arms: np.ndarray, rewards: np.ndarray, K: int) -> np.ndarray:
    out = np.full(K, np.nan)
    for k in range(K):
        mask = arms == k
        if mask.sum() > 0:
            out[k] = rewards[mask].mean()
    return out


def ipw_arm_means(
    arms: np.ndarray,
    rewards: np.ndarray,
    propensities: np.ndarray,
    K: int,
) -> np.ndarray:
    """Horvitz-Thompson-style estimator using exact recorded propensities."""
    if not (arms.shape == rewards.shape == propensities.shape):
        raise ValueError("arms, rewards, and propensities must have matching shapes")
    out = np.full(K, np.nan)
    n_total = len(arms)
    for k in range(K):
        mask = arms == k
        if mask.sum() == 0:
            continue
        # Weight = 1 / propensity; sum across all rounds where arm k was chosen.
        weights = 1.0 / propensities[mask]
        # Hajek-style normalization: divide by sum of weights rather than n_total.
        # More stable than the raw Horvitz-Thompson sum / n_total for small samples.
        out[k] = (weights * rewards[mask]).sum() / weights.sum()
    return out


def winner_observed_mean(
    arms: np.ndarray,
    rewards: np.ndarray,
    K: int,
) -> tuple[int, float]:
    """Return (winner_index, winner_naive_mean) where winner = empirical-best arm."""
    means = naive_arm_means(arms, rewards, K)
    winner = int(np.nanargmax(means))
    return winner, float(means[winner])


def bootstrap_winner_debiased(
    arms: np.ndarray,
    rewards: np.ndarray,
    K: int,
    n_bootstrap: int = 500,
    seed: int = 0,
) -> tuple[int, float]:
    """Debias the winner's observed mean by the average winner-vs-true gap on
    resampled data, where we treat the observed sample as the truth.

    This is the simplest form of bootstrap selection-bias correction: estimate
    the upward bias of "max of K means" by bootstrap and subtract it from the
    observed winner. It will not fully correct in the limit but it is the
    standard demo of the principle.
    """
    rng = np.random.default_rng(seed)
    means = naive_arm_means(arms, rewards, K)
    selected_winner = int(np.nanargmax(means))

    # Treat observed sample as truth; resample with replacement per arm.
    biases = np.empty(n_bootstrap)
    for b in range(n_bootstrap):
        boot_means = np.empty(K)
        for k in range(K):
            mask = arms == k
            if mask.sum() == 0:
                boot_means[k] = np.nan
                continue
            arm_rewards = rewards[mask]
            resample = rng.choice(arm_rewards, size=len(arm_rewards), replace=True)
            boot_means[k] = resample.mean()
        boot_winner = int(np.nanargmax(boot_means))
        biases[b] = boot_means[boot_winner] - means[boot_winner]

    estimated_bias = float(np.mean(biases))
    return selected_winner, float(means[selected_winner] - estimated_bias)
