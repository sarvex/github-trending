"""
API/endpoint tests using FastAPI TestClient
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

def test_trending_endpoint_success():
    mock_graph = {
        "nodes": [
            {"id": "owner/repo", "description": "desc", "stars": 10, "forks": 2, "language": "python"}
        ],
        "edges": []
    }
    with patch("services.TrendingAnalysisService.get_trending_graph") as mock_service:
        class DummyGraph:
            def model_dump(self):
                return mock_graph
        mock_service.return_value = DummyGraph()
        response = client.get("/analyze/github/trending/python")
        assert response.status_code == 200
        assert response.json()["nodes"][0]["id"] == "owner/repo"


def test_trending_endpoint_error():
    with patch("services.TrendingAnalysisService.get_trending_graph", side_effect=Exception("fail")):
        response = client.get("/analyze/github/trending/python")
        assert response.status_code == 500
