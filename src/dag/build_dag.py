"""Build the Hattie-style variable subset DAG from CSV metadata."""

from __future__ import annotations

import sys
from pathlib import Path

import networkx as nx
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dag.dag_schema import DAG_EDGES

REQUIRED_NODE_COLS = {"node_id", "label", "taxonomy", "description"}


def build_graph(variable_csv_path: str) -> nx.DiGraph:
    """Load node metadata from CSV and return a validated DiGraph."""
    csv_path = Path(variable_csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Variable CSV not found: {csv_path}")

    nodes_df = pd.read_csv(csv_path)
    missing = REQUIRED_NODE_COLS - set(nodes_df.columns)
    if missing:
        raise ValueError(f"Variable CSV missing columns: {sorted(missing)}")

    duplicate_ids = nodes_df["node_id"][nodes_df["node_id"].duplicated()].tolist()
    if duplicate_ids:
        raise ValueError(f"Duplicate node_id values in CSV: {duplicate_ids}")

    graph = nx.DiGraph()
    for _, row in nodes_df.iterrows():
        graph.add_node(
            row["node_id"],
            label=row["label"],
            taxonomy=row["taxonomy"],
            description=row["description"],
        )

    node_ids = set(graph.nodes)
    for src, dst in DAG_EDGES:
        if src not in node_ids:
            raise ValueError(f"Edge references unknown source node: {src}")
        if dst not in node_ids:
            raise ValueError(f"Edge references unknown target node: {dst}")
        graph.add_edge(src, dst)

    if not nx.is_directed_acyclic_graph(graph):
        cycles = list(nx.simple_cycles(graph))
        raise ValueError(f"Graph is not acyclic. Cycles found: {cycles}")

    return graph
