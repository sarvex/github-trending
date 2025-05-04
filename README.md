# GitHub Trending Analyzer

A combined FastAPI and Dash application to fetch, analyze, and visualize trending GitHub repositories. The interactive Dash UI is available at `/`, and API endpoints (such as `/analyze/github/trending/{language}`) are served on the same port (8000).

---

## Architecture Overview

- **Frontend:** Dash app ([client.py](client.py)) serves interactive graph visualization at `/`. The Dash app is imported and mounted by `main.py`; do not run `client.py` directly. UI constants (node size, layout, etc.) are configurable at the top of this file.
- **Backend:** Python modules for scraping GitHub trending repositories and analyzing them into graph data (nodes/edges).
- **Infrastructure:** Docker and Helm for deployment.

---

## Code Structure

```bash
/ (project root)
│
├── main.py                  # Application entrypoint (run this to start FastAPI + Dash)
├── client.py                # Dash UI app (imported and mounted at / by main.py)
├── requirements.txt         # Python dependencies
├── Dockerfile               # Containerization config
├── .env                     # Environment variables (see .env.sample)
├── README.md                # Project documentation
├── server/                  # Backend modules
│   ├── __init__.py
│   ├── analyzer.py          # Graph analysis logic
│   ├── cache.py             # Caching (in-memory or Redis)
│   ├── domain.py            # Domain models (Repository, Graph, etc.)
│   ├── github.py            # GitHub trending scraper logic
│   ├── scraper.py           # Scraper abstraction
│   ├── semantic.py          # OpenAI embedding/semantic similarity
│   └── services.py          # Service layer
├── tests/                   # Test suite
│   ├── test_analyzer.py
│   ├── test_api.py
│   ├── test_domain.py
│   ├── test_github.py
│   └── test_services.py
└── helm/
    └── github-trending/     # Helm chart for Kubernetes deployment
```

---

## Features

---

## Architecture

This project follows clean architecture principles with a domain-driven design (DDD) approach, ensuring maintainability, extensibility, and separation of concerns. The main components are:

- **API Layer ([main.py])**: Defines FastAPI endpoints and delegates business logic to the service layer.
- **Service Layer ([services.py])**: Orchestrates the application logic, calling scrapers and analyzers, and returning domain models.
- **Domain Layer ([domain.py])**: Contains core business models (Repository, Edge, Graph) using Pydantic for validation and documentation.
- **Scraper Abstraction ([scraper.py])**: Provides a generic, extensible base class for web scraping, using requests and BeautifulSoup.
- **Specialized Scraper ([github.py])**: Implements GitHub-specific scraping logic by extending the generic scraper abstraction.
- **Analyzer ([analyzer.py])**: Contains logic for analyzing repositories and building graph structures based on domain models.
- **Infrastructure ([cache.py])**: Handles in-memory caching to avoid redundant scrapes and reduce external requests.

This modular structure allows for easy extension (e.g., adding new scrapers for other sites) and ensures each component has a single, well-defined responsibility.

- **API Endpoint**: `/analyze/github/trending/{language}` — Returns trending repositories for the given language (e.g., `/analyze/github/trending/python`).
- **Web Scraping**: Uses `requests` and `BeautifulSoup4` to extract repository name, description, stars, forks, language, and topics from the GitHub trending page.
- **Graph Analysis**: Analyzes connections between repositories based on shared topics/tags. Optionally, computes semantic similarity between repository descriptions using the OpenAI API.
- **Graph JSON Output**: Returns results as nodes (repositories) and edges (connections) in a format directly usable by graph visualization libraries like D3.js, Cytoscape.js, or Vis.js.
- **Caching**: Implements in-memory caching to avoid redundant scraping for a given language within a 30-minute window.
- **Error Handling**: Handles network issues and changes in GitHub's HTML structure gracefully.

---

## Example Output

```json
{
  "nodes": [
    { "id": "owner1/repo1", "description": "...", "stars": 1234, "forks": 567, "language": "python" },
    { "id": "owner2/repo2", "description": "...", "stars": 876, "forks": 234, "language": "python" }
    // ... more nodes
  ],
  "edges": [
    { "source": "owner1/repo1", "target": "owner2/repo2", "weight": 2, "semantic_similarity": 0.72 },
    { "source": "owner1/repo1", "target": "owner3/repo3", "weight": 1 }
    // ... more edges
  ]
}
```

