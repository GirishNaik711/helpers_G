from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, TypedDict

from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from core.citations.qa_citations import (
    attach_claims_to_citations,
    pool_sources,
    validate_claims_have_sources,
)
from core.guardrails import check_non_prescriptive
from core.llm.types import LlmClient, LlmMessage
from core.prompts.qa import QA_SYNTHESIS_SYSTEM, QA_SYNTHESIS_USER
from core.prompts.router import ROUTER_SYSTEM, ROUTER_USER
from core.schemas.qa import Answer, Claim, Message, QAState
from core.schemas.routing import RetrievalPlan
from data.providers.internal_content import InternalContentProvider
from data.providers.market_data import MarketDataProvider
from data.providers.news import NewsAggregator
from data.providers.user_context import UserContextProvider
from data.relational.repo import RelationalRepo
from data.relational.session_repo import InsightSessionRepo
from observability.logger import logger


class QAFlowState(TypedDict, total=False):
    # inputs
    session_id: str
    question: str
    conversation: list[dict]  # raw messages from API later (role/content/created_at)
    user_id: str

    # loaded
    qa_state: QAState

    # outputs
    answer: Answer


@dataclass
class QAFlowDeps:
    llm: LlmClient
    db_session: Session
    user_context_provider: UserContextProvider
    market_data_provider: MarketDataProvider
    news_provider: NewsAggregator
    internal_provider: InternalContentProvider


def build_qa_graph(deps: QAFlowDeps):
    g = StateGraph(QAFlowState)

    g.add_node("load_session_context", lambda s: _load_session_context(s, deps))
    g.add_node("route", lambda s: _route(s, deps))
    g.add_node("retrieve", lambda s: _retrieve(s, deps))
    g.add_node("synthesize", lambda s: _synthesize(s, deps))
    g.add_node("citations_and_guardrails", lambda s: _citations_and_guardrails(s))
    g.add_node("finalize", lambda s: _finalize(s))

    g.set_entry_point("load_session_context")
    g.add_edge("load_session_context", "route")
    g.add_edge("route", "retrieve")
    g.add_edge("retrieve", "synthesize")
    g.add_edge("synthesize", "citations_and_guardrails")
    g.add_edge("citations_and_guardrails", "finalize")
    g.add_edge("finalize", END)

    return g.compile()


def run_qa_flow(*, session_id: str, question: str, conversation: list[dict], deps: QAFlowDeps) -> Answer:
    graph = build_qa_graph(deps)
    out = graph.invoke({"session_id": session_id, "question": question, "conversation": conversation})
    return out["answer"]


def _load_session_context(state: QAFlowState, deps: QAFlowDeps) -> dict:
    session_repo = InsightSessionRepo(deps.db_session)
    insight_session = session_repo.get(state["session_id"])

    # Load fresh user_context from DB for portfolio-aware follow-ups
    rel_repo = RelationalRepo(deps.db_session)
    user_ctx_provider = deps.user_context_provider

    user_id = insight_session.user_id
    user_context = user_ctx_provider.load(user_id)

    # conversation: keep last 6 messages
    msgs: list[Message] = []
    for m in (state.get("conversation") or [])[-6:]:
        # minimal validation
        try:
            msgs.append(Message.model_validate(m))
        except Exception:
            continue

    qa_state = QAState(
        session_id=insight_session.session_id,
        user_id=user_id,
        user_context=user_context,
        insights_context=insight_session.insights,
        conversation=msgs,
    )

    logger.info("qa.load_session_context", fields={"session_id": insight_session.session_id, "user_id": user_id})
    return {"qa_state": qa_state, "user_id": user_id}


def _route(state: QAFlowState, deps: QAFlowDeps) -> dict:
    qa_state: QAState = state["qa_state"]

    insight_headlines = [i.headline for i in qa_state.insights_context]
    known_tickers = sorted({h.ticker for h in qa_state.user_context.portfolio.holdings if h.ticker})
    known_holdings = [h.name for h in qa_state.user_context.portfolio.holdings[:10]]

    prompt = ROUTER_USER.format(
        question=state["question"],
        last_6_messages=[m.model_dump() for m in qa_state.conversation],
        insight_headlines=insight_headlines,
        known_portfolio_entities={"tickers": known_tickers, "holdings": known_holdings},
        approved_sources=["mt_newswires", "benzinga", "market_data_api", "connect_coach"],
    )

    resp = deps.llm.generate(
        messages=[
            LlmMessage(role="system", content=ROUTER_SYSTEM),
            LlmMessage(role="user", content=prompt),
        ],
        temperature=0.0,
    )

    plan = RetrievalPlan.model_validate(_safe_json(resp.text))
    qa_state.retrieval_plan = plan
    logger.info("qa.route", fields={"need_news": plan.need_news, "need_market_data": plan.need_market_data, "need_internal": plan.need_internal_content})
    return {"qa_state": qa_state}


