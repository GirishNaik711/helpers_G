#core/schemas/routing.py
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class Intent(str, Enum):
    portfolio_relation = "portfolio_relation"
    asset_deep_dive = "asset_deep_dive"
    risk_explainer = "risk_explainer"
    definition = "definition"
    recap_insight = "recap_insight"
    generic_scope = "generic_scope"


class Confidence(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Entities(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tickers: list[str] = Field(default_factory=list)
    asset_names: list[str] = Field(default_factory=list)
    sectors: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)


class RetrievalPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intents: list[Intent] = Field(default_factory=list)
    entities: Entities = Field(default_factory=Entities)

    need_news: bool = False
    need_market_data: bool = False
    need_internal_content: bool = False

    confidence: Confidence = Confidence.medium
    why: str = Field(default="", description="1 sentence; internal logs only")

    max_news_items: int = 5
    max_internal_items: int = 3