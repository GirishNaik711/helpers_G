core/schemas/qa.py
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from core.schemas.citations import Citation
from core.schemas.insights import Insight
from core.schemas.routing import RetrievalPlan
from core.schemas.user_context import UserContext


class Role(str, Enum):
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Role
    content: str
    created_at: datetime


class ClaimType(str, Enum):
    market_fact = "market_fact"
    news_fact = "news_fact"
    portfolio_fact = "portfolio_fact"
    definition = "definition"
    explanation = "explanation"


class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str
    text: str
    type: ClaimType
    requires_citation: bool = True


class Confidence(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class QuestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    question: str
    context_mode: str = Field(
        default="insights_plus_sources",
        description="insights_only | insights_plus_sources",
    )


class Answer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer_text: str
    direct_portfolio_relevance: Optional[str] = None
    risks_and_considerations: list[str] = Field(default_factory=list)

    citations: list[Citation] = Field(default_factory=list)
    confidence: Confidence = Confidence.medium
    disclaimer: Optional[str] = None


class ToolContext(BaseModel):
    """
    Retrieval outputs used by synthesis. Keep generic for PoC.
    """

    model_config = ConfigDict(extra="forbid")

    market_data: dict = Field(default_factory=dict)
    news_items: list[dict] = Field(default_factory=list)
    internal_content: list[dict] = Field(default_factory=list)


class QAState(BaseModel):
    """
    State carried through the QA flow (LangGraph).
    """

    model_config = ConfigDict(extra="forbid")

    session_id: str
    user_id: str

    user_context: UserContext
    insights_context: list[Insight] = Field(default_factory=list)

    conversation: list[Message] = Field(default_factory=list)  # last 6 messages
    retrieval_plan: Optional[RetrievalPlan] = None
    tool_context: ToolContext = Field(default_factory=ToolContext)

    draft_answer: Optional[str] = None
    claims: list[Claim] = Field(default_factory=list)

    final_answer: Optional[Answer] = None