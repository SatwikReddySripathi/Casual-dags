"""Run the classifier-error sensitivity sweep and write artifacts.

Entry point:

    python src/sensitivity/run_analysis.py

Produces:
    outputs/sensitivity_curve.png       — bias vs classifier error rate
    outputs/sensitivity_predictions.csv — per-sweep estimates (one row per setting)
    outputs/sensitivity_report.md       — interpretation and reviewer-facing summary
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.sensitivity.simulate import (
    TrialData,
    inject_classifier_error,
    simulate_trial,
)

OUTPUT_DIR = PROJECT_ROOT / "outputs"
CURVE_PATH = OUTPUT_DIR / "sensitivity_curve.png"
TABLE_PATH = OUTPUT_DIR / "sensitivity_predictions.csv"
REPORT_PATH = OUTPUT_DIR / "sensitivity_report.md"


def per_protocol_estimate(T: np.ndarray, A_hat: np.ndarray, Y: np.ndarray) -> float:
    """Effect estimate restricted to classifier-identified adherers."""
    mask = A_hat == 1
    treated = Y[mask & (T == 1)]
    control = Y[mask & (T == 0)]
    if len(treated) == 0 or len(control) == 0:
        return float("nan")
    return float(treated.mean() - control.mean())


def itt_estimate(T: np.ndarray, Y: np.ndarray) -> float:
    """Intent-to-treat effect estimate (ignores adherence)."""
    treated = Y[T == 1]
    control = Y[T == 0]
    if len(treated) == 0 or len(control) == 0:
        return float("nan")
    return float(treated.mean() - control.mean())


def run_sweep(
    true_effect: float = 0.5,
    adherence_rate: float = 0.85,
    error_rates: np.ndarray | None = None,
    n_per_trial: int = 1000,
    n_runs: int = 200,
    noise_sd: float = 1.0,
    base_seed: int = 0,
) -> pd.DataFrame:
    """Sweep classifier error rate, averaging over many simulated trials."""
    if error_rates is None:
        error_rates = np.linspace(0.0, 0.5, 11)

    rows = []
    for err in error_rates:
        pp_estimates = []
        itt_estimates = []
        for run in range(n_runs):
            data: TrialData = simulate_trial(
                n=n_per_trial,
                true_effect=true_effect,
                adherence_rate=adherence_rate,
                noise_sd=noise_sd,
                seed=base_seed + run,
            )
            A_hat = inject_classifier_error(
                data.A_true,
                error_rate=err,
                seed=base_seed + run + 100_000,
            )
            pp_estimates.append(per_protocol_estimate(data.T, A_hat, data.Y))
            itt_estimates.append(itt_estimate(data.T, data.Y))

        pp_arr = np.array(pp_estimates, dtype=float)
        itt_arr = np.array(itt_estimates, dtype=float)
        rows.append(
            {
                "classifier_error_rate": float(err),
                "true_effect": true_effect,
                "pp_mean": float(np.nanmean(pp_arr)),
                "pp_sd": float(np.nanstd(pp_arr)),
                "pp_bias": float(np.nanmean(pp_arr) - true_effect),
                "itt_mean": float(np.nanmean(itt_arr)),
                "itt_bias": float(np.nanmean(itt_arr) - true_effect),
                "n_per_trial": int(n_per_trial),
                "n_runs": int(n_runs),
            }
        )
    return pd.DataFrame(rows)


def plot_curve(df: pd.DataFrame, true_effect: float, png_path: Path) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.errorbar(
        df["classifier_error_rate"],
        df["pp_mean"],
        yerr=df["pp_sd"],
        marker="o",
        capsize=3,
        linewidth=1.6,
        label="Per-protocol estimate (mean ± SD)",
        color="#1f6fb2",
    )
    ax.plot(
        df["classifier_error_rate"],
        df["itt_mean"],
        marker="s",
        linestyle="--",
        linewidth=1.4,
        label="Intent-to-treat estimate (mean)",
        color="#a14f00",
    )
    ax.axhline(
        true_effect,
        color="#2e7d32",
        linestyle=":",
        linewidth=1.6,
        label=f"True treatment effect (θ = {true_effect})",
    )

    ax.set_xlabel("Classifier error rate (symmetric flip probability)")
    ax.set_ylabel("Estimated treatment effect")
    ax.set_title(
        "Sensitivity of causal estimate to adherence-classifier error\n"
        "(reviewer concern: classifier error propagation)",
        fontsize=13,
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left", frameon=True)
    fig.tight_layout()
    fig.savefig(png_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_report(df: pd.DataFrame, true_effect: float, report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    zero_err = df.iloc[0]
    worst = df.loc[df["pp_bias"].abs().idxmax()]
    v1_err = 1.0 / 30.0  # V1 baseline misclassification rate
    nearest_idx = (df["classifier_error_rate"] - v1_err).abs().idxmin()
    v1_row = df.loc[nearest_idx]

    lines: list[str] = []
    lines.append("# Classifier-error Sensitivity Analysis — V2")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This analysis directly answers the reviewer's deeper concern about the "
        "adherence classifier: not just whether the classifier is validated, but "
        "how classifier error propagates into the causal estimates the classifier "
        "gates. A per-protocol estimate that filters on a noisy adherence "
        "prediction is biased; this sweep quantifies that bias as a function of "
        "classifier error rate."
    )
    lines.append("")
    lines.append("## Simulation setup")
    lines.append("")
    lines.append(f"- True treatment effect θ = {true_effect}")
    lines.append(
        "- Synthetic randomized trial: T ~ Bernoulli(0.5), "
        "A ~ Bernoulli(adherence_rate), "
        "Y = (θ · T if A=1 else 0) + N(0, 1)."
    )
    lines.append(
        f"- {int(zero_err['n_runs'])} independent trials of "
        f"{int(zero_err['n_per_trial'])} units per error-rate setting."
    )
    lines.append(
        "- Symmetric classifier error model: each true label is flipped "
        "independently with probability `classifier_error_rate`."
    )
    lines.append("")
    lines.append("## Headline results")
    lines.append("")
    lines.append("| Scenario | Classifier error rate | PP estimate (mean) | PP bias vs θ |")
    lines.append("|---|---:|---:|---:|")
    lines.append(
        f"| Perfect classifier | {zero_err['classifier_error_rate']:.3f} | "
        f"{zero_err['pp_mean']:.3f} | {zero_err['pp_bias']:+.3f} |"
    )
    lines.append(
        f"| V1 baseline-rate match (~1/30) | {v1_row['classifier_error_rate']:.3f} | "
        f"{v1_row['pp_mean']:.3f} | {v1_row['pp_bias']:+.3f} |"
    )
    lines.append(
        f"| Worst case in sweep | {worst['classifier_error_rate']:.3f} | "
        f"{worst['pp_mean']:.3f} | {worst['pp_bias']:+.3f} |"
    )
    lines.append("")
    lines.append("## Full sweep")
    lines.append("")
    lines.append("| Classifier error | PP mean | PP SD | PP bias | ITT mean | ITT bias |")
    lines.append("|---:|---:|---:|---:|---:|---:|")
    for _, row in df.iterrows():
        lines.append(
            f"| {row['classifier_error_rate']:.3f} | "
            f"{row['pp_mean']:.3f} | {row['pp_sd']:.3f} | "
            f"{row['pp_bias']:+.3f} | {row['itt_mean']:.3f} | "
            f"{row['itt_bias']:+.3f} |"
        )
    lines.append("")
    lines.append("See `sensitivity_curve.png` for the figure.")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "The intent-to-treat estimate is biased toward zero because non-adherent "
        "units carry no treatment effect — this is mechanical and is the reason the "
        "framework needs an adherence classifier at all. The per-protocol estimate "
        "approaches the true treatment effect θ when classifier error is zero and "
        "drifts toward the ITT estimate as classifier error increases, because the "
        "per-protocol subset becomes increasingly contaminated by non-adherers "
        "(false positives) and shrinks (false negatives)."
    )
    lines.append("")
    lines.append(
        "**For the reviewer's purposes:** the V1 baseline classifier's "
        "misclassification rate sits in the low-bias region of this sweep, but the "
        "V1 dataset is internally calibrated and not a true error-rate estimate. "
        "The real classifier error rate, measured against held-out human-rated data "
        "with multiple raters, is the input this curve needs to make a quantitative "
        "claim about how much causal-estimate bias the platform actually carries."
    )
    lines.append("")
    lines.append("## What this analysis intentionally simplifies")
    lines.append("")
    lines.append("- Single binary treatment. The Medhavi platform has multiple policy contrasts.")
    lines.append("- Symmetric classifier error. Real classifiers typically have asymmetric error rates.")
    lines.append("- No covariate adjustment. A real analysis would use covariates to reduce variance.")
    lines.append("- Static adherence. The paper §6 discusses time-varying treatments where adherence patterns evolve.")
    lines.append("- No interrater disagreement model. The current sweep treats classifier error as a single quantity; a full model would propagate disagreement between human raters into classifier-error uncertainty.")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    true_effect = 0.5
    df = run_sweep(
        true_effect=true_effect,
        adherence_rate=0.85,
        n_per_trial=1000,
        n_runs=200,
    )

    df.to_csv(TABLE_PATH, index=False)
    print(f"Wrote sweep table: {TABLE_PATH}")

    plot_curve(df, true_effect, CURVE_PATH)
    print(f"Wrote sensitivity curve: {CURVE_PATH}")

    write_report(df, true_effect, REPORT_PATH)
    print(f"Wrote sensitivity report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
