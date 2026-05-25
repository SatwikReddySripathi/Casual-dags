"""Tests for the V2 Module A1 bandit-inference simulators and estimators."""

import numpy as np
import pytest

from src.bandit.inference import (
    bootstrap_winner_debiased,
    ipw_arm_means,
    naive_arm_means,
    winner_observed_mean,
)
from src.bandit.simulate import (
    run_softmax_bandit,
    simulate_winners_curse,
)


def test_winners_curse_runs_with_defaults():
    run = simulate_winners_curse(K=3, n_per_arm=20, n_sims=50, seed=1)
    assert run.observed_means.shape == (50, 3)
    assert run.winners.shape == (50,)
    assert run.winner_observed.shape == (50,)


def test_winners_curse_rejects_K_one():
    with pytest.raises(ValueError):
        simulate_winners_curse(K=1)


def test_winners_curse_bias_is_positive_on_average():
    # With K identical arms, mean of winner_observed should exceed true mean.
    run = simulate_winners_curse(K=10, n_per_arm=30, n_sims=2000, seed=0)
    assert run.winner_observed.mean() > 0.5


def test_softmax_bandit_logs_match_lengths():
    log = run_softmax_bandit(
        true_means=np.array([0.3, 0.5, 0.7]),
        n_batches=4,
        batch_size=10,
        temperature=2.0,
        seed=5,
    )
    T = 4 * 10
    assert log.arms.shape == (T,)
    assert log.rewards.shape == (T,)
    assert log.propensities.shape == (T,)
    assert ((log.arms >= 0) & (log.arms < 3)).all()
    assert ((log.rewards == 0) | (log.rewards == 1)).all()
    assert ((log.propensities > 0) & (log.propensities <= 1)).all()


def test_softmax_bandit_concentrates_on_better_arm():
    # Best arm has highest true mean; with high temperature and many batches it
    # should be chosen most often.
    log = run_softmax_bandit(
        true_means=np.array([0.2, 0.8]),
        n_batches=20,
        batch_size=30,
        temperature=10.0,
        seed=11,
    )
    counts = np.bincount(log.arms, minlength=2)
    assert counts[1] > counts[0]


def test_naive_arm_means_basic():
    arms = np.array([0, 0, 1, 1, 2])
    rewards = np.array([1, 0, 1, 1, 0])
    means = naive_arm_means(arms, rewards, K=3)
    assert means[0] == pytest.approx(0.5)
    assert means[1] == pytest.approx(1.0)
    assert means[2] == pytest.approx(0.0)


def test_ipw_arm_means_matches_naive_when_propensities_uniform():
    arms = np.array([0, 0, 1, 1])
    rewards = np.array([1, 0, 1, 0])
    propensities = np.array([0.5, 0.5, 0.5, 0.5])
    ipw = ipw_arm_means(arms, rewards, propensities, K=2)
    naive = naive_arm_means(arms, rewards, K=2)
    assert np.allclose(ipw, naive)


def test_ipw_is_approximately_unbiased_under_adaptive_collection():
    """IPW's whole point: averaged across many runs, per-arm estimates should
    track true means even when allocation is highly adaptive.

    Note: naive sample means of stationary i.i.d. Bernoulli arms are *also*
    unbiased under most adaptive allocation rules — the rounds an arm is
    selected on do not change that arm's Bernoulli reward distribution. So
    this test is about IPW's unbiasedness, not IPW being strictly better than
    naive on MAE. Where IPW genuinely helps is winner-selection bias (Demo 1)
    and contextual or non-stationary settings.
    """
    rng_seeds = range(80)
    true_means = np.array([0.4, 0.5, 0.6])
    ipw_estimates = np.zeros((len(list(rng_seeds)), 3))
    for i, s in enumerate(range(80)):
        log = run_softmax_bandit(
            true_means=true_means,
            n_batches=12,
            batch_size=30,
            temperature=8.0,
            seed=s,
        )
        ipw_estimates[i] = ipw_arm_means(log.arms, log.rewards, log.propensities, K=3)
    mean_estimates = np.nanmean(ipw_estimates, axis=0)
    # Across 80 runs the mean IPW estimate per arm should be within 0.05 of truth.
    assert np.all(np.abs(mean_estimates - true_means) < 0.05), (
        f"IPW means deviated from truth: {mean_estimates} vs {true_means}"
    )


def test_ipw_mae_within_reasonable_bound_of_naive():
    """IPW costs variance from up-weighting rare arms. Sanity check: not
    catastrophically worse than naive on average across runs.
    """
    rng_seeds = range(40)
    naive_errs = []
    ipw_errs = []
    true_means = np.array([0.4, 0.5, 0.6])
    for s in rng_seeds:
        log = run_softmax_bandit(
            true_means=true_means,
            n_batches=12,
            batch_size=30,
            temperature=8.0,
            seed=s,
        )
        naive = naive_arm_means(log.arms, log.rewards, K=3)
        ipw = ipw_arm_means(log.arms, log.rewards, log.propensities, K=3)
        naive_errs.append(float(np.nanmean(np.abs(naive - true_means))))
        ipw_errs.append(float(np.nanmean(np.abs(ipw - true_means))))
    assert np.mean(ipw_errs) <= 2.0 * np.mean(naive_errs)


def test_winner_observed_mean_picks_argmax():
    arms = np.array([0, 0, 1, 1, 2, 2])
    rewards = np.array([1, 1, 0, 1, 0, 0])
    winner, value = winner_observed_mean(arms, rewards, K=3)
    assert winner == 0
    assert value == pytest.approx(1.0)


def test_bootstrap_winner_debias_reduces_observed_winner():
    rng = np.random.default_rng(3)
    K = 6
    n_per_arm = 40
    arms_list = []
    rewards_list = []
    for k in range(K):
        arms_list.append(np.full(n_per_arm, k))
        rewards_list.append(rng.binomial(1, 0.5, size=n_per_arm))
    arms = np.concatenate(arms_list)
    rewards = np.concatenate(rewards_list)
    winner, observed = winner_observed_mean(arms, rewards, K=K)
    debiased_winner, debiased_value = bootstrap_winner_debiased(
        arms=arms, rewards=rewards, K=K, n_bootstrap=400, seed=9
    )
    assert debiased_winner == winner
    # Debiased value should be no larger than the observed winner mean (and
    # typically strictly smaller; allow exact equality only in degenerate runs).
    assert debiased_value <= observed + 1e-9
