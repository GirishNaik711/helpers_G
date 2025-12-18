#core/schemas/insights.py
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from core.schemas.citations import Citation


class InsightTone(str, Enum):
    educational = "educational"


class Insight(BaseModel):
    """
    Canonical insight structure (Scope doc).
    """

    model_config = ConfigDict(extra="forbid")

    insight_id: str
    headline: str
    explanation: str = Field(..., description="2–3 short sentences")
    personal_relevance: str = Field(..., description="Why this matters for this user")
    sources: list[Citation] = Field(default_factory=list)
    tone: InsightTone = InsightTone.educational


class InsightSession(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    user_id: str
    created_at: datetime
    insights: list[Insight] = Field(default_factory=list)