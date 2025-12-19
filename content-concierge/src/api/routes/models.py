from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class InsightsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(..., description="customer_id")


class AskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str
    conversation: list[dict] = Field(
        default_factory=list,
        description="List of Message dicts; we keep last 6 in flow",
    )


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: str
    detail: Optional[str] = None
    at: datetime = Field(default_factory=datetime.utcnow)
