"""
Unit tests for domain models (Repository, Edge, Graph)
"""
from domain import Repository, Edge, Graph
import pytest

def test_repository_model():
    repo = Repository(
        id="owner/repo",
        description="A test repo",
        stars=10,
        forks=2,
        language="python",
        topics=["fastapi", "tdd"]
    )
    assert repo.id == "owner/repo"
    assert repo.language == "python"
    assert "tdd" in repo.topics

def test_graph_model():
    repo = Repository(id="a/b", description="", stars=1, forks=1, language="python", topics=[])
    edge = Edge(source="a/b", target="c/d", weight=2)
    graph = Graph(nodes=[repo], edges=[edge])
    assert graph.nodes[0].id == "a/b"
    assert graph.edges[0].weight == 2
