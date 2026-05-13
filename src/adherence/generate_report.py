"""Markdown report generator for the adherence baseline."""

from __future__ import annotations

from pathlib import Path


def generate_markdown_report(metrics: dict, errors: list, output_path: str) -> None:
    """Write a baseline report Markdown file at ``output_path``.

    ``metrics`` must contain at minimum:
      - total_examples (int)
      - policy_types (list[str])
      - label_set (list[str])
      - accuracy (float)
      - macro_precision (float)
      - macro_recall (float)
      - macro_f1 (float)
      - per_label (dict[str, dict])  # optional
    ``errors`` is a list of dicts with id, policy_type, human_label,
    predicted_label, tutor_response, and reasons.
    """
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Medhavi Adherence Classifier V1 Baseline Report")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This baseline responds to the reviewer concern that the post-generation "
        "adherence classifier is load-bearing but lacked validation."
    )
    lines.append("")
    lines.append("## Dataset Summary")
    lines.append("")
    lines.append(f"- Total examples: {metrics.get('total_examples', 'N/A')}")
    policy_types = metrics.get("policy_types", [])
    lines.append(f"- Policy types: {', '.join(policy_types) if policy_types else 'N/A'}")
    label_set = metrics.get("label_set", [])
    lines.append(f"- Label set: {', '.join(label_set) if label_set else 'N/A'}")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Accuracy | {metrics.get('accuracy', 0.0):.3f} |")
    lines.append(f"| Macro Precision | {metrics.get('macro_precision', 0.0):.3f} |")
    lines.append(f"| Macro Recall | {metrics.get('macro_recall', 0.0):.3f} |")
    lines.append(f"| Macro F1 | {metrics.get('macro_f1', 0.0):.3f} |")
    lines.append("")

    per_label = metrics.get("per_label") or {}
    if per_label:
        lines.append("### Per-label scores")
        lines.append("")
        lines.append("| Label | Precision | Recall | F1 | Support |")
        lines.append("|---|---:|---:|---:|---:|")
        for label, vals in per_label.items():
            lines.append(
                f"| {label} | {vals.get('precision', 0.0):.3f} | "
                f"{vals.get('recall', 0.0):.3f} | {vals.get('f1', 0.0):.3f} | "
                f"{vals.get('support', 0)} |"
            )
        lines.append("")

    lines.append("## Confusion Matrix")
    lines.append("")
    lines.append("See `adherence_confusion_matrix.png`.")
    lines.append("")
    lines.append("## Error Analysis")
    lines.append("")
    if not errors:
        lines.append("No misclassified examples on this run.")
    else:
        lines.append(f"Total misclassified examples: {len(errors)}.")
        lines.append("")
        for err in errors:
            lines.append(
                f"- **id={err.get('id')}** "
                f"(policy: `{err.get('policy_type')}`) — "
                f"human: `{err.get('human_label')}`, "
                f"predicted: `{err.get('predicted_label')}`."
            )
            response_preview = (err.get("tutor_response") or "").strip().replace("\n", " ")
            if len(response_preview) > 220:
                response_preview = response_preview[:217] + "..."
            lines.append(f"  - Response: {response_preview}")
            reasons = err.get("reasons") or []
            if reasons:
                lines.append(f"  - Classifier reasoning: {'; '.join(reasons)}")
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "This is not a final classifier. It is a validation scaffold that defines "
        "the construct, creates manually labeled examples, establishes measurable "
        "baseline error rates, and reveals where classifier errors may propagate "
        "into causal claims."
    )
    lines.append("")
    lines.append("## Next Steps")
    lines.append("")
    lines.append("1. Expand from 30 examples to 100+ examples.")
    lines.append("2. Add two independent human raters.")
    lines.append("3. Compute Cohen's kappa for interrater reliability.")
    lines.append("4. Compare rule-based, LLM-as-judge, and fine-tuned classifier approaches.")
    lines.append("5. Run sensitivity analysis showing how adherence classifier error affects causal estimates.")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
