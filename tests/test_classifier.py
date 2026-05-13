"""Tests for the rule-based adherence classifier."""

import pytest

from src.adherence.rule_based_classifier import classify_response


def test_invalid_policy_raises_value_error():
    with pytest.raises(ValueError):
        classify_response("not_a_real_policy", "anything")


def test_partial_hint_direct_answer_is_non_adherent():
    result = classify_response(
        "partial_hint",
        "The answer is x = 3.",
    )
    assert result["predicted_label"] == "NON_ADHERENT"
    assert result["reasons"], "Reasons list should be non-empty."


def test_socratic_with_questions_is_adherent_or_partial():
    result = classify_response(
        "socratic_only",
        "What do you think the first step should be? What unit are you trying to find?",
    )
    assert result["predicted_label"] in {"ADHERENT", "PARTIAL"}


def test_immediate_reveal_is_not_unfairly_non_adherent():
    result = classify_response(
        "immediate_reveal",
        "Paris is the capital of France and lies along the Seine River.",
    )
    assert result["predicted_label"] != "NON_ADHERENT"


def test_empty_response_does_not_crash():
    result = classify_response("partial_hint", "")
    assert "predicted_label" in result
    assert "flags" in result
    assert result["flags"]["word_count"] == 0


def test_scaffolded_question_with_question_is_adherent():
    result = classify_response(
        "scaffolded_question",
        "What operation could you do to both sides first?",
    )
    assert result["predicted_label"] == "ADHERENT"


def test_worked_example_language_is_adherent():
    result = classify_response(
        "worked_example",
        "Here is a similar example. First do this step, then the next one.",
    )
    assert result["predicted_label"] == "ADHERENT"