def _retrieve(state: QAFlowState, deps: QAFlowDeps) -> dict:
    qa_state: QAState = state["qa_state"]
    plan = qa_state.retrieval_plan
    if not plan:
        return {"qa_state": qa_state}

    tickers = plan.entities.tickers
    if not tickers:
        # fall back to portfolio tickers for portfolio_relation intent
        if any(i.value == "portfolio_relation" for i in plan.intents):
            tickers = sorted({h.ticker for h in qa_state.user_context.portfolio.holdings if h.ticker})

    # tool_context
    if plan.need_market_data and tickers:
        qa_state.tool_context.market_data = deps.market_data_provider.get_snapshot(tickers)

    if plan.need_news:
        query = state["question"]
        qa_state.tool_context.news_items = deps.news_provider.search(query=query, tickers=tickers, limit=plan.max_news_items)

    if plan.need_internal_content:
        qa_state.tool_context.internal_content = deps.internal_provider.search(query=state["question"], limit=plan.max_internal_items)

    logger.info("qa.retrieve", fields={"news": len(qa_state.tool_context.news_items), "market": bool(qa_state.tool_context.market_data), "internal": len(qa_state.tool_context.internal_content)})
    return {"qa_state": qa_state}


def _synthesize(state: QAFlowState, deps: QAFlowDeps) -> dict:
    qa_state: QAState = state["qa_state"]

    prompt = QA_SYNTHESIS_USER.format(
        question=state["question"],
        user_context=qa_state.user_context.model_dump(),
        insights_context=[i.model_dump() for i in qa_state.insights_context],
        tool_context=qa_state.tool_context.model_dump(),
    )

    resp = deps.llm.generate(
        messages=[
            LlmMessage(role="system", content=QA_SYNTHESIS_SYSTEM),
            LlmMessage(role="user", content=prompt),
        ],
        temperature=0.0,
    )

    data = _safe_json(resp.text)

    claims = []
    for c in data.get("claims") or []:
        try:
            claims.append(Claim.model_validate(c))
        except Exception:
            continue

    qa_state.claims = claims
    qa_state.draft_answer = data.get("answer_text", "")

    # Build Answer shell; citations added in next node
    ans = Answer(
        answer_text=data.get("answer_text", ""),
        direct_portfolio_relevance=data.get("direct_portfolio_relevance"),
        risks_and_considerations=data.get("risks_and_considerations") or [],
        citations=[],
        confidence=data.get("confidence", "medium"),
        disclaimer=data.get("disclaimer"),
    )
    qa_state.final_answer = ans

    return {"qa_state": qa_state}


def _citations_and_guardrails(state: QAFlowState) -> dict:
    qa_state: QAState = state["qa_state"]
    ans = qa_state.final_answer
    if not ans:
        raise ValueError("Missing synthesized answer")

    # Guardrail: non-prescriptive
    gr = check_non_prescriptive(" ".join([ans.answer_text or "", ans.direct_portfolio_relevance or "", " ".join(ans.risks_and_considerations)]))
    if not gr.ok:
        raise ValueError(f"Guardrail violation: {gr.reasons}")

    # Pool citations: insight citations + tool outputs
    insight_citations = []
    for ins in qa_state.insights_context:
        insight_citations.extend(ins.sources or [])

    pooled = pool_sources(
        insight_citations=insight_citations,
        tool_news=qa_state.tool_context.news_items,
        tool_market=qa_state.tool_context.market_data,
        tool_internal=qa_state.tool_context.internal_content,
    )
    pooled = attach_claims_to_citations(citations=pooled, claims=qa_state.claims)

    # Validate: if any claim requires citation, ensure we have at least one
    validate_claims_have_sources(claims=qa_state.claims, citations=pooled)

    ans.citations = pooled
    qa_state.final_answer = ans
    return {"qa_state": qa_state}


def _finalize(state: QAFlowState) -> dict:
    qa_state: QAState = state["qa_state"]
    if not qa_state.final_answer:
        raise ValueError("No final answer")
    logger.info("qa.finalize", fields={"session_id": qa_state.session_id, "citations": len(qa_state.final_answer.citations), "claims": len(qa_state.claims)})
    return {"answer": qa_state.final_answer}


def _safe_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except Exception:
                return {}
        return {}
