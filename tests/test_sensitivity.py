"""Tests for the classifier-error sensitivity simulation."""

import numpy as np
import pytest

from src.sensitivity.run_analysis import (
    itt_estimate,
    per_protocol_estimate,
    run_sweep,
)
from src.sensitivity.simulate import inject_classifier_error, simulate_trial


def test_simulate_trial_shapes_and_ranges():
    data = simulate_trial(n=500, seed=1)
    assert data.T.shape == (500,)
    assert data.A_true.shape == (500,)
    assert data.Y.shape == (500,)
    assert set(np.unique(data.T)).issubset({0, 1})
    assert set(np.unique(data.A_true)).issubset({0, 1})


def test_simulate_trial_rejects_invalid_adherence_rate():
    with pytest.raises(ValueError):
        simulate_trial(adherence_rate=1.5)


def test_simulate_trial_is_seed_reproducible():
    a = simulate_trial(n=200, seed=7)
    b = simulate_trial(n=200, seed=7)
    assert np.array_equal(a.T, b.T)
    assert np.array_equal(a.A_true, b.A_true)
    assert np.allclose(a.Y, b.Y)


def test_inject_classifier_error_zero_returns_original():
    A = np.array([0, 1, 0, 1, 1, 0])
    out = inject_classifier_error(A, error_rate=0.0, seed=42)
    assert np.array_equal(out, A)


def test_inject_classifier_error_one_flips_all():
    A = np.array([0, 1, 0, 1, 1, 0])
    out = inject_classifier_error(A, error_rate=1.0, seed=42)
    assert np.array_equal(out, 1 - A)


def test_inject_classifier_error_half_disagrees_roughly_half():
    A = np.zeros(2000, dtype=int)
    out = inject_classifier_error(A, error_rate=0.5, seed=0)
    disagreement = float(np.mean(out != A))
    assert 0.45 < disagreement < 0.55


def test_per_protocol_recovers_true_effect_when_classifier_is_perfect():
    data = simulate_trial(n=2000, true_effect=0.6, adherence_rate=0.9, seed=3)
    est = per_protocol_estimate(data.T, data.A_true, data.Y)
    assert abs(est - 0.6) < 0.15


def test_itt_attenuates_when_adherence_below_one():
    data = simulate_trial(n=5000, true_effect=1.0, adherence_rate=0.5, seed=11)
    itt = itt_estimate(data.T, data.Y)
    # ITT averages effect across adherers and non-adherers, so should be near
    # adherence_rate * true_effect = 0.5 (well below 1.0).
    assert itt < 0.7


def test_run_sweep_produces_expected_columns_and_increasing_bias():
    df = run_sweep(
        true_effect=0.5,
        error_rates=np.array([0.0, 0.2, 0.4]),
        n_per_trial=600,
        n_runs=30,
    )
    expected = {"classifier_error_rate", "pp_mean", "pp_sd", "pp_bias", "itt_mean", "itt_bias"}
    assert expected.issubset(set(df.columns))
    # Bias magnitude should grow as classifier error increases.
    assert abs(df.iloc[2]["pp_bias"]) > abs(df.iloc[0]["pp_bias"])
