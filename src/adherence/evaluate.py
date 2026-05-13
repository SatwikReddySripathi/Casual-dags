"""Evaluate the rule-based adherence classifier against manual labels.

Run from project root:

    python src/adherence/evaluate.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend; do this before pyplot import
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    precision_recall_fscore_support,
)

# Make `src.adherence...` imports work when this script is run directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.adherence.generate_report import generate_markdown_report
from src.adherence.rubric import LABELS
from src.adherence.rule_based_classifier import classify_response

DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

PROMPTS_PATH = DATA_DIR / "sample_prompts.csv"
LABELS_PATH = DATA_DIR / "manual_labels.csv"
PREDICTIONS_PATH = OUTPUT_DIR / "adherence_predictions.csv"
CONFUSION_PATH = OUTPUT_DIR / "adherence_confusion_matrix.png"
REPORT_PATH = OUTPUT_DIR / "adherence_baseline_report.md"

REQUIRED_PROMPT_COLS = {"id", "policy_type", "student_prompt", "assigned_policy", "tutor_response"}
REQUIRED_LABEL_COLS = {"id", "human_label", "human_reason"}


def _validate_columns(df: pd.DataFrame, required: set, name: str) -> None:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{name} is missing required columns: {sorted(missing)}")


def _load_data() -> pd.DataFrame:
    if not PROMPTS_PATH.exists():
        raise FileNotFoundError(f"Missing prompts file: {PROMPTS_PATH}")
    if not LABELS_PATH.exists():
        raise FileNotFoundError(f"Missing labels file: {LABELS_PATH}")

    prompts = pd.read_csv(PROMPTS_PATH)
    labels = pd.read_csv(LABELS_PATH)

    _validate_columns(prompts, REQUIRED_PROMPT_COLS, "sample_prompts.csv")
    _validate_columns(labels, REQUIRED_LABEL_COLS, "manual_labels.csv")

    invalid_labels = set(labels["human_label"]) - set(LABELS)
    if invalid_labels:
        raise ValueError(f"manual_labels.csv contains invalid labels: {invalid_labels}")

    prompt_ids = set(prompts["id"])
    label_ids = set(labels["id"])
    if prompt_ids != label_ids:
        only_prompts = prompt_ids - label_ids
        only_labels = label_ids - prompt_ids
        raise ValueError(
            "id mismatch between prompts and labels — "
            f"only in prompts: {sorted(only_prompts)}, only in labels: {sorted(only_labels)}"
        )

    merged = prompts.merge(labels, on="id", how="inner").sort_values("id").reset_index(drop=True)
    return merged


def _run_classifier(df: pd.DataFrame) -> pd.DataFrame:
    predicted_labels: list[str] = []
    reasons_col: list[str] = []
    flag_records: list[dict] = []

    for _, row in df.iterrows():
        result = classify_response(
            policy_type=row["policy_type"],
            tutor_response=str(row["tutor_response"] or ""),
            student_prompt=str(row.get("student_prompt") or ""),
        )
        predicted_labels.append(result["predicted_label"])
        reasons_col.append(" | ".join(result["reasons"]))
        flag_records.append(result["flags"])

    df = df.copy()
    df["predicted_label"] = predicted_labels
    df["classifier_reasons"] = reasons_col
    flags_df = pd.DataFrame(flag_records).add_prefix("flag_")
    df = pd.concat([df.reset_index(drop=True), flags_df.reset_index(drop=True)], axis=1)
    return df


def _compute_metrics(df: pd.DataFrame) -> dict:
    y_true = df["human_label"].tolist()
    y_pred = df["predicted_label"].tolist()

    accuracy = float(np.mean([yt == yp for yt, yp in zip(y_true, y_pred)]))

    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=LABELS, average="macro", zero_division=0
    )
    per_p, per_r, per_f1, per_s = precision_recall_fscore_support(
        y_true, y_pred, labels=LABELS, average=None, zero_division=0
    )

    per_label = {
        label: {
            "precision": float(per_p[i]),
            "recall": float(per_r[i]),
            "f1": float(per_f1[i]),
            "support": int(per_s[i]),
        }
        for i, label in enumerate(LABELS)
    }

    return {
        "total_examples": int(len(df)),
        "policy_types": sorted(df["policy_type"].unique().tolist()),
        "label_set": list(LABELS),
        "accuracy": accuracy,
        "macro_precision": float(macro_p),
        "macro_recall": float(macro_r),
        "macro_f1": float(macro_f1),
        "per_label": per_label,
    }


def _save_confusion_matrix(df: pd.DataFrame, path: Path) -> None:
    y_true = df["human_label"].tolist()
    y_pred = df["predicted_label"].tolist()
    cm = confusion_matrix(y_true, y_pred, labels=LABELS)

    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(LABELS)))
    ax.set_yticks(range(len(LABELS)))
    ax.set_xticklabels(LABELS, rotation=30, ha="right")
    ax.set_yticklabels(LABELS)
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("Human label")
    ax.set_title("Adherence Classifier V1 — Confusion Matrix")

    threshold = cm.max() / 2.0 if cm.max() > 0 else 0.5
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            color = "white" if cm[i, j] > threshold else "black"
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", color=color)

    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _collect_errors(df: pd.DataFrame) -> list[dict]:
    errs = []
    mismatched = df[df["human_label"] != df["predicted_label"]]
    for _, row in mismatched.iterrows():
        errs.append(
            {
                "id": int(row["id"]),
                "policy_type": row["policy_type"],
                "human_label": row["human_label"],
                "predicted_label": row["predicted_label"],
                "tutor_response": row["tutor_response"],
                "reasons": [r for r in str(row["classifier_reasons"]).split(" | ") if r],
            }
        )
    return errs


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = _load_data()
    df = _run_classifier(df)

    df.to_csv(PREDICTIONS_PATH, index=False)
    print(f"Wrote predictions: {PREDICTIONS_PATH}")

    metrics = _compute_metrics(df)
    _save_confusion_matrix(df, CONFUSION_PATH)
    print(f"Wrote confusion matrix: {CONFUSION_PATH}")

    errors = _collect_errors(df)
    generate_markdown_report(metrics, errors, str(REPORT_PATH))
    print(f"Wrote report: {REPORT_PATH}")

    print(
        "Baseline metrics — "
        f"accuracy={metrics['accuracy']:.3f}, "
        f"macro_f1={metrics['macro_f1']:.3f}, "
        f"errors={len(errors)}/{metrics['total_examples']}"
    )


if __name__ == "__main__":
    main()
