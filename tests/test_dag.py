"""Tests for the Hattie variable subset DAG."""

from pathlib import Path

import networkx as nx

from src.dag.build_dag import build_graph
from src.dag.dag_schema import DAG_EDGES

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VARIABLES_CSV = PROJECT_ROOT / "data" / "hattie_variable_subset.csv"


EXPECTED_NODES = {
    "teacher_clarity",
    "feedback_quality",
    "scaffolding",
    "prior_achievement",
    "language_background",
    "engagement_history",
    "student_confidence",
    "error_rate",
    "hint_dependency",
    "learning_outcome",
}


def test_graph_builds_successfully():
    graph = build_graph(str(VARIABLES_CSV))
    assert isinstance(graph, nx.DiGraph)
    assert graph.number_of_nodes() > 0


def test_graph_is_directed():
    graph = build_graph(str(VARIABLES_CSV))
    assert graph.is_directed()


def test_graph_is_acyclic():
    graph = build_graph(str(VARIABLES_CSV))
    assert nx.is_directed_acyclic_graph(graph)


def test_expected_nodes_exist():
    graph = build_graph(str(VARIABLES_CSV))
    assert EXPECTED_NODES.issubset(set(graph.nodes))


def test_expected_edges_exist():
    graph = build_graph(str(VARIABLES_CSV))
    for src, dst in DAG_EDGES:
        assert graph.has_edge(src, dst), f"Missing edge {src} -> {dst}"


def test_node_attributes_populated():
    graph = build_graph(str(VARIABLES_CSV))
    for node in graph.nodes:
        attrs = graph.nodes[node]
        assert attrs.get("label"), f"Node {node} missing label"
        assert attrs.get("taxonomy"), f"Node {node} missing taxonomy"
        assert attrs.get("description"), f"Node {node} missing description"
