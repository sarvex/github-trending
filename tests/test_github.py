"""
Unit/integration tests for GitHubTrendingScraper (with mock)
"""
import pytest
from github import GitHubTrendingScraper
from unittest.mock import patch

@patch.object(GitHubTrendingScraper, 'fetch')
def test_fetch_trending_repos_mocked(mock_fetch):
    # Simulate parsed soup with one repo
    class DummySoup:
        def select(self, _):
            class RepoElem:
                def select_one(self, sel):
                    if sel == "h2 a":
                        class A: get = lambda self, x, default=None: "/owner/repo"
                        return A()
                    if sel == "p.my-1":
                        class P: text = "desc"
                        return P()
                    if sel == "span[itemprop='programmingLanguage']":
                        class L: text = "python"
                        return L()
                    if sel == "a[href$='/stargazers']":
                        class S: text = "10"
                        return S()
                    if sel == "a[href$='/network/members']":
                        class F: text = "2"
                        return F()
                    if sel == "a.topic-tag":
                        class T: text = "fastapi"
                        return T()
                    return None
                def select(self, sel):
                    if sel == "a.topic-tag":
                        class T: text = "fastapi"
                        return [T()]
                    return []
            return [RepoElem()]
    mock_fetch.return_value = DummySoup()
    scraper = GitHubTrendingScraper()
    repos = scraper.fetch_trending_repos("python")
    assert len(repos) == 1
    assert repos[0]["id"] == "owner/repo"
    assert repos[0]["language"] == "python"
