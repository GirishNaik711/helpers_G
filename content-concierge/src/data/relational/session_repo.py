from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.schemas.insights import InsightSession
from data.relational.session_models import InsightSessionRow


class InsightSessionRepo:
    def __init__(self, session: Session):
        self.session = session

    def save(self, insight_session: InsightSession) -> None:
        row = InsightSessionRow(
            session_id=insight_session.session_id,
            user_id=insight_session.user_id,
            created_at=insight_session.created_at,
            payload=insight_session.model_dump(),
        )
        self.session.add(row)
        self.session.commit()

    def get(self, session_id: str) -> InsightSession:
        stmt = select(InsightSessionRow).where(InsightSessionRow.session_id == session_id)
        row = self.session.execute(stmt).scalar_one()
        return InsightSession.model_validate(row.payload)
