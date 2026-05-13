"""Render the Medhavi V1 DAG figures.

Two figures are produced from this script:

1. ``hattie_taxonomy_dag.png`` — the full Hattie-style variable taxonomy DAG.
   This responds to the reviewer's claim that the framework's centerpiece (the
   intervention/diagnostic/context decomposition) deserves a clean figure.

2. ``clarity_retention_dag.png`` — a publication-style replacement for the
   ASCII DAG shown in the paper's Section 2.2 (clarity / grade-retention
   mediation). This is the specific figure the reviewer named.

Run from project root:

    python src/dag/render_dag.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dag.build_dag import build_graph

DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

VARIABLES_CSV = DATA_DIR / "hattie_variable_subset.csv"
TAXONOMY_PNG = OUTPUT_DIR / "hattie_taxonomy_dag.png"
TAXONOMY_GRAPHML = OUTPUT_DIR / "hattie_taxonomy_dag.graphml"
MEDIATION_PNG = OUTPUT_DIR / "clarity_retention_dag.png"
MEDIATION_GRAPHML = OUTPUT_DIR / "clarity_retention_dag.graphml"

# -----------------------------------------------------------------------------
# Taxonomy DAG configuration
# -----------------------------------------------------------------------------

TAXONOMY_POSITIONS = {
    "prior_achievement": (-3.0, 2.0),
    "language_background": (-3.0, 0.0),
    "engagement_history": (-3.0, -2.0),
    "teacher_clarity": (-1.0, 2.4),
    "feedback_quality": (-1.0, 0.6),
    "scaffolding": (-1.0, -1.4),
    "student_confidence": (1.2, 1.6),
    "error_rate": (1.2, 0.0),
    "hint_dependency": (1.2, -1.6),
    "learning_outcome": (3.4, 0.0),
}

TAXONOMY_COLORS = {
    "Context": "#9ecae1",
    "Intervention": "#a1d99b",
    "Diagnostic": "#fdae6b",
    "Outcome": "#bcbddc",
}

# Edge styling by the source node's taxonomy. This serves as the edge
# annotation the reviewer asked for: each edge's mechanism type is visually
# distinct and listed in the legend.
EDGE_STYLES = {
    "Intervention": {"color": "#2e7d32", "style": "solid", "label": "treatment effect (Intervention →)"},
    "Context": {"color": "#1f5fa8", "style": "dashed", "label": "context covariate (Context →)"},
    "Diagnostic": {"color": "#7b3f00", "style": "solid", "label": "mediation to outcome (Diagnostic →)"},
}


def _readable_label(node_label: str) -> str:
    parts = node_label.split(" ")
    if len(parts) == 2:
        return f"{parts[0]}\n{parts[1]}"
    return node_label


def _edge_style_key(graph: nx.DiGraph, src: str) -> str:
    return graph.nodes[src]["taxonomy"]


def render_taxonomy_dag(graph: nx.DiGraph, png_path: Path, graphml_path: Path) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    graphml_path.parent.mkdir(parents=True, exist_ok=True)

    missing_positions = [n for n in graph.nodes if n not in TAXONOMY_POSITIONS]
    if missing_positions:
        raise ValueError(f"Missing fixed positions for nodes: {missing_positions}")

    node_colors = [TAXONOMY_COLORS.get(graph.nodes[n]["taxonomy"], "#cccccc") for n in graph.nodes]
    labels = {n: _readable_label(graph.nodes[n]["label"]) for n in graph.nodes}
    node_size = 3600

    fig, ax = plt.subplots(figsize=(14, 9))

    edges_by_style: dict[str, list[tuple[str, str]]] = {k: [] for k in EDGE_STYLES}
    for u, v in graph.edges():
        key = _edge_style_key(graph, u)
        edges_by_style.setdefault(key, []).append((u, v))

    for style_key, edges in edges_by_style.items():
        if not edges:
            continue
        style = EDGE_STYLES.get(style_key, {"color": "#444444", "style": "solid"})
        nx.draw_networkx_edges(
            graph,
            TAXONOMY_POSITIONS,
            edgelist=edges,
            ax=ax,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=18,
            edge_color=style["color"],
            style=style["style"],
            width=1.4,
            connectionstyle="arc3,rad=0.06",
            node_size=node_size,
        )

    nx.draw_networkx_nodes(
        graph,
        TAXONOMY_POSITIONS,
        ax=ax,
        node_color=node_colors,
        node_size=node_size,
        edgecolors="#222222",
        linewidths=1.3,
    )
    nx.draw_networkx_labels(
        graph,
        TAXONOMY_POSITIONS,
        labels=labels,
        ax=ax,
        font_size=10,
        font_weight="bold",
    )

    taxonomy_handles = [
        mpatches.Patch(color=color, label=name) for name, color in TAXONOMY_COLORS.items()
    ]
    edge_handles = [
        mlines.Line2D(
            [],
            [],
            color=cfg["color"],
            linestyle=cfg["style"],
            linewidth=1.6,
            label=cfg["label"],
        )
        for cfg in EDGE_STYLES.values()
    ]

    first_legend = ax.legend(
        handles=taxonomy_handles,
        title="Node taxonomy",
        loc="lower right",
        frameon=True,
    )
    ax.add_artist(first_legend)
    ax.legend(
        handles=edge_handles,
        title="Edge mechanism",
        loc="lower left",
        frameon=True,
        fontsize=9,
    )

    ax.set_title("Medhavi Variable Taxonomy DAG — V1 Mockup", fontsize=16, pad=18)
    ax.set_axis_off()
    ax.margins(0.12)
    fig.tight_layout()
    fig.savefig(png_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    nx.write_graphml(graph, graphml_path)


# -----------------------------------------------------------------------------
# Section 2.2 clarity / grade-retention mediation DAG
# -----------------------------------------------------------------------------

MEDIATION_NODES = {
    "teacher_clarity": {
        "label": "Teacher\nClarity",
        "role": "Intervention",
        "pos": (-3.2, 0.4),
    },
    "meeting_grade_level": {
        "label": "Meeting\nGrade-Level\nStandards",
        "role": "Diagnostic (mediator)",
        "pos": (-0.9, 0.4),
    },
    "grade_retention": {
        "label": "Grade\nRetention",
        "role": "Diagnostic (mediator)",
        "pos": (1.4, 1.8),
    },
    "achievement": {
        "label": "Achievement",
        "role": "Outcome",
        "pos": (3.6, 0.4),
    },
}

MEDIATION_EDGES = [
    ("teacher_clarity", "meeting_grade_level", "+ improves"),
    ("meeting_grade_level", "grade_retention", "− reduces"),
    ("grade_retention", "achievement", "− reduces (Hattie d≈−0.32)"),
    ("meeting_grade_level", "achievement", "+ improves"),
]

MEDIATION_ROLE_COLORS = {
    "Intervention": "#a1d99b",
    "Diagnostic (mediator)": "#fdae6b",
    "Outcome": "#bcbddc",
}


def _build_mediation_graph() -> nx.DiGraph:
    g = nx.DiGraph()
    for nid, attrs in MEDIATION_NODES.items():
        g.add_node(nid, label=attrs["label"], role=attrs["role"])
    for src, dst, sign in MEDIATION_EDGES:
        g.add_edge(src, dst, sign=sign)
    if not nx.is_directed_acyclic_graph(g):
        raise ValueError("Mediation DAG is not acyclic.")
    return g


def render_mediation_dag(png_path: Path, graphml_path: Path) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    graphml_path.parent.mkdir(parents=True, exist_ok=True)

    graph = _build_mediation_graph()
    positions = {nid: MEDIATION_NODES[nid]["pos"] for nid in graph.nodes}
    node_colors = [MEDIATION_ROLE_COLORS[graph.nodes[n]["role"]] for n in graph.nodes]
    node_size = 6500

    fig, ax = plt.subplots(figsize=(13, 7.5))

    nx.draw_networkx_edges(
        graph,
        positions,
        ax=ax,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=22,
        edge_color="#333333",
        width=1.6,
        connectionstyle="arc3,rad=0.04",
        node_size=node_size,
    )
    nx.draw_networkx_nodes(
        graph,
        positions,
        ax=ax,
        node_color=node_colors,
        node_size=node_size,
        edgecolors="#222222",
        linewidths=1.4,
    )
    nx.draw_networkx_labels(
        graph,
        positions,
        labels={n: graph.nodes[n]["label"] for n in graph.nodes},
        ax=ax,
        font_size=9,
        font_weight="bold",
    )

    edge_labels = {(u, v): d["sign"] for u, v, d in graph.edges(data=True)}
    nx.draw_networkx_edge_labels(
        graph,
        positions,
        edge_labels=edge_labels,
        ax=ax,
        font_size=9,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1.5),
        label_pos=0.5,
    )

    role_handles = [
        mpatches.Patch(color=color, label=role) for role, color in MEDIATION_ROLE_COLORS.items()
    ]
    ax.legend(handles=role_handles, title="Node role", loc="upper left", frameon=True)

    ax.set_title(
        "Clarity / Grade-Retention Mediation DAG — Replaces paper §2.2 ASCII figure",
        fontsize=14,
        pad=16,
    )
    ax.set_axis_off()
    ax.margins(0.14)
    fig.tight_layout()
    fig.savefig(png_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    nx.write_graphml(graph, graphml_path)


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------


def main() -> None:
    taxonomy_graph = build_graph(str(VARIABLES_CSV))
    render_taxonomy_dag(taxonomy_graph, TAXONOMY_PNG, TAXONOMY_GRAPHML)
    print(f"Wrote taxonomy DAG:   {TAXONOMY_PNG}")
    print(f"Wrote taxonomy GraphML: {TAXONOMY_GRAPHML}")

    render_mediation_dag(MEDIATION_PNG, MEDIATION_GRAPHML)
    print(f"Wrote mediation DAG:    {MEDIATION_PNG}")
    print(f"Wrote mediation GraphML:{MEDIATION_GRAPHML}")


if __name__ == "__main__":
    main()
