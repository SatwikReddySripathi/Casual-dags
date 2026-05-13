# Medhavi Pedagogical Adherence Rubric — V1

## Purpose

This rubric defines whether a generated tutor response followed the assigned pedagogical policy.

Policy names use the vocabulary of the Medhavi framework paper (`Casual KG Medhavi.pdf`, §3.1 and §7), which names specific pedagogical contrasts the platform deploys: full-vs-partial hints, immediate-vs-delayed answer reveal, specific-vs-generic corrective feedback, and "do not provide the answer; only identify the error location."

## Label Set

### ADHERENT

The tutor response follows the assigned policy and does not violate key constraints.

### PARTIAL

The tutor response mostly follows the policy but gives too much help, is slightly too direct, or mixes policy styles.

### NON_ADHERENT

The tutor response violates the assigned policy in a clear way, such as revealing the final answer when only a hint was allowed.

## Supported Policy Types

| Policy | Paper contrast (Casual KG Medhavi.pdf) |
|---|---|
| `partial_hint` | "full vs partial hints" (§3.1, §7) |
| `scaffolded_question` | generalization of "do not provide the answer; only identify the error location" (§7) |
| `immediate_reveal` | "immediate vs delayed answer reveal" (§3.1) |
| `socratic_only` | Socratic questioning (adjacent to paper's "withhold answer" framing) |
| `worked_example` | worked examples (§1.1; Hattie inventory) |

## Policy-Specific Rules

### partial_hint

The tutor should give a clue, next step, or conceptual hint without revealing the final answer.

ADHERENT:
- Gives one useful hint.
- Does not reveal the answer.
- Leaves meaningful work for the student.

PARTIAL:
- Gives a very strong hint.
- Almost solves the problem.
- Still leaves a small step for the student.

NON_ADHERENT:
- Gives the final answer.
- Shows the complete solution.
- Uses language like "the answer is" or "so x = ..."

### scaffolded_question

The tutor should guide using one small next-step question.

ADHERENT:
- Asks one focused next-step question.
- Avoids solving the whole problem.

PARTIAL:
- Asks a question but adds too much explanation.

NON_ADHERENT:
- Gives the answer without asking a guiding question.

### immediate_reveal

The tutor is allowed to answer directly and immediately, but should still be useful.

ADHERENT:
- Gives the answer with a short explanation.

PARTIAL:
- Gives the answer with weak or incomplete explanation.

NON_ADHERENT:
- Refuses unnecessarily.
- Gives unrelated or incorrect content.

### socratic_only

The tutor should use guiding questions and avoid direct instruction.

ADHERENT:
- Mostly or entirely asks questions.
- Encourages the student to reason.

PARTIAL:
- Mostly Socratic but includes some direct explanation.

NON_ADHERENT:
- Directly explains the answer.
- Gives the final solution.

### worked_example

The tutor may give a worked example.

ADHERENT:
- Gives a similar worked example.
- Explains the steps.
- Connects the example to the student task.

PARTIAL:
- Gives an example but connection is weak.

NON_ADHERENT:
- Only gives the final answer.
- Does not provide a useful example.
