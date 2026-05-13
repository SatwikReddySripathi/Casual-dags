"""Transparent rule-based baseline classifier for pedagogical adherence.

This is a V1 baseline only. It exists so we can establish a measurable error
rate against the manual labels, not to act as a final classifier.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Allow running this file directly: python src/adherence/rule_based_classifier.py
_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
if str(_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_ROOT))

from src.adherence.rubric import (
    DIRECT_ANSWER_PATTERNS,
    EXAMPLE_LANGUAGE_PATTERNS,
    POLICY_TYPES,
    REFUSAL_PATTERNS,
)


def _extract_flags(tutor_response: str) -> dict:
    text = (tutor_response or "").lower().strip()

    contains_direct_answer_pattern = any(p in text for p in DIRECT_ANSWER_PATTERNS)
    contains_refusal = any(p in text for p in REFUSAL_PATTERNS)
    contains_example_language = any(p in text for p in EXAMPLE_LANGUAGE_PATTERNS)

    question_count = text.count("?")
    asks_question = question_count >= 1

    # Estimate sentence count from terminal punctuation. Always at least 1 if any
    # text exists so divisions later do not blow up.
    sentence_marks = re.findall(r"[.!?]+", text)
    sentence_count = max(1, len(sentence_marks)) if text else 0

    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)

    return {
        "contains_direct_answer_pattern": contains_direct_answer_pattern,
        "contains_refusal": contains_refusal,
        "contains_example_language": contains_example_language,
        "asks_question": asks_question,
        "question_count": question_count,
        "sentence_count": sentence_count,
        "word_count": word_count,
    }


def _classify_partial_hint(flags: dict) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if flags["contains_direct_answer_pattern"]:
        reasons.append("Direct answer language detected under partial_hint policy.")
        return "NON_ADHERENT", reasons
    if flags["word_count"] > 60:
        reasons.append("Long response (>60 words) suggests near-solution under partial_hint.")
        return "PARTIAL", reasons
    reasons.append("Short hint without direct answer language.")
    return "ADHERENT", reasons


def _classify_scaffolded_question(flags: dict) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if not flags["asks_question"] and flags["contains_direct_answer_pattern"]:
        reasons.append("No guiding question and direct answer language present.")
        return "NON_ADHERENT", reasons
    if flags["asks_question"] and flags["word_count"] <= 45:
        reasons.append("Asks a focused question and stays concise.")
        return "ADHERENT", reasons
    if flags["asks_question"] and flags["word_count"] > 45:
        reasons.append("Asks a question but adds substantial extra explanation.")
        return "PARTIAL", reasons
    reasons.append("Neither a clear question nor an obvious final answer.")
    return "PARTIAL", reasons


def _classify_immediate_reveal(flags: dict) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if flags["contains_refusal"]:
        reasons.append("Refusal detected even though direct answers are allowed.")
        return "NON_ADHERENT", reasons
    if flags["word_count"] < 5:
        reasons.append("Response too short to be a useful answer.")
        return "PARTIAL", reasons
    reasons.append("Direct answer with reasonable length.")
    return "ADHERENT", reasons


def _classify_socratic_only(flags: dict) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if flags["contains_direct_answer_pattern"]:
        reasons.append("Direct answer language under socratic_only policy.")
        return "NON_ADHERENT", reasons
    if flags["question_count"] >= 1 and flags["question_count"] >= flags["sentence_count"] / 2:
        reasons.append("Majority of sentences are questions.")
        return "ADHERENT", reasons
    if flags["question_count"] >= 1:
        reasons.append("Has at least one question but is mostly direct explanation.")
        return "PARTIAL", reasons
    reasons.append("No questions present under socratic_only policy.")
    return "NON_ADHERENT", reasons


def _classify_worked_example(flags: dict) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if flags["contains_example_language"]:
        reasons.append("Contains example/step language consistent with a worked example.")
        return "ADHERENT", reasons
    if flags["contains_direct_answer_pattern"]:
        reasons.append("Final answer provided without a worked example.")
        return "NON_ADHERENT", reasons
    reasons.append("No worked example language and no direct final answer; ambiguous.")
    return "PARTIAL", reasons


_DISPATCH = {
    "partial_hint": _classify_partial_hint,
    "scaffolded_question": _classify_scaffolded_question,
    "immediate_reveal": _classify_immediate_reveal,
    "socratic_only": _classify_socratic_only,
    "worked_example": _classify_worked_example,
}


def classify_response(
    policy_type: str,
    tutor_response: str,
    student_prompt: str = "",
) -> dict:
    """Classify a single tutor response against a pedagogical policy.

    Returns a dict with predicted_label, human-readable reasons, and the
    underlying flags used for the decision (useful for error analysis).
    """
    if policy_type not in POLICY_TYPES:
        raise ValueError(
            f"Unknown policy_type {policy_type!r}. Expected one of {POLICY_TYPES}."
        )

    flags = _extract_flags(tutor_response)
    predicted_label, reasons = _DISPATCH[policy_type](flags)

    if not reasons:
        reasons = ["No specific signals detected; defaulted to PARTIAL."]

    return {
        "predicted_label": predicted_label,
        "reasons": reasons,
        "flags": flags,
    }


if __name__ == "__main__":
    demo = classify_response(
        "partial_hint",
        "Try subtracting 4 from both sides first. What do you get?",
    )
    print(demo)
