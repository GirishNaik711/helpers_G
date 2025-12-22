from __future__ import annotations

from sqlalchemy.orm import Session

from core.schemas.insights import InsightSession
from data.relational.session_repo import InsightSessionRepo


def persist_insight_session(db: Session, insight_session: InsightSession) -> None:
    InsightSessionRepo(db).save(insight_session)
