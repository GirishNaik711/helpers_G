from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, TypedDict


from langgraph.graph import StateGraph, END

from core.citations.assembler import assemble_basic_citations
from core.citations.validator import validate_session_citations
from core.guardrails import check_non_prescriptive, require_citations_for_external_claims
from core.llm.types import LlmClient, LlmMessage
from core.prompts.insights import (
    INSIGHT_HYPOTHESIS_SYSTEM,
    INSIGHT_HYPOTHESIS_USER,
    INSIGHT_SYNTHESIS_SYSTEM,
    INSIGHT_SYNTHESIS_USER,
)
from core.schemas.insights import Insight, InsightSession
from core.schemas.user_context import UserContext
from data.providers.market_data import MarketDataProvider
from data.providers.news import NewsAggregator
from data.providers.user_context import UserContextProvider
from observability.logger import logger


class InsightsState(TypedDict, total=False):
    user_id: str
    user_context: UserContext

    themes: list[str]

    market_data: dict
    news_items: list[dict]

    insight_drafts: list[dict]
    final_session: InsightSession


@dataclass
class InsightsFlowDeps:
    llm: LlmClient
    user_context_provider: UserContextProvider
    market_data_provider: MarketDataProvider
    news_provider: NewsAggregator


def build_insights_graph(deps: InsightsFlowDeps):
    g = StateGraph(InsightsState)

    g.add_node("load_user_context", lambda s: _load_user_context(s, deps))
    g.add_node("hypothesize_themes", lambda s: _hypothesize_themes(s, deps))
    g.add_node("retrieve_market_and_news", lambda s: _retrieve_market_and_news(s, deps))
    g.add_node("synthesize_insights", lambda s: _synthesize_insights(s, deps))
    g.add_node("validate_and_package", lambda s: _validate_and_package(s))

    g.set_entry_point("load_user_context")
    g.add_edge("load_user_context", "hypothesize_themes")
    g.add_edge("hypothesize_themes", "retrieve_market_and_news")
    g.add_edge("retrieve_market_and_news", "synthesize_insights")
    g.add_edge("synthesize_insights", "validate_and_package")
    g.add_edge("validate_and_package", END)

    return g.compile()


def run_insights_flow(*, user_id: str, deps: InsightsFlowDeps) -> InsightSession:
    graph = build_insights_graph(deps)
    out = graph.invoke({"user_id": user_id})
    return out["final_session"]


def _load_user_context(state: InsightsState, deps: InsightsFlowDeps) -> dict:
    user_id = state["user_id"]
    uc = deps.user_context_provider.load(user_id)
    logger.info("insights.load_user_context", fields={"user_id": user_id})
    return {"user_context": uc}

def _hypothesize_themes(state: InsightsState, deps: InsightsFlowDeps) -> dict:
    uc = state["user_context"]
    tickers = [h.ticker for h in uc.portfolio.holdings if h.ticker]
    top_holdings = [h.name for h in uc.portfolio.holdings[:5]]
    goal_types = [g.goal_type for g in uc.goals.goals]
    inactive = uc.activity.inactivity_flag

    prompt = INSIGHT_HYPOTHESIS_USER.format(
        tickers=tickers,
        top_holdings=top_holdings,
        goal_types=goal_types,
        inactive=inactive,
    )
    resp = deps.llm.generate(
        messages=[
            LlmMessage(role="system", content=INSIGHT_HYPOTHESIS_SYSTEM),
            LlmMessage(role="user", content=prompt),
        ],
        temperature=0.0,
    )

    themes = _safe_json(resp.text).get("themes") or []
    themes = [t.strip() for t in themes if isinstance(t, str) and t.strip()]
    logger.info("insights.hypothesize_themes", fields={"themes_count": len(themes)})
    return {"themes": themes}


def _retrieve_market_and_news(state: InsightsState, deps: InsightsFlowDeps) -> dict:
    uc = state["user_context"]
    tickers = sorted({h.ticker for h in uc.portfolio.holdings if h.ticker})

    market_data = deps.market_data_provider.get_snapshot(tickers)
    # Use themes as search query signal
    query = " ".join(state.get("themes", [])[:3]) or "portfolio update"
    news_items = deps.news_provider.search(query=query, tickers=tickers, limit=5)

    logger.info(
        "insights.retrieve_market_and_news",
        fields={"tickers": tickers, "news_items": len(news_items)},
    )
    return {"market_data": market_data, "news_items": news_items}


def _synthesize_insights(state: InsightsState, deps: InsightsFlowDeps) -> dict:
    uc = state["user_context"]

    prompt = INSIGHT_SYNTHESIS_USER.format(
        user_context=uc.model_dump(),
        market_data=state.get("market_data", {}),
        news_items=state.get("news_items", []),
    )

    resp = deps.llm.generate(
        messages=[
            LlmMessage(role="system", content=INSIGHT_SYNTHESIS_SYSTEM),
            LlmMessage(role="user", content=prompt),
        ],
        temperature=0.0,
    )
    drafts = _safe_json(resp.text).get("insights") or []
    drafts = [d for d in drafts if isinstance(d, dict)]
    logger.info("insights.synthesize_insights", fields={"drafts": len(drafts)})
    return {"insight_drafts": drafts}


def _validate_and_package(state: InsightsState) -> dict:
    user_id = state["user_id"]
    drafts = state.get("insight_drafts", [])
    # citations: attach minimal citations from retrieved sources
    source_pool = []
    for item in state.get("news_items", []):
        if item.get("url"):
            source_pool.append(
                {
                    "provider": item.get("provider", "unknown"),
                    "title": item.get("title", "News"),
                    "url": item.get("url", ""),
                    "published_at": item.get("published_at"),
                }
            )

    citations = assemble_basic_citations(sources=source_pool)

    insights: list[Insight] = []
    for d in drafts[:3]:
        headline = (d.get("headline") or "").strip()
        explanation = (d.get("explanation") or "").strip()
        relevance = (d.get("personal_relevance") or "").strip()

        # Guardrail: non-prescriptive language
        gr = check_non_prescriptive(" ".join([headline, explanation, relevance]))
        if not gr.ok:
            raise ValueError(f"Guardrail violation: {gr.reasons}")

        insights.append(
            Insight(
                insight_id=str(uuid.uuid4()),
                headline=headline,
                explanation=explanation,
                personal_relevance=relevance,
                sources=citations[:2] if citations else [],
            )
        )

    # Guardrail: require at least 1 source per insight
    gr2 = require_citations_for_external_claims([i.model_dump() for i in insights])
    if not gr2.ok:
        raise ValueError(f"Citation guardrail failed: {gr2.reasons}")

    session = InsightSession(
        session_id=str(uuid.uuid4()),
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        insights=insights,
    )

    validate_session_citations(session)
    logger.info("insights.session_ready", fields={"session_id": session.session_id, "insights": len(insights)})

    return {"final_session": session}


def _safe_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        # If model returns accidental prose, try to extract JSON block quickly
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except Exception:
                return {}
        return {}
