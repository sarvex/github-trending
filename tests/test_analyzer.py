"""
Unit tests for the analyzer (graph construction)
"""
from analyzer import analyze_repositories
from domain import Repository

def test_analyze_repositories_shared_topics():
    repo1 = Repository(id="a/b", description="", stars=1, forks=1, language="python", topics=["fastapi", "web"])
    repo2 = Repository(id="c/d", description="", stars=2, forks=2, language="python", topics=["fastapi", "api"])
    repo3 = Repository(id="e/f", description="", stars=3, forks=3, language="python", topics=["data"])
    repos = [repo1, repo2, repo3]
    graph = analyze_repositories(repos)
    assert len(graph["nodes"]) == 3
    # Only one edge with shared topic 'fastapi'
    assert any(e["source"] == "a/b" and e["target"] == "c/d" and e["weight"] == 1 for e in graph["edges"])
    # No edge between repo1 and repo3
    assert not any(e["source"] == "a/b" and e["target"] == "e/f" for e in graph["edges"])
