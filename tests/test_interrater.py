"""Tests for the Cohen's kappa interrater module."""

import pytest

from src.adherence.interrater import cohen_kappa, kappa_interpretation
from src.adherence.rubric import LABELS


def test_kappa_perfect_agreement_is_one():
    a = ["ADHERENT", "PARTIAL", "NON_ADHERENT", "ADHERENT"]
    assert cohen_kappa(a, list(a), LABELS) == pytest.approx(1.0)


def test_kappa_total_disagreement_is_negative():
    a = ["ADHERENT", "ADHERENT", "ADHERENT", "ADHERENT"]
    b = ["NON_ADHERENT", "NON_ADHERENT", "NON_ADHERENT", "NON_ADHERENT"]
    # Marginals are degenerate; both raters use one category each. Expected
    # agreement matches observed in this construction.
    assert cohen_kappa(a, b, LABELS) <= 0.0


def test_kappa_chance_level_near_zero():
    # Construct so that observed agreement ~= chance agreement.
    a = ["ADHERENT"] * 50 + ["NON_ADHERENT"] * 50
    b = ["ADHERENT"] * 25 + ["NON_ADHERENT"] * 25 + ["ADHERENT"] * 25 + ["NON_ADHERENT"] * 25
    k = cohen_kappa(a, b, LABELS)
    assert -0.1 < k < 0.1


def test_kappa_length_mismatch_raises():
    with pytest.raises(ValueError):
        cohen_kappa(["ADHERENT"], ["ADHERENT", "PARTIAL"], LABELS)


def test_kappa_unknown_label_raises():
    with pytest.raises(ValueError):
        cohen_kappa(["WAT"], ["ADHERENT"], LABELS)


def test_kappa_interpretation_buckets():
    assert "slight" in kappa_interpretation(0.1)
    assert "fair" in kappa_interpretation(0.3)
    assert "moderate" in kappa_interpretation(0.5)
    assert "substantial" in kappa_interpretation(0.7)
    assert "almost perfect" in kappa_interpretation(0.9)
    assert "worse than chance" in kappa_interpretation(-0.1)
