from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select

from data.relational.db import SessionLocal
from data.relational.models import (
    ActivityEvent,
    ActivitySummary,
    Goal,
    HoldingsSnapshot,
    Preference,
    User,
    WealthSnapshot,
)


def seed_customer(customer_id: str = "cust_001") -> None:
    now = datetime.now(timezone.utc)

    with SessionLocal() as session:
        # --- Upsert-ish guard: if user exists, do nothing (idempotent seed)
        existing = session.execute(select(User).where(User.customer_id == customer_id)).scalar_one_or_none()
        if existing:
            print(f"[seed] user {customer_id} already exists; skipping.")
            return

        user = User(
            customer_id=customer_id,
            full_name="Alex Johnson",
            date_of_birth=date(1975, 5, 12),
            retirement_goal_date=date(2032, 1, 1),
            preferred_notification_method="email",
            investment_experience_level="intermediate",
        )
        session.add(user)
        session.flush()

        wealth = WealthSnapshot(
            customer_id=customer_id,
            as_of=now,
            total_investable_assets=1_050_000,
            checking_balance=50_000,
            savings_balance=100_000,
            brokerage_balance=900_000,
            external_accounts_linked=1,
        )
        session.add(wealth)

        # Holdings snapshot: same as_of so "latest snapshot" query returns both
        holdings = [
            HoldingsSnapshot(
                customer_id=customer_id,
                as_of=now,
                name="Apple Inc.",
                ticker="AAPL",
                category="domestic_stocks",
                units=120,
                current_market_value=22_000,
                cost_basis=15_000,
                dividend_reinvestment_enabled=True,
                recent_dividend_payments=150,
                dividend_yield_pct=0.005,
            ),
            HoldingsSnapshot(
                customer_id=customer_id,
                as_of=now,
                name="Vanguard S&P 500 ETF",
                ticker="VOO",
                category="etf",
                units=300,
                current_market_value=135_000,
                cost_basis=110_000,
                dividend_reinvestment_enabled=True,
                recent_dividend_payments=400,
                dividend_yield_pct=0.013,
            ),
        ]
        session.add_all(holdings)

        goals = [
            Goal(
                customer_id=customer_id,
                goal_type="retirement",
                target_amount=1_800_000,
                progress_pct=71.0,
                estimated_goal_date=date(2032, 1, 1),
            )
        ]
        session.add_all(goals)

        activity_summary = ActivitySummary(
            customer_id=customer_id,
            last_login_at=now - timedelta(days=45),
            login_frequency_30d=1,
            engagement_score=0.20,
            inactivity_flag=True,
        )
        session.add(activity_summary)

        preferences = Preference(
            customer_id=customer_id,
            preferred_insight_format="text",
        )
        session.add(preferences)

        # Activity events (optional; useful later)
        events = [
            ActivityEvent(
                customer_id=customer_id,
                event_type="login",
                event_at=now - timedelta(days=45),
                event_metadata={"channel": "web"},
            ),
            ActivityEvent(
                customer_id=customer_id,
                event_type="content_view",
                event_at=now - timedelta(days=60),
                event_metadata={"content_id": "retirement_basics_101"},
            ),
        ]
        session.add_all(events)

        session.commit()
        print(f"[seed] inserted user + snapshots for {customer_id}")


if __name__ == "__main__":
    seed_customer()
