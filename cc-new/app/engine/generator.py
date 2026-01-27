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
    InsightScope
)
from app.engine.signals import (
    build_goal_portfolio_signals,
    build_market_trend_signals,
    build_positions_ticker_signals,
    build_performance_signals,
    build_inactive_activation_signals,
    build_everyday_performance_signals,
    build_everyday_positions_signals,
    build_advanced_performance_signals,
    build_advanced_positions_signals
)

from app.core.config import settings
from app.core.safety import enforce_non_advisory_or_raise
from app.engine.normalize import normalize_pipeline_payload
from app.llm.registry import resolve_llm
from app.providers.base import ProviderRequest
from app.providers.registry import resolve_providers
import logging
logger = logging.getLogger("cc.generator")


def _safe_sample(text: str | None, n: int = 120) -> str:
    t = (text or "").replace("\n", " ").strip()
    return t[:n] + ("…" if len(t) > n else "")

def plan_bundles(context, rc, provider_payloads):
    arch = (context.get("archetype") or "").strip().upper()
    # Dashboard: portfolio + optional market
    if rc.placement.value == "INVESTMENT_DASHBOARD":
        bundles = []
        if arch  == "INACTIVE":
            bundles.append(build_inactive_activation_signals(context))
        bundles.append(build_goal_portfolio_signals(context))
        mb = build_market_trend_signals(provider_payloads, context)
        if mb:
            bundles.append(mb)
        return bundles

    # Positions: ticker-focused if possible, else fallback to dashboard-style
    if rc.placement.value == "POSITIONS":
        bundles = []

        if arch == "ADVANCED":
            bundles.append(build_advanced_positions_signals(context, rc.focus_ticker))
        # everyday educational overlay
        if arch  == "EVERYDAY":
            bundles.append(build_everyday_positions_signals(context, rc.focus_ticker))

        # ticker-specific context when available
        if rc.focus_ticker:
            tb = build_positions_ticker_signals(provider_payloads, context, rc.focus_ticker)
            if tb:
                bundles.append(tb)

        # fallback if nothing else
        if not bundles:
            bundles.append(build_goal_portfolio_signals(context))
            mb = build_market_trend_signals(provider_payloads, context)
            if mb:
                bundles.append(mb)

        return bundles

            

    if rc.placement.value == "PERFORMANCE":
        bundles = []
        if arch == "ADVANCED":
            bundles.append(build_advanced_performance_signals(context))
        elif arch == "EVERYDAY":
            bundles.append(build_everyday_performance_signals(context))
        else:
            bundles.append(build_performance_signals(context))

        mb = build_market_trend_signals(provider_payloads, context)
        if mb:
            bundles.append(mb)
        return bundles



    # default fallback
    return [build_goal_portfolio_signals(context)]

    
