"""Interrater reliability (Cohen's kappa) for the adherence labels.

This script is the V2-readiness scaffold for the most important V1→V2 ask:
adding a second human annotator. The script accepts two label files and reports
Cohen's kappa overall and per-policy. If the second-rater file does not yet
exist it prints the exact workflow to enable kappa computation.

Run from project root:

    python src/adherence/interrater.py

Optional environment overrides:

    MEDHAVI_RATER2_PATH=data/manual_labels_rater2.csv python src/adherence/interrater.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.adherence.rubric import LABELS

DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

PROMPTS_PATH = DATA_DIR / "sample_prompts.csv"
RATER1_PATH = DATA_DIR / "manual_labels.csv"
RATER2_PATH = Path(os.environ.get("MEDHAVI_RATER2_PATH", str(DATA_DIR / "manual_labels_rater2.csv")))
REPORT_PATH = OUTPUT_DIR / "interrater_report.md"


def cohen_kappa(labels_a: list[str], labels_b: list[str], categories: list[str]) -> float:
    """Cohen's kappa between two label sequences over a fixed category set.

    Returns 1.0 for perfect agreement, 0.0 for chance-level agreement, and
    negative values for worse-than-chance. Implementation is intentionally
    minimal so we do not pull in additional dependencies for one number.
    """
    if len(labels_a) != len(labels_b):
        raise ValueError(
            f"label sequences must match in length; got {len(labels_a)} vs {len(labels_b)}"
        )
    if not labels_a:
        raise ValueError("label sequences must be non-empty")

    n = len(labels_a)
    idx = {c: i for i, c in enumerate(categories)}
    k = len(categories)
    cm = np.zeros((k, k), dtype=float)
    for a, b in zip(labels_a, labels_b):
        if a not in idx or b not in idx:
            raise ValueError(f"label {a!r} or {b!r} not in categories {categories}")
        cm[idx[a]][idx[b]] += 1

    p_o = np.trace(cm) / n
    row_marg = cm.sum(axis=1) / n
    col_marg = cm.sum(axis=0) / n
    p_e = float((row_marg * col_marg).sum())
    if p_e == 1.0:
        # Degenerate: both raters used only one category; kappa undefined but
        # report 1.0 if they agreed perfectly, else 0.0.
        return 1.0 if p_o == 1.0 else 0.0
    return float((p_o - p_e) / (1 - p_e))


def kappa_interpretation(kappa: float) -> str:
    if kappa < 0:
        return "worse than chance"
    if kappa < 0.20:
        return "slight (Landis & Koch)"
    if kappa < 0.40:
        return "fair (Landis & Koch)"
    if kappa < 0.60:
        return "moderate (Landis & Koch)"
    if kappa < 0.80:
        return "substantial (Landis & Koch)"
    return "almost perfect (Landis & Koch)"


def _print_rater2_workflow() -> None:
    print(
        "Second-rater file not found at:\n"
        f"  {RATER2_PATH}\n\n"
        "Workflow to enable Cohen's kappa:\n"
        "  1. Share docs/adherence_rubric.md with the second annotator.\n"
        "  2. Share data/sample_prompts.csv (NOT data/manual_labels.csv — the\n"
        "     second rater must be blind to the first rater's labels).\n"
        "  3. Ask the second rater to produce a file with the same schema as\n"
        "     data/manual_labels.csv (columns: id, human_label, human_reason).\n"
        "  4. Save it as data/manual_labels_rater2.csv (or point\n"
        "     MEDHAVI_RATER2_PATH at any location).\n"
        "  5. Re-run: python src/adherence/interrater.py\n"
    )


def _write_report(
    overall_kappa: float,
    per_policy: dict[str, dict],
    n_examples: int,
    rater2_path: Path,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Interrater Reliability Report")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- Rater 1 labels: `{RATER1_PATH.relative_to(PROJECT_ROOT)}`")
    lines.append(f"- Rater 2 labels: `{rater2_path}`")
    lines.append(f"- Examples scored by both raters: {n_examples}")
    lines.append("")
    lines.append("## Overall Cohen's kappa")
    lines.append("")
    lines.append(f"- κ = **{overall_kappa:.3f}** — {kappa_interpretation(overall_kappa)}")
    lines.append("")
    lines.append("## Per-policy Cohen's kappa")
    lines.append("")
    lines.append("| Policy | n | κ | Interpretation |")
    lines.append("|---|---:|---:|---|")
    for policy, info in per_policy.items():
        lines.append(
            f"| `{policy}` | {info['n']} | {info['kappa']:.3f} | "
            f"{kappa_interpretation(info['kappa'])} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append(
        "Cohen's kappa is a chance-corrected agreement measure for two raters "
        "with categorical labels. Values near 1.0 indicate strong agreement above "
        "chance; values near 0.0 indicate agreement no better than chance. The "
        "Landis & Koch interpretive bands above are heuristic and should not be "
        "over-interpreted on small samples."
    )
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not RATER2_PATH.exists():
        _print_rater2_workflow()
        return

    prompts = pd.read_csv(PROMPTS_PATH)
    rater1 = pd.read_csv(RATER1_PATH)
    rater2 = pd.read_csv(RATER2_PATH)

    merged = (
        prompts[["id", "policy_type"]]
        .merge(rater1[["id", "human_label"]].rename(columns={"human_label": "label_r1"}), on="id")
        .merge(rater2[["id", "human_label"]].rename(columns={"human_label": "label_r2"}), on="id")
    )

    overall = cohen_kappa(merged["label_r1"].tolist(), merged["label_r2"].tolist(), LABELS)

    per_policy: dict[str, dict] = {}
    for policy, group in merged.groupby("policy_type"):
        labels_a = group["label_r1"].tolist()
        labels_b = group["label_r2"].tolist()
        try:
            k = cohen_kappa(labels_a, labels_b, LABELS)
        except ValueError:
            k = float("nan")
        per_policy[policy] = {"n": int(len(group)), "kappa": float(k)}

    _write_report(overall, per_policy, n_examples=int(len(merged)), rater2_path=RATER2_PATH)
    print(f"Overall Cohen's kappa: {overall:.3f} ({kappa_interpretation(overall)})")
    print(f"Wrote report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
