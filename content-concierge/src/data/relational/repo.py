#data/relational/repo.py

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from data.relational.models import (
    ActivitySummary,
    Goal,
    HoldingsSnapshot,
    Preference,
    User,
    WealthSnapshot,
)


class RelationalRepo:
    def __init__(self, session: Session):
        self.session = session

    def get_user(self, customer_id: str) -> User:
        stmt = select(User).where(User.customer_id == customer_id)
        user = self.session.execute(stmt).scalar_one()
        return user

    def get_latest_wealth(self, customer_id: str) -> WealthSnapshot | None:
        stmt = (
            select(WealthSnapshot)
            .where(WealthSnapshot.customer_id == customer_id)
            .order_by(WealthSnapshot.as_of.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_latest_holdings(self, customer_id: str) -> list[HoldingsSnapshot]:
        # Latest as_of for this customer
        latest_as_of_stmt = (
            select(HoldingsSnapshot.as_of)
            .where(HoldingsSnapshot.customer_id == customer_id)
            .order_by(HoldingsSnapshot.as_of.desc())
            .limit(1)
        )
        latest_as_of = self.session.execute(latest_as_of_stmt).scalar_one_or_none()
        if latest_as_of is None:
            return []

        stmt = select(HoldingsSnapshot).where(
            HoldingsSnapshot.customer_id == customer_id,
            HoldingsSnapshot.as_of == latest_as_of,
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_goals(self, customer_id: str) -> list[Goal]:
        stmt = select(Goal).where(Goal.customer_id == customer_id)
        return list(self.session.execute(stmt).scalars().all())

    def get_activity_summary(self, customer_id: str) -> ActivitySummary | None:
        stmt = select(ActivitySummary).where(ActivitySummary.customer_id == customer_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_preferences(self, customer_id: str) -> Preference | None:
        stmt = select(Preference).where(Preference.customer_id == customer_id)
        return self.session.execute(stmt).scalar_one_or_none()
