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
pytest
```

Configuration is loaded from environment variables. Copy the repository's `.env.example` to `.env` at the repository root for local use. Keep all API credentials server-side.
