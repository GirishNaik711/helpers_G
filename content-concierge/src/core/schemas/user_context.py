#core/schemas/user_context.py

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ExperienceLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    unknown = "unknown"


class NotificationMethod(str, Enum):
    email = "email"
    sms = "sms"
    push = "push"
    none = "none"
    unknown = "unknown"


class InsightFormat(str, Enum):
    text = "text"
    bullet = "bullet"
    audio = "audio"
    video = "video"
    unknown = "unknown"


class AccountProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(..., description="System identifier")
    full_name: str
    date_of_birth: Optional[date] = None
    retirement_goal_date: Optional[date] = None
    preferred_notification_method: NotificationMethod = NotificationMethod.unknown
    investment_experience_level: ExperienceLevel = ExperienceLevel.unknown


class WealthSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_investable_assets: Optional[float] = Field(
        default=None, description="Sum across linked accounts"
    )
    checking_balance: Optional[float] = None
    savings_balance: Optional[float] = None
    brokerage_balance: Optional[float] = None
    external_accounts_linked: int = 0


class AssetClassAllocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    equities_pct: float = 0.0
    fixed_income_pct: float = 0.0
    cash_pct: float = 0.0
    alternatives_pct: float = 0.0
    etfs_pct: float = 0.0
    mutual_funds_pct: float = 0.0

    def total_pct(self) -> float:
        return (
            self.equities_pct
            + self.fixed_income_pct
            + self.cash_pct
            + self.alternatives_pct
            + self.etfs_pct
            + self.mutual_funds_pct
        )


class HoldingCategory(str, Enum):
    domestic_stocks = "domestic_stocks"
    international_stocks = "international_stocks"
    us_treasuries = "us_treasuries"
    reits = "reits"
    corporate_bonds = "corporate_bonds"
    etf = "etf"
    mutual_fund = "mutual_fund"
    cash = "cash"
    other = "other"


class Holding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    ticker: Optional[str] = None
    category: HoldingCategory = HoldingCategory.other

    units: Optional[float] = None
    current_market_value: Optional[float] = None
    cost_basis: Optional[float] = None
    acquisition_date: Optional[date] = None

    dividend_reinvestment_enabled: Optional[bool] = None
    recent_dividend_payments: Optional[float] = None
    dividend_yield_pct: Optional[float] = None

    unrealized_gain_loss: Optional[float] = None


class Portfolio(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset_mix: AssetClassAllocation = Field(default_factory=AssetClassAllocation)
    holdings: list[Holding] = Field(default_factory=list)


class GoalType(str, Enum):
    retirement = "retirement"
    home_purchase = "home_purchase"
    education = "education"
    emergency_fund = "emergency_fund"
    other = "other"


class Goal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goal_type: GoalType
    target_amount: Optional[float] = None
    progress_pct: Optional[float] = Field(default=None, ge=0, le=100)
    estimated_goal_date: Optional[date] = None


class Goals(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goals: list[Goal] = Field(default_factory=list)
    contribution_schedule: Optional[str] = Field(
        default=None, description="Free-form for PoC; refine later"
    )


class ActivityHistory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    last_login_at: Optional[datetime] = None
    login_frequency_30d: Optional[int] = None
    latest_transactions: list[str] = Field(default_factory=list)
    recent_interactions: list[str] = Field(default_factory=list)
    engagement_score: Optional[float] = None
    inactivity_flag: bool = False


class Preferences(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preferred_insight_format: InsightFormat = InsightFormat.text
    prior_content_consumed: list[str] = Field(default_factory=list)
    insight_feedback: dict[str, int] = Field(
        default_factory=dict,
        description="insight_id -> feedback (-1/0/+1) for PoC",
    )


class UserContext(BaseModel):
    """
    Canonical user context used across Insights generation and Q&A.
    """

    model_config = ConfigDict(extra="forbid")

    profile: AccountProfile
    wealth: WealthSummary = Field(default_factory=WealthSummary)
    portfolio: Portfolio = Field(default_factory=Portfolio)
    goals: Goals = Field(default_factory=Goals)
    activity: ActivityHistory = Field(default_factory=ActivityHistory)
    preferences: Preferences = Field(default_factory=Preferences)