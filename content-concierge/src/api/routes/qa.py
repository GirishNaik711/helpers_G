from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db, get_llm
from api.routes.models import AskRequest
from core.agent.qa_flow import QAFlowDeps, run_qa_flow
from core.llm.types import LlmClient
from data.providers.internal_content import InternalContentProvider
from data.providers.market_data import MarketDataProvider
from data.providers.news import NewsAggregator
from data.providers.user_context import UserContextProvider
from data.relational.repo import RelationalRepo
from observability.logger import logger

router = APIRouter(tags=["qa"])


@router.post("/sessions/{session_id}/ask")
def ask(session_id: str, req: AskRequest, db: Session = Depends(get_db), llm: LlmClient = Depends(get_llm)):
    try:
        rel_repo = RelationalRepo(db)
        user_ctx_provider = UserContextProvider(rel_repo)

        deps = QAFlowDeps(
            llm=llm,
            db_session=db,
            user_context_provider=user_ctx_provider,
            market_data_provider=MarketDataProvider(),
            news_provider=NewsAggregator(),
            internal_provider=InternalContentProvider(),
        )

        ans = run_qa_flow(
            session_id=session_id,
            question=req.question,
            conversation=req.conversation,
            deps=deps,
        )
        return ans.model_dump()
    except Exception as e:
        logger.error("api.qa.error", fields={"session_id": session_id, "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))
