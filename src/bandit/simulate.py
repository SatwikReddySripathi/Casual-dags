"""Bandit allocation simulators for the V2 inference-bias demos.

Two phenomena are modeled here, both flagged by the reviewer:

1. **Winner's curse.** Pick the empirical-best arm out of K i.i.d. Bernoulli arms
   with identical true means. The selected arm's observed mean is biased upward
   purely because of selection: we conditioned on being above all the others.
   This is the reviewer's "premature convergence on a false best arm" worry,
   reduced to its simplest form.

2. **Adaptive collection bias.** Run a softmax bandit that re-allocates each
   batch in proportion to currently-observed arm means. Because allocation
   probabilities depend on the random outcomes already observed, the per-arm
   sample mean computed naively over an arm's selected rounds is no longer a
   straightforward i.i.d. average; this is what the bandit-inference literature
   (Dimakopoulou et al., Nie et al., Zhang et al.) addresses with inverse-
   propensity-weighted estimators. ``run_softmax_bandit`` records exact
   propensities per round so that IPW correction is exact, not approximate.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# ----------------------------------------------------------------------------
# Winner's curse
# ----------------------------------------------------------------------------


@dataclass
class WinnersCurseRun:
    """Per-simulation winner's-curse outcomes (one row per simulation)."""

    observed_means: np.ndarray  # shape (n_sims, K)
    winners: np.ndarray  # shape (n_sims,), index of selected best arm
    winner_observed: np.ndarray  # shape (n_sims,), winner's observed mean
    winner_true: np.ndarray  # shape (n_sims,), winner's true mean


def simulate_winners_curse(
    K: int = 5,
    n_per_arm: int = 50,
    n_sims: int = 2000,
    true_means: np.ndarray | None = None,
    seed: int = 0,
) -> WinnersCurseRun:
    """Repeatedly: draw n_per_arm Bernoulli outcomes per arm, pick best, record.

    With all true means equal, any positive winner-observed-minus-winner-true
    is pure selection bias.
    """
    if K < 2:
        raise ValueError(f"K must be >= 2; got {K}")
    if n_per_arm < 1:
        raise ValueError(f"n_per_arm must be >= 1; got {n_per_arm}")

    rng = np.random.default_rng(seed)
    if true_means is None:
        true_means = np.full(K, 0.5)
    true_means = np.asarray(true_means, dtype=float)
    if true_means.shape != (K,):
        raise ValueError(f"true_means shape must be ({K},); got {true_means.shape}")

    obs = np.empty((n_sims, K), dtype=float)
    for k in range(K):
        draws = rng.binomial(1, true_means[k], size=(n_sims, n_per_arm))
        obs[:, k] = draws.mean(axis=1)

    winners = obs.argmax(axis=1)
    winner_obs = obs[np.arange(n_sims), winners]
    winner_true = true_means[winners]
    return WinnersCurseRun(
        observed_means=obs,
        winners=winners,
        winner_observed=winner_obs,
        winner_true=winner_true,
    )


# ----------------------------------------------------------------------------
# Softmax bandit with exact, recorded propensities
# ----------------------------------------------------------------------------


@dataclass
class BanditLog:
    """Per-round bandit log with exact propensities so IPW is well-defined."""

    arms: np.ndarray  # shape (T,)
    rewards: np.ndarray  # shape (T,)
    propensities: np.ndarray  # shape (T,) — P(chosen arm | history at that round)
    true_means: np.ndarray  # shape (K,)


def run_softmax_bandit(
    true_means: np.ndarray,
    n_batches: int = 10,
    batch_size: int = 30,
    temperature: float = 5.0,
    seed: int = 0,
    min_propensity: float = 0.01,
) -> BanditLog:
    """Batched softmax allocator over K Bernoulli arms.

    Round 0 is uniform allocation. Each subsequent round computes a softmax
    over the current observed arm means using a temperature parameter, then
    samples a batch with replacement from that distribution. Propensities for
    the chosen arms are recorded exactly. ``min_propensity`` is a floor that
    prevents IPW weights from blowing up on essentially-never-chosen arms.
    """
    true_means = np.asarray(true_means, dtype=float)
    K = len(true_means)
    if K < 2:
        raise ValueError(f"need at least 2 arms; got {K}")
    if not (0.0 < min_propensity <= 1.0 / K):
        raise ValueError("min_propensity must be in (0, 1/K]")

    rng = np.random.default_rng(seed)

    arms_acc: list[np.ndarray] = []
    rewards_acc: list[np.ndarray] = []
    propensities_acc: list[np.ndarray] = []

    # Round 0: uniform allocation, propensity = 1/K everywhere.
    uniform_probs = np.full(K, 1.0 / K)
    arms_0 = rng.choice(K, size=batch_size, p=uniform_probs)
    rewards_0 = rng.binomial(1, true_means[arms_0])
    prop_0 = uniform_probs[arms_0]
    arms_acc.append(arms_0)
    rewards_acc.append(rewards_0)
    propensities_acc.append(prop_0)

    for _ in range(1, n_batches):
        flat_arms = np.concatenate(arms_acc)
        flat_rewards = np.concatenate(rewards_acc)

        observed = np.empty(K)
        for k in range(K):
            mask = flat_arms == k
            observed[k] = flat_rewards[mask].mean() if mask.sum() > 0 else 0.5

        # Softmax with floor.
        logits = temperature * (observed - observed.max())  # stability
        probs = np.exp(logits)
        probs = probs / probs.sum()
        probs = np.maximum(probs, min_propensity)
        probs = probs / probs.sum()

        arms = rng.choice(K, size=batch_size, p=probs)
        rewards = rng.binomial(1, true_means[arms])
        propensities = probs[arms]
        arms_acc.append(arms)
        rewards_acc.append(rewards)
        propensities_acc.append(propensities)

    return BanditLog(
        arms=np.concatenate(arms_acc),
        rewards=np.concatenate(rewards_acc),
        propensities=np.concatenate(propensities_acc),
        true_means=true_means,
    )
