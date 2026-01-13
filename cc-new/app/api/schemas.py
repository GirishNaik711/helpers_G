# app/api/schemas.py

from __future__ import annotations

from datetime import datetime, date
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict, HttpUrl

class RiskMode(str, Enum):
    strict = "strict"


class InsightType(str, Enum):
    GOAL_PROGRESS = "GOAL_PROGRESS"
    MARKET_TREND = "MARKET_TREND"
    PORTFOLIO_COMPOSITION = "PORTFOLIO_COMPOSITION"


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    source: str
    title: str
    url: HttpUrl
    published_at: Optional[datetime] = None


class LearnMore(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    title: str
    url: HttpUrl


class Insight(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    type: InsightType
    headline: str
    explanation: str
    personal_relevance: str
    learn_more: Optional[LearnMore] = None
    citations: list[Citation] = Field(default_factory=list)


class Audit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str
    providers_used: list[str]
    trace_id: str


class GenerateInsightsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str
    as_of: datetime
    insights: list[Insight]
    audit: Audit


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: str
    details: Optional[Any] = None




class UserBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    retirement_goal_date: Optional[date] = None
    preferred_notification_method: Optional[str] = None
    investment_experience_level: Optional[str] = None


class WealthSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of: datetime
    total_investable_assets: float
    checking_balance: float
    savings_balance: float
    brokerage_balance: float
    external_accounts_linked: int


class HoldingSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of: datetime
    name: str
    ticker: str
    category: str
    units: float
    current_market_value: float
    cost_basis: float
    dividend_reinvestment_enabled: bool
    recent_dividend_payments: float
    dividend_yield_pct: float


class GoalSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goal_type: str
    target_amount: float
    progress_pct: float
    estimated_goal_date: date


class ActivitySummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    last_login_at: datetime
    login_frequency_30d: int
    engagement_score: float
    inactivity_flag: bool


class Preferences(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preferred_insight_format: str


class PipelinePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user: UserBlock
    wealth_snapshot: WealthSnapshot
    holdings_snapshots: List[HoldingSnapshot]
    goals: List[GoalSnapshot]
    activity_summary: ActivitySummary
    preferences: Preferences
    activity_events: List[Dict[str, Any]]


class GenerateInsightsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    payload: PipelinePayload