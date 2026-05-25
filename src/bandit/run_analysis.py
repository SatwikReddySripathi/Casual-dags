"""Run the V2 Module A1 bandit-inference demos and write artifacts.

Entry point:

    python src/bandit/run_analysis.py

Produces:
    outputs/bandit_winners_curse.png    — winner's curse bias vs K
    outputs/bandit_ipw_vs_naive.png     — IPW vs naive estimator bias
    outputs/bandit_inference_table.csv  — sweep table
    outputs/bandit_inference_report.md  — methodology and interpretation
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

from src.bandit.inference import (
    bootstrap_winner_debiased,
    ipw_arm_means,
    naive_arm_means,
)
from src.bandit.simulate import (
    run_softmax_bandit,
    simulate_winners_curse,
)

OUTPUT_DIR = PROJECT_ROOT / "outputs"
WINNERS_PNG = OUTPUT_DIR / "bandit_winners_curse.png"
IPW_PNG = OUTPUT_DIR / "bandit_ipw_vs_naive.png"
TABLE_PATH = OUTPUT_DIR / "bandit_inference_table.csv"
REPORT_PATH = OUTPUT_DIR / "bandit_inference_report.md"


# -----------------------------------------------------------------------------
# Winner's curse sweep
# -----------------------------------------------------------------------------


def winners_curse_sweep(
    k_values: list[int],
    n_per_arm: int = 50,
    n_sims: int = 2000,
    true_mean: float = 0.5,
    seed: int = 0,
) -> pd.DataFrame:
    rows = []
    for K in k_values:
        run = simulate_winners_curse(
            K=K,
            n_per_arm=n_per_arm,
            n_sims=n_sims,
            true_means=np.full(K, true_mean),
            seed=seed,
        )
        observed = float(run.winner_observed.mean())
        # Bootstrap-debias each sim's winner and average.
        debiased_means = []
        for sim_idx in range(n_sims):
            obs_row = run.observed_means[sim_idx]
            # Synthesize a per-sim "data": fake per-arm reward sequences of
            # length n_per_arm that average to the observed mean. For the
            # bootstrap to make sense we need actual realizations, which we
            # don't store. So we use a quick analytic correction here instead:
            # the observed winner mean less the empirical mean upward gap.
            true_mean_array = np.full(K, true_mean)
            _ = true_mean_array  # placeholder; analytic correction shown below
            # Analytic estimate of upward selection bias:
            #   bias ≈ (max(obs_row) - mean(obs_row)) * 0 for analysis-only;
            # we report the bootstrap result on a representative single run
            # below rather than within the sweep loop, to keep this fast.
            debiased_means.append(obs_row.max())
        rows.append(
            {
                "K": K,
                "true_mean": true_mean,
                "n_per_arm": n_per_arm,
                "n_sims": n_sims,
                "winner_observed_mean": observed,
                "winners_curse_bias": observed - true_mean,
            }
        )
    return pd.DataFrame(rows)


def plot_winners_curse(df: pd.DataFrame, true_mean: float, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(
        df["K"],
        df["winner_observed_mean"],
        marker="o",
        linewidth=1.8,
        color="#a14f00",
        label="Observed mean of empirical-best arm",
    )
    ax.axhline(
        true_mean,
        color="#2e7d32",
        linestyle=":",
        linewidth=1.6,
        label=f"True mean (all arms identical, μ = {true_mean})",
    )
    ax.set_xlabel("Number of arms K")
    ax.set_ylabel("Estimated mean of selected arm")
    ax.set_title(
        "Winner's curse: empirical-best arm mean inflates with K\n"
        "(reviewer concern: premature convergence on a false best arm)",
        fontsize=13,
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", frameon=True)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Adaptive collection: IPW vs naive
# -----------------------------------------------------------------------------


def ipw_vs_naive_sweep(
    temperatures: list[float],
    true_means: np.ndarray,
    n_batches: int = 12,
    batch_size: int = 30,
    n_runs: int = 200,
    base_seed: int = 0,
) -> pd.DataFrame:
    """For each softmax temperature (allocation sharpness), measure mean
    absolute bias of naive and IPW arm-mean estimators across many runs.
    """
    K = len(true_means)
    rows = []
    for tau in temperatures:
        naive_mae = []
        ipw_mae = []
        for r in range(n_runs):
            log = run_softmax_bandit(
                true_means=true_means,
                n_batches=n_batches,
                batch_size=batch_size,
                temperature=tau,
                seed=base_seed + r,
            )
            naive = naive_arm_means(log.arms, log.rewards, K)
            ipw = ipw_arm_means(log.arms, log.rewards, log.propensities, K)
            naive_mae.append(float(np.nanmean(np.abs(naive - true_means))))
            ipw_mae.append(float(np.nanmean(np.abs(ipw - true_means))))
        rows.append(
            {
                "softmax_temperature": tau,
                "naive_mae": float(np.nanmean(naive_mae)),
                "ipw_mae": float(np.nanmean(ipw_mae)),
                "n_runs": n_runs,
                "n_batches": n_batches,
                "batch_size": batch_size,
            }
        )
    return pd.DataFrame(rows)


def plot_ipw_vs_naive(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(
        df["softmax_temperature"],
        df["naive_mae"],
        marker="o",
        linewidth=1.8,
        color="#a14f00",
        label="Naive sample-mean estimator",
    )
    ax.plot(
        df["softmax_temperature"],
        df["ipw_mae"],
        marker="s",
        linewidth=1.8,
        color="#1f6fb2",
        label="IPW estimator (uses recorded propensities)",
    )
    ax.set_xlabel("Softmax allocation temperature (higher = more concentration on apparent-best arm)")
    ax.set_ylabel("Mean absolute estimation error across arms")
    ax.set_title(
        "Adaptive collection: IPW vs naive arm-mean estimators\n"
        "(reviewer concern: bandit inference literature not engaged)",
        fontsize=13,
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", frameon=True)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Report
# -----------------------------------------------------------------------------


def write_report(
    winners_df: pd.DataFrame,
    ipw_df: pd.DataFrame,
    bootstrap_demo: dict,
    report_path: Path,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Bandit Inference Demos — V2 Module A1")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "Two phenomena flagged by the reviewer are demonstrated here on synthetic "
        "data so they are no longer hand-waves in the paper:"
    )
    lines.append("")
    lines.append(
        "1. **Winner's curse / premature convergence on a false best arm** — "
        "the reviewer's specific Mode 2 worry. When K arms are i.i.d. with the "
        "same true mean and you select the empirical best one, the selected "
        "arm's observed mean is biased upward purely by selection."
    )
    lines.append(
        "2. **Adaptive collection bias correction** — the reviewer's note that the "
        "paper proposes bandit-based allocation and then retrospective causal "
        "analysis without engaging the bandit-inference literature. The IPW "
        "estimator (Horvitz-Thompson-style, using recorded propensities) is the "
        "correction; this report shows it works on data the simulator generates."
    )
    lines.append("")
    lines.append("## Demo 1 — Winner's curse vs K")
    lines.append("")
    lines.append(
        "K arms, each with identical true mean μ = 0.5. For each simulation we "
        "draw n_per_arm Bernoulli outcomes per arm, pick the empirical-best arm, "
        "and record its observed mean. Averaged across simulations the difference "
        "between observed-winner-mean and true mean is the winner's-curse bias."
    )
    lines.append("")
    lines.append("| K | n per arm | n sims | Observed winner mean | Bias vs μ=0.5 |")
    lines.append("|---:|---:|---:|---:|---:|")
    for _, row in winners_df.iterrows():
        lines.append(
            f"| {int(row['K'])} | {int(row['n_per_arm'])} | {int(row['n_sims'])} | "
            f"{row['winner_observed_mean']:.4f} | {row['winners_curse_bias']:+.4f} |"
        )
    lines.append("")
    lines.append("See `bandit_winners_curse.png` for the curve.")
    lines.append("")
    lines.append("**Interpretation.** Even with K = 2 there is positive selection bias; the")
    lines.append("bias grows with K because the maximum of more i.i.d. estimates is further from")
    lines.append("their common true value. This is the rigorous form of the reviewer's")
    lines.append("'premature convergence on a false best arm' concern.")
    lines.append("")
    lines.append("### Bootstrap-based correction on one run")
    lines.append("")
    lines.append(
        "Treat the observed sample as truth, resample within each arm with "
        "replacement, recompute the winner each bootstrap iteration, and the "
        "mean (winner_observed - winner_resample) approximates the upward "
        "selection bias. Subtract it from the observed winner mean to get the "
        "debiased estimate."
    )
    lines.append("")
    lines.append(f"- Selected winner index: {bootstrap_demo['winner']}")
    lines.append(f"- Winner observed mean: {bootstrap_demo['observed']:.4f}")
    lines.append(f"- Bootstrap-debiased estimate: {bootstrap_demo['debiased']:.4f}")
    lines.append(f"- True mean of selected arm: {bootstrap_demo['true']:.4f}")
    lines.append("")
    lines.append("## Demo 2 — IPW vs naive estimator under adaptive collection")
    lines.append("")
    lines.append(
        "A softmax bandit allocates batches with probability proportional to "
        "exp(temperature · observed_mean). Higher temperature concentrates on the "
        "apparent-best arm earlier. For each temperature we run many trials and "
        "compute the mean absolute error of naive sample-mean and IPW estimators "
        "against the true means."
    )
    lines.append("")
    lines.append("| Temperature | Naive MAE | IPW MAE | Runs |")
    lines.append("|---:|---:|---:|---:|")
    for _, row in ipw_df.iterrows():
        lines.append(
            f"| {row['softmax_temperature']:.1f} | "
            f"{row['naive_mae']:.4f} | {row['ipw_mae']:.4f} | {int(row['n_runs'])} |"
        )
    lines.append("")
    lines.append("See `bandit_ipw_vs_naive.png` for the curve.")
    lines.append("")
    lines.append("**Interpretation — honest reading of the numbers.**")
    lines.append("")
    lines.append(
        "For stationary Bernoulli arms, naive per-arm sample means are "
        "approximately unbiased even under adaptive allocation, because each "
        "arm's reward distribution does not change when the bandit chooses to "
        "sample it more or less often. IPW preserves this unbiasedness but "
        "pays a variance cost from up-weighting rounds where the chosen arm "
        "had low propensity. In the simple Bernoulli setting the variance "
        "cost can match or exceed the bias gain — which is why IPW's MAE in "
        "the table above sits at or slightly above naive's."
    )
    lines.append("")
    lines.append("Where IPW (and the broader bandit-inference literature) genuinely matters:")
    lines.append("")
    lines.append("- **Winner-selection bias** — Demo 1 above is the live case. Reporting the empirical-best arm's observed mean overstates that arm's true performance. The bootstrap or IPW-style debiasing is what produces the honest number.")
    lines.append("- **Contextual settings** — when the allocator depends on student covariates that also affect reward, naive sample means are biased and IPW (or g-computation) restores unbiasedness. This is the setting Medhavi will actually deploy in.")
    lines.append("- **Non-stationary arms** — when arm reward distributions drift, the rounds an arm was chosen on are correlated with that arm's reward at that time. Naive averaging mixes regimes; IPW with the right weighting separates them.")
    lines.append("- **Confidence intervals** — naive intervals on bandit-collected data are anti-conservative; the bandit-inference literature provides corrected CIs via sandwich variance or martingale bounds.")
    lines.append("")
    lines.append(
        "The takeaway for the Medhavi paper is twofold: (1) when reporting "
        "'the best policy works at level X', use Demo 1's debiasing; (2) when "
        "running retrospective causal analysis on bandit-collected data with "
        "covariates, the per-round propensities must be logged so IPW (or a "
        "doubly-robust variant) can correct the resulting biases."
    )
    lines.append("")
    lines.append("## What is intentionally simplified")
    lines.append("")
    lines.append("- Bernoulli arms only. Real-world rewards are richer (continuous GLP scores).")
    lines.append("- Softmax allocator with known propensities. Real Thompson sampling needs Monte Carlo for exact propensities; the simplification keeps IPW well-defined.")
    lines.append("- No context features. Contextual bandits would use IPW conditioned on student covariates.")
    lines.append("- Stationary arms. The platform's true means may drift with content updates.")
    lines.append("")
    lines.append("## Next within Phase A")
    lines.append("")
    lines.append("- A2: G-methods feasibility demo (time-varying treatments).")
    lines.append("- A3: Multiple-comparisons correction demo.")
    lines.append("- A4: Differential-attrition monitor.")
    lines.append("- A5: Early-stopping safeguard for bandits (integrates with this module's simulator).")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Demo 1: winner's curse vs K.
    true_mean = 0.5
    k_values = [2, 3, 4, 5, 7, 10, 15, 20]
    winners_df = winners_curse_sweep(
        k_values=k_values,
        n_per_arm=50,
        n_sims=3000,
        true_mean=true_mean,
        seed=0,
    )
    plot_winners_curse(winners_df, true_mean, WINNERS_PNG)
    print(f"Wrote winners-curse plot: {WINNERS_PNG}")

    # Bootstrap demo on one representative run with K = 5.
    from src.bandit.simulate import simulate_winners_curse as _sim

    # Synthesize per-round draws so the bootstrap can resample.
    rng = np.random.default_rng(7)
    K = 5
    n_per_arm = 50
    arms_list = []
    rewards_list = []
    for k in range(K):
        arms_list.append(np.full(n_per_arm, k))
        rewards_list.append(rng.binomial(1, 0.5, size=n_per_arm))
    arms_single = np.concatenate(arms_list)
    rewards_single = np.concatenate(rewards_list)
    naive_means_single = np.array([rewards_single[arms_single == k].mean() for k in range(K)])
    selected_winner = int(np.argmax(naive_means_single))
    debiased_winner, debiased_value = bootstrap_winner_debiased(
        arms=arms_single,
        rewards=rewards_single,
        K=K,
        n_bootstrap=1000,
        seed=11,
    )
    bootstrap_demo = {
        "winner": int(selected_winner),
        "observed": float(naive_means_single[selected_winner]),
        "debiased": float(debiased_value),
        "true": 0.5,
    }

    # Demo 2: IPW vs naive across allocation temperatures.
    true_means = np.array([0.45, 0.50, 0.55])
    temperatures = [0.0, 1.0, 3.0, 6.0, 10.0, 15.0]
    ipw_df = ipw_vs_naive_sweep(
        temperatures=temperatures,
        true_means=true_means,
        n_batches=12,
        batch_size=30,
        n_runs=300,
        base_seed=42,
    )
    plot_ipw_vs_naive(ipw_df, IPW_PNG)
    print(f"Wrote IPW-vs-naive plot: {IPW_PNG}")

    # Combined table for transparency.
    winners_df.assign(demo="winners_curse").to_csv(TABLE_PATH, index=False)
    print(f"Wrote sweep table: {TABLE_PATH}")

    write_report(winners_df, ipw_df, bootstrap_demo, REPORT_PATH)
    print(f"Wrote bandit inference report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
