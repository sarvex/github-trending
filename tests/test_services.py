"""
Integration tests for TrendingAnalysisService
"""
from services import TrendingAnalysisService
from unittest.mock import patch

def test_get_trending_graph_integration():
    mock_repo = {
        "id": "owner/repo",
        "description": "desc",
        "stars": 10,
        "forks": 2,
        "language": "python",
        "topics": ["fastapi"]
    }
    with patch("github.GitHubTrendingScraper.fetch_trending_repos", return_value=[mock_repo]):
        graph = TrendingAnalysisService.get_trending_graph("python")
        assert graph.nodes[0].id == "owner/repo"
        assert graph.nodes[0].language == "python"
        assert graph.edges == []  # Only one repo, so no edges
