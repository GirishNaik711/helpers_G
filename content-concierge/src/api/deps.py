from __future__ import annotations

from typing import Generator

from sqlalchemy.orm import Session

from core.llm.factory import get_llm_client
from data.relational.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_llm():
    return get_llm_client()
