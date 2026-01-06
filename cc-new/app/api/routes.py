#app.api.routes.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.schemas import GenerateInsightsRequest, GenerateInsightsResponse, ErrorResponse
from app.engine.generator import generate_insights

router = APIRouter(prefix="/v1/insights", tags=["insights"])


@router.post(
    "/generate",
    response_model=GenerateInsightsResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def generate(req: GenerateInsightsRequest) -> GenerateInsightsResponse:
    try:
        return generate_insights(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": "bad_request", "details": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "internal_error", "details": str(e)})