- **Nodes**: Each node represents a repository and includes its metadata.
- **Edges**: Each edge represents a connection between two repositories, with `weight` indicating the number of shared topics. If semantic similarity is enabled, a `semantic_similarity` field is included.

---

## Prerequisites

- Python 3.9+
- Docker (for containerized runs)
- Helm & Kubernetes (for cluster deployment)
- OpenAI API Key and model for semantic similarity (if enabled)

---

## Running Locally

```sh
pip install -r requirements.txt
python main.py
```

Visit [http://localhost:8000/](http://localhost:8000/) (or `/` if deployed) to use the Dash UI.

**Note:** All UI constants for the graph visualization (node size, font, layout, etc.) can be tuned at the top of `client.py`.

**Logging:** Logging is used throughout the codebase. Logs are output to stdout by default and can be configured for production.

**Environment Variables:**

- All sensitive and configuration values are loaded from `.env` using `python-dotenv`.
- See `.env.sample` for a template. You must set your OpenAI API key and model for semantic similarity.
- The `.env` file is loaded after imports for best practices.

---

## Docker Usage

Build and run the Dash container:

```sh
docker build -t github-trending:latest .
docker run -p 8000:8000 github-trending:latest uvicorn main:app --host 0.0.0.0 --port 8000
```

Visit [http://localhost:8000/](http://localhost:8000/) in your browser.

---

## Helm/Kubernetes Deployment

1. Build and push your Docker image to a registry (update `values.yaml`):

```sh
docker build -t your-dockerhub-username/github-trending:latest .
docker push your-dockerhub-username/github-trending:latest
```

2. Deploy with Helm:

```sh
helm install github-trending ./helm/github-trending
```

3. Customize `helm/github-trending/values.yaml` for ingress, resources, env, etc.

---

## API Usage

- Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Example endpoint:
  - `GET /analyze/github/trending/{language}`
  - Example: [http://localhost:8000/analyze/github/trending/python](http://localhost:8000/analyze/github/trending/python)

Response is a JSON graph:

```json
{
  "nodes": [
    {"id": "repo1", "description": "...", "stars": 123, "forks": 45, "language": "Python", "topics": ["ai", "ml"]},
    ...
  ],
  "edges": [
    {"source": "repo1", "target": "repo2", "weight": 2}
  ]
}
```

---

## Advanced: Semantic Similarity (Optional)

To enable semantic similarity analysis between repository descriptions:

1. Add your OpenAI API key, model, and API URL to your `.env` file (see `.env.sample`).
2. Set `ENABLE_SEMANTIC_SIMILARITY=true` in your `.env` file.
3. If semantic similarity fails (e.g., due to API/model issues), the UI will now show a warning if no edges are found.
4. Debug logs for OpenAI API issues are written to the server log.
5. The edge objects in the output will include a `semantic_similarity` field (float between 0 and 1) if enabled.

---

## Frontend Visualization

The output JSON is directly compatible with JavaScript graph libraries such as D3.js, Cytoscape.js, or Vis.js. Each node can be rendered as a graph node, and each edge as a link with strength/weight determined by shared topics or semantic similarity.

### UI Tuning

- All graph visualization constants (node size, font, layout, etc.) are at the top of `client.py`.
- You can adjust these for your preferred look and feel.

### Error Feedback

- If semantic similarity or topic analysis fails, the UI will show a warning if the graph has nodes but no edges.

---

## Troubleshooting

- **No edges in graph:** If the UI shows a warning and there are no edges, check your OpenAI API key, model, and API URL in `.env`. Review server logs for errors.
- **API errors:** All errors from OpenAI and GitHub are logged using Python's `logging` module.
- **Production cache:** For production, use Redis or Memcached instead of in-memory cache for scalability.
- **Health endpoint:** Use `/health` for readiness/liveness checks.

---

## Logging & Monitoring

- Logging is enabled throughout the codebase using the standard Python `logging` module.
- For production, configure logging to output to files or external systems (e.g., ELK, Datadog).
- All semantic/embedding failures are logged at error level.

---

## Best Practices Followed

- Clean architecture with clear separation of concerns
- All config/secrets in `.env`, loaded after imports
- Logging and error handling throughout
- UI constants are configurable
- Caching with aiocache (swap for Redis in production)
- Test suite for all major modules
- Lint and code style improvements
- User feedback for backend/semantic failures

---

## License

MIT License
