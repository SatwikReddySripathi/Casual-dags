"""Rubric constants and validation helpers for Medhavi adherence classification.

Policy names follow the vocabulary the Medhavi framework paper uses for its
named pedagogical contrasts (Casual KG Medhavi.pdf §3.1, §7):

    partial_hint            — paper's "partial hints" side of full-vs-partial
    scaffolded_question     — generalization of paper's "only identify the
                              error location" framing (a single guiding question)
    immediate_reveal        — paper's "immediate answer reveal" side of
                              immediate-vs-delayed reveal
    socratic_only           — Socratic questioning (not in paper but adjacent)
    worked_example          — paper §1.1 (worked examples in Hattie's list)
"""

LABELS = ["ADHERENT", "PARTIAL", "NON_ADHERENT"]

POLICY_TYPES = [
    "partial_hint",
    "scaffolded_question",
    "immediate_reveal",
    "socratic_only",
    "worked_example",
]

POLICY_PAPER_CONTRAST = {
    "partial_hint": "full vs partial hints (paper §3.1, §7)",
    "scaffolded_question": "do not provide the answer; only identify the error location (paper §7)",
    "immediate_reveal": "immediate vs delayed answer reveal (paper §3.1)",
    "socratic_only": "Socratic questioning (adjacent to paper §7 'withhold answer')",
    "worked_example": "worked examples (paper §1.1; Hattie inventory)",
}

DIRECT_ANSWER_PATTERNS = [
    "the answer is",
    "final answer",
    "so x =",
    "therefore x",
    "equals",
    "the correct answer is",
    "you should write",
]

REFUSAL_PATTERNS = [
    "i can't help",
    "i cannot help",
    "i won't",
    "not allowed",
]

EXAMPLE_LANGUAGE_PATTERNS = [
    "example",
    "similar",
    "step",
    "first",
    "next",
]


def validate_label(label: str) -> bool:
    return label in LABELS


def validate_policy_type(policy_type: str) -> bool:
    return policy_type in POLICY_TYPES