def generate_insights(req: GenerateInsightsRequest) -> GenerateInsightsResponse:
    rc = req.request_context

    trace_id = f"trace_{uuid.uuid4()}"
    logger.info(
        "[%s] generate_insights start customer_id=%s session_id=%s",
        trace_id,
        req.payload.user.customer_id,
        req.session_id,
    )

    context = normalize_pipeline_payload(req.payload)
    
    arch = (context.get("archetype") or "").strip().upper()
    logger.info("[%s] archetype=%s tier=%s", trace_id, arch, context.get("tier"))

    logger.info(
        "[%s] normalized context tickers=%s inactivity=%s goal_progress=%s",
        trace_id,
        context.get("tickers"),
        context.get("inactivity_flag"),
        context.get("goal_progress_pct"),
    )

    provider_payloads = []
    providers = resolve_providers(settings.default_market_providers_list)

    preq = ProviderRequest(
        customer_id=context["customer_id"],
        as_of=req.payload.wealth_snapshot.as_of,
        context=context,
    )

    for provider in providers:
        status = provider.healthcheck()
        logger.info(
            "[%s] provider=%s health ok=%s configured=%s msg=%s",
            trace_id,
            provider.name,
            status.ok,
            status.configured,
            status.message,
        )

        if not status.ok:
            continue

        try:
            resp = provider.fetch(preq)
            logger.info(
                "[%s] provider=%s fetched items=%d citations=%d",
                trace_id,
                provider.name,
                len(resp.items),
                len(resp.citations),
            )

            if resp.items:
                first = resp.items[0]
                logger.info(
                    "[%s] provider=%s sample kind=%s title=%s summary=%s",
                    trace_id,
                    provider.name,
                    first.kind,
                    _safe_sample(first.title, 80),
                    _safe_sample(first.summary, 140),
                )

            provider_payloads.append(resp)

        except Exception:
            logger.info(
                "[%s] providers_done ok_payloads=%d requested=%d",
                trace_id,
                len(provider_payloads),
                len(providers),
            )

    bundles = plan_bundles(context, rc, provider_payloads)

    logger.info(
        "[%s] llm_provider=%s bundles=%d",
        trace_id,
        settings.llm_provider,
        len(bundles),
    )

    llm = resolve_llm(settings.llm_provider)
    insights: List[Insight] = []

    for bundle in bundles[: settings.insights_count]:
        logger.info(
            "[%s] bundle kind=%s facts=%d",
            trace_id,
            bundle.kind,
            len(bundle.facts),
        )

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
                "[%s] realized keys=%s headline=%s",
                trace_id,
                list(realized.keys()),
                _safe_sample(realized.get("headline"), 120),
            )

            if realized.get("headline") in (rc.recent_headlines or []):
                logger.info("[%s] skipped repeated headline", trace_id)
                continue

        except Exception:
            logger.exception("[%s] llm.realize failed", trace_id)
            raise

        enforce_non_advisory_or_raise(
            [
                realized["headline"],
                realized["explanation"],
                realized["personal_relevance"],
            ]
        )

        try:
            verdict = llm.judge(
                f'{realized["headline"]}\n'
                f'{realized["explanation"]}\n'
                f'{realized["personal_relevance"]}'
            )

            logger.info(
                "[%s] llm=%s judge verdict=%s reason=%s",
                trace_id,
                llm.name,
                verdict.get("verdict"),
                _safe_sample(verdict.get("reason"), 160),
            )

        except Exception:
            logger.exception("[%s] llm.judge failed", trace_id)
            raise

        if verdict.get("verdict") != "PASS":
            logger.warning(
                "[%s] insight blocked by judge reason=%s",
                trace_id,
                verdict.get("reason"),
            )
            continue

        scope = (
            InsightScope.TICKER
            if rc.placement.value == "POSITIONS" and rc.focus_ticker
            else InsightScope.PORTFOLIO
        )

        kind_to_type = {
            "goal_portfolio": InsightType.GOAL_PROGRESS,
            "market_trend": InsightType.MARKET_TREND,
            "positions_ticker": InsightType.MARKET_TREND,
            "performance": InsightType.PORTFOLIO_COMPOSITION,
            "inactive_activation": InsightType.PORTFOLIO_COMPOSITION,
            "everyday_performance": InsightType.PORTFOLIO_COMPOSITION,
            "everyday_positions": InsightType.PORTFOLIO_COMPOSITION,
            "advanced_performance": InsightType.PORTFOLIO_COMPOSITION,
            "advanced_positions": InsightType.PORTFOLIO_COMPOSITION,

        }
        
        insight_type = kind_to_type.get(bundle.kind, InsightType.MARKET_TREND)
        
        insights.append(
            Insight(
                id=str(uuid.uuid4()),
                type=insight_type,
                headline=realized["headline"],
                explanation=realized["explanation"],
                personal_relevance=realized["personal_relevance"],
                placement=rc.placement,
                trigger=rc.trigger,
                scope=scope,
                ticker=rc.focus_ticker if scope == InsightScope.TICKER else None,
                priority=len(insights),
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

