"""Synthetic trial generator for the classifier-error sensitivity analysis.

The reviewer's deeper concern about the adherence classifier is not just
"validate it" — it is "show how classifier error propagates into the causal
estimates the classifier gates." This module produces synthetic randomized
trial data with known ground truth so we can quantify that propagation.

Model:
    T  ~ Bernoulli(0.5)                       # randomized treatment
    A  ~ Bernoulli(adherence_rate)            # true LLM-policy adherence
    Y  = (true_effect * T if A else non_adherent_effect * T) + N(0, noise_sd)

The classifier observes A through a noisy channel parameterized by error_rate
(see ``inject_classifier_error``). Per-protocol analysis then filters on the
classifier's prediction A_hat, not on A.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class TrialData:
    T: np.ndarray  # binary treatment assignment
    A_true: np.ndarray  # binary true adherence
    Y: np.ndarray  # continuous outcome


def simulate_trial(
    n: int = 1000,
    true_effect: float = 0.5,
    adherence_rate: float = 0.85,
    non_adherent_effect: float = 0.0,
    noise_sd: float = 1.0,
    seed: int = 42,
) -> TrialData:
    """Generate one synthetic randomized trial.

    The treatment effect only manifests for observations where the LLM actually
    adhered to its assigned policy. This captures the structural assumption
    behind per-protocol analysis: the assigned treatment was not effectively
    delivered when adherence failed.
    """
    if not (0.0 <= adherence_rate <= 1.0):
        raise ValueError(f"adherence_rate must be in [0, 1]; got {adherence_rate}")
    if noise_sd < 0:
        raise ValueError(f"noise_sd must be non-negative; got {noise_sd}")

    rng = np.random.default_rng(seed)
    T = rng.binomial(1, 0.5, size=n)
    A_true = rng.binomial(1, adherence_rate, size=n)
    per_unit_effect = np.where(A_true == 1, true_effect, non_adherent_effect)
    Y = per_unit_effect * T + rng.normal(0.0, noise_sd, size=n)
    return TrialData(T=T, A_true=A_true, Y=Y)


def inject_classifier_error(
    A_true: np.ndarray,
    error_rate: float,
    seed: int = 0,
) -> np.ndarray:
    """Flip each true adherence label independently with probability ``error_rate``.

    This is a symmetric error model: false positive rate = false negative rate
    = error_rate. Asymmetric models are a natural extension but are out of
    scope for the V2 sensitivity sweep.
    """
    if not (0.0 <= error_rate <= 1.0):
        raise ValueError(f"error_rate must be in [0, 1]; got {error_rate}")
    rng = np.random.default_rng(seed)
    flips = rng.binomial(1, error_rate, size=len(A_true))
    return np.where(flips == 1, 1 - A_true, A_true).astype(A_true.dtype)
