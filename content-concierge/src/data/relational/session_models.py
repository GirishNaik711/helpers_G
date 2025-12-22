from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from data.relational.base import Base


class InsightSessionRow(Base):
    __tablename__ = "insight_sessions"

    session_id: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Full serialized InsightSession
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
