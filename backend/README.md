# Backend

FastAPI service for BreatheWise AI.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run tests from this directory:

```bash
pytest -q
```

## Endpoints

- `GET /health` — service health check.
- `GET /api/locations/search?name=Hyderabad` — city/town lookup.
- `GET /api/air-quality?latitude=17.385&longitude=78.486` — modeled current conditions, US AQI scale, pollutant concentrations, and source metadata.

The example coordinates are illustrative only. The API does not request or infer browser location.

The air-quality response is based on Open-Meteo modeled data; it is not a CPCB station measurement or a personal exposure reading. Keep this caveat visible in any client that consumes the endpoint.

Configuration is loaded from environment variables. Copy the repository's `.env.example` to `.env` at the repository root for local use. Keep all API credentials server-side.
