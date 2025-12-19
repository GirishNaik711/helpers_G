import pytest
from pydantic import ValidationError

from core.schemas.routing import RetrievalPlan


def test_retrieval_plan_validates():
    data = {
        "intents": ["asset_deep_dive"],
        "entities": {"tickers": ["AAPL"], "asset_names": [], "sectors": [], "themes": []},
        "need_news": True,
        "need_market_data": False,
        "need_internal_content": False,
        "confidence": "high",
        "why": "User asked about recent news.",
    }
    plan = RetrievalPlan.model_validate(data)
    assert plan.need_news is True
    assert plan.entities.tickers == ["AAPL"]


def test_retrieval_plan_rejects_bad_schema():
    data = {"need_news": True}  # missing required fields
    with pytest.raises(ValidationError):
        RetrievalPlan.model_validate(data)
