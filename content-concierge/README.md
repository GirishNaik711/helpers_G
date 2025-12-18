# Content Concierge (PoC1)

PoC1 bootstrap for a modular Content Concierge service using FastAPI.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate

pip install -e .
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
