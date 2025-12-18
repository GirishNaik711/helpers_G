from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data.relational.base import Base


class User(Base):
    __tablename__ = "users"

    customer_id: Mapped[str] = mapped_column(Text, primary_key=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    retirement_goal_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    preferred_notification_method: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    investment_experience_level: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    wealth_snapshots: Mapped[list["WealthSnapshot"]] = relationship(back_populates="user")
    holdings_snapshots: Mapped[list["HoldingsSnapshot"]] = relationship(back_populates="user")
    goals: Mapped[list["Goal"]] = relationship(back_populates="user")
    activity_summary: Mapped["ActivitySummary | None"] = relationship(back_populates="user")
    preferences: Mapped["Preference | None"] = relationship(back_populates="user")


class WealthSnapshot(Base):
    __tablename__ = "wealth_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[str] = mapped_column(ForeignKey("users.customer_id", ondelete="CASCADE"), nullable=False)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    total_investable_assets: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    checking_balance: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    savings_balance: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    brokerage_balance: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    external_accounts_linked: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user: Mapped["User"] = relationship(back_populates="wealth_snapshots")


Index("ix_wealth_customer_asof", WealthSnapshot.customer_id, WealthSnapshot.as_of.desc())


class HoldingsSnapshot(Base):
    __tablename__ = "holdings_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[str] = mapped_column(ForeignKey("users.customer_id", ondelete="CASCADE"), nullable=False)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    name: Mapped[str] = mapped_column(Text, nullable=False)
    ticker: Mapped[str | None] = mapped_column(String(16), nullable=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="other")

    units: Mapped[float | None] = mapped_column(Numeric(20, 6), nullable=True)
    current_market_value: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    cost_basis: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)

    dividend_reinvestment_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    recent_dividend_payments: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    dividend_yield_pct: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)

    user: Mapped["User"] = relationship(back_populates="holdings_snapshots")


Index("ix_holdings_customer_asof", HoldingsSnapshot.customer_id, HoldingsSnapshot.as_of.desc())
Index("ix_holdings_ticker", HoldingsSnapshot.ticker)


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[str] = mapped_column(ForeignKey("users.customer_id", ondelete="CASCADE"), nullable=False)

    goal_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_amount: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    progress_pct: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    estimated_goal_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    user: Mapped["User"] = relationship(back_populates="goals")


class ActivityEvent(Base):
    __tablename__ = "activity_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[str] = mapped_column(ForeignKey("users.customer_id", ondelete="CASCADE"), nullable=False)

    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    event_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    event_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


Index("ix_activity_customer_eventat", ActivityEvent.customer_id, ActivityEvent.event_at.desc())


class ActivitySummary(Base):
    __tablename__ = "activity_summary"

    customer_id: Mapped[str] = mapped_column(ForeignKey("users.customer_id", ondelete="CASCADE"), primary_key=True)

    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    login_frequency_30d: Mapped[int | None] = mapped_column(Integer, nullable=True)
    engagement_score: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    inactivity_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user: Mapped["User"] = relationship(back_populates="activity_summary")


class Preference(Base):
    __tablename__ = "preferences"

    customer_id: Mapped[str] = mapped_column(ForeignKey("users.customer_id", ondelete="CASCADE"), primary_key=True)
    preferred_insight_format: Mapped[str] = mapped_column(String(32), nullable=False, default="text")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="preferences")


class ContentConsumption(Base):
    __tablename__ = "content_consumption"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[str] = mapped_column(ForeignKey("users.customer_id", ondelete="CASCADE"), nullable=False)

    content_id: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False, default="unknown")
    consumed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


Index("ix_consumption_customer_time", ContentConsumption.customer_id, ContentConsumption.consumed_at.desc())


class InsightFeedback(Base):
    __tablename__ = "insight_feedback"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[str] = mapped_column(ForeignKey("users.customer_id", ondelete="CASCADE"), nullable=False)

    insight_id: Mapped[str] = mapped_column(Text, nullable=False)
    feedback: Mapped[int] = mapped_column(Integer, nullable=False)  # -1, 0, +1
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
