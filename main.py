import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.wsgi import WSGIMiddleware
from server.services import TrendingAnalysisService
from server.cache import cache_get, cache_set
from requests.exceptions import HTTPError
from dotenv import load_dotenv
from client import app as dash_app

load_dotenv()

logging.basicConfig(level=logging.INFO)

CACHE_TTL = 1800  # 30 minutes

app = FastAPI()

# Mount Dash at root
app.mount("/", WSGIMiddleware(dash_app.server))

@app.get("/analyze/github/trending/{language}", response_model=None, tags=["Trending Analysis"])
def analyze_github_trending(language: str):
    """
    Analyze trending GitHub repositories for a specified language and return graph data.
    Utilizes caching to avoid redundant scraping.
    """
    cache_key = f"trending:{language.lower()}"
    cached = cache_get(cache_key)
    if cached:
        return JSONResponse(content=cached)
    try:
        graph = TrendingAnalysisService.get_trending_graph(language)
        cache_set(cache_key, graph.model_dump(), ttl=CACHE_TTL)
        return JSONResponse(content=graph.model_dump())
    except HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
