# Content Concierge (PoC1)

PoC1 bootstrap for a modular Content Concierge service using FastAPI.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate

pip install -e .
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

## POSTMAN TESTS:
get user: curl -X GET http://localhost:8000/users/cust_001

get user holdings: curl -X GET http://localhost:8000/users/cust_001/holdings


get user Goals: curl -X GET http://localhost:8000/users/cust_001/goals
