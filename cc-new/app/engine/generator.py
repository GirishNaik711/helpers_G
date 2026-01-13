# app/engine/generator.py

from __future__ import annotations

import uuid
from typing import List

from app.api.schemas import (
    GenerateInsightsRequest,
    GenerateInsightsResponse,
    Insight,
    InsightType,
    Citation,
    Audit,
)
from app.core.config import settings
from app.core.safety import enforce_non_advisory_or_raise
from app.engine.normalize import normalize_pipeline_payload
from app.engine.signals import build_goal_portfolio_signals, build_market_trend_signals
from app.llm.registry import resolve_llm
from app.providers.base import ProviderRequest
from app.providers.registry import resolve_providers
import logging
logger = logging.getLogger("cc.generator")


def _safe_sample(text: str | None, n: int = 120) -> str:
    t = (text or "").replace("\n", " ").strip()
    return t[:n] + ("…" if len(t) > n else "")


def generate_insights(req: GenerateInsightsRequest) -> GenerateInsightsResponse:
    
    trace_id = f"trace_{uuid.uuid4()}"
    logger.info("[%s] generate_insights start customer_id=%s session_id=%s",
                trace_id, req.payload.user.customer_id, req.session_id)
    
    context = normalize_pipeline_payload(req.payload)
    
    logger.info("[%s] normalized context tickers=%s inactivity=%s goal_progress=%s",
            trace_id, context.get("tickers"), context.get("inactivity_flag"), context.get("goal_progress_pct"))


    provider_payloads = []
    providers = resolve_providers(settings.default_market_providers_list)

    preq = ProviderRequest(
        customer_id=context["customer_id"],
        as_of=req.payload.wealth_snapshot.as_of,
        context=context,
    )

    for provider in providers:
        status = provider.healthcheck()
        logger.info("[%s] provider=%s health ok=%s configured=%s msg=%s",
                    trace_id, provider.name, status.ok, status.configured, status.message)
        if not status.ok:
            continue
        try:
            resp = provider.fetch(preq)
            logger.info("[%s] provider=%s fetched items=%d citations=%d",
                        trace_id, provider.name, len(resp.items), len(resp.citations))
            if resp.items:
                first = resp.items[0]
                logger.info(
                    "[%s] provider=%s sample kind=%s title=%s summary=%s",
                    trace_id, provider.name, first.kind,
                    _safe_sample(first.title, 80),
                    _safe_sample(first.summary, 140),
                )
            provider_payloads.append(resp)
        except Exception:
            logger.info("[%s] providers_done ok_payloads=%d requested=%d",
            trace_id, len(provider_payloads), len(providers))

    
    bundles = [build_goal_portfolio_signals(context)]

    market_bundle = build_market_trend_signals(provider_payloads, context)
    if market_bundle:
        bundles.append(market_bundle)


    logger.info("[%s] llm_provider=%s bundles=%d", trace_id, settings.llm_provider, len(bundles))
    
    llm = resolve_llm(settings.llm_provider)
    insights: List[Insight] = []

    for bundle in bundles[: settings.insights_count]:
        try:
            realized = llm.realize(
                {
                    "facts": bundle.facts,
                    "allowed_claims": [],
                    "audience": "long-term investor",
                    "style": "educational exploration",
                }
            )
            logger.info(
            "[%s] llm=%s realized ok headline=%s",
            trace_id, llm.name, _safe_sample(realized.get("headline"), 120)
        )
        except Exception:
            logger.exception("[%s] llm.realize failed", trace_id)
            raise

        enforce_non_advisory_or_raise(
            [realized["headline"], realized["explanation"], realized["personal_relevance"]]
        )

        try:
            verdict = llm.judge(
                f'{realized["headline"]}\n{realized["explanation"]}\n{realized["personal_relevance"]}'
            )
            logger.info(
            "[%s] llm=%s judge verdict=%s reason=%s",
            trace_id, llm.name, verdict.get("verdict"), _safe_sample(verdict.get("reason"), 160)
        )

        except Exception:
            logger.exception("[%s] llm.judge failed", trace_id)
            raise
        
        if verdict.get("verdict") != "PASS":
            logger.warning("[%s] insight blocked by judge reason=%s", trace_id, verdict.get("reason"))
            continue
        

        insights.append(
            Insight(
                id=str(uuid.uuid4()),
                type=InsightType.GOAL_PROGRESS
                if bundle.kind == "goal_portfolio"
                else InsightType.MARKET_TREND,
                headline=realized["headline"],
                explanation=realized["explanation"],
                personal_relevance=realized["personal_relevance"],
                citations=[
                    Citation(
                        source=c.source,
                        title=c.title,
                        url=c.url,
                        published_at=c.published_at,
                    )
                    for c in (bundle.citations or [])
                ],
            )
        )

    return GenerateInsightsResponse(
        customer_id=req.payload.user.customer_id,
        as_of=req.payload.wealth_snapshot.as_of,
        insights=insights,
        audit=Audit(
            model=settings.llm_provider,
            providers_used=[p.name for p in providers],
            trace_id=trace_id,
        ),
    )
