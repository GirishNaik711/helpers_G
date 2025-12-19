from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db, get_llm
from api.routes.models import InsightsRequest
from core.agent.insights_flow import InsightsFlowDeps, run_insights_flow
from core.agent.insights_persists import persist_insight_session
from core.llm.types import LlmClient
from data.providers.market_data import MarketDataProvider
from data.providers.news import NewsAggregator
from data.providers.user_context import UserContextProvider
from data.relational.repo import RelationalRepo
from observability.logger import logger

router = APIRouter(tags=["insights"])


@router.post("/insights")
def generate_insights(req: InsightsRequest, db: Session = Depends(get_db), llm: LlmClient = Depends(get_llm)):
    try:
        rel_repo = RelationalRepo(db)
        user_ctx_provider = UserContextProvider(rel_repo)

        deps = InsightsFlowDeps(
            llm=llm,
            user_context_provider=user_ctx_provider,
            market_data_provider=MarketDataProvider(),
            news_provider=NewsAggregator(),
        )

        session = run_insights_flow(user_id=req.user_id, deps=deps)

        # Persist for follow-up Q&A
        persist_insight_session(db, session)

        return session.model_dump()
    except Exception as e:
        logger.error("api.insights.error", fields={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))
