from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.deps import get_db
from data.providers.user_context import UserContextProvider
from data.relational.repo import RelationalRepo

router = APIRouter(tags=["users"])


@router.get("/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    try:
        repo = RelationalRepo(db)
        provider = UserContextProvider(repo)
        user_context = provider.load(user_id)
        return user_context.model_dump()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/users/{user_id}/holdings")
def get_holdings(user_id: str, db: Session = Depends(get_db)):
    try:
        repo = RelationalRepo(db)
        provider = UserContextProvider(repo)
        uc = provider.load(user_id)
        return {"user_id": user_id, "holdings": [h.model_dump() for h in uc.portfolio.holdings]}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/users/{user_id}/goals")
def get_goals(user_id: str, db: Session = Depends(get_db)):
    try:
        repo = RelationalRepo(db)
        provider = UserContextProvider(repo)
        uc = provider.load(user_id)
        return {"user_id": user_id, "goals": [g.model_dump() for g in uc.goals.goals]}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
