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
from app.core.safety import enforce_non_advisory_or_raise
from app.engine.normalize import normalize_pipeline_payload
from app.engine.signals import build_goal_portfolio_signals, build_market_trend_signals
from app.llm.registry import resolve_llm
from app.providers.base import ProviderRequest
from app.providers.registry import resolve_providers


def generate_insights(req: GenerateInsightsRequest) -> GenerateInsightsResponse:
    # ----------------------------
    # Normalize
    # ----------------------------
    context = normalize_pipeline_payload(req.payload)

    # ----------------------------
    # Providers (holdings-driven)
    # ----------------------------
    provider_payloads = []
    providers = resolve_providers(req.options.market_providers)

    preq = ProviderRequest(
        customer_id=context["customer_id"],
        as_of=req.payload.wealth_snapshot.as_of,
        context=context,
    )

    for provider in providers:
        status = provider.healthcheck()
        if not status.ok:
            continue
        provider_payloads.append(provider.fetch(preq))

    # ----------------------------
    # Build signal bundles (A+B)
    # ----------------------------
    bundles = [build_goal_portfolio_signals(context)]

    market_bundle = build_market_trend_signals(provider_payloads, context)
    if market_bundle:
        bundles.append(market_bundle)

    # ----------------------------
    # LLM realization (C)
    # ----------------------------
    llm = resolve_llm(req.options.llm_provider)
    insights: List[Insight] = []

    for bundle in bundles[: req.options.count]:
        realized = llm.realize(
            {
                "facts": bundle.facts,
                "allowed_claims": [],
                "audience": "long-term investor",
                "style": "educational exploration",
            }
        )

        enforce_non_advisory_or_raise(
            [realized["headline"], realized["explanation"], realized["personal_relevance"]]
        )

        verdict = llm.judge(
            f'{realized["headline"]}\n{realized["explanation"]}\n{realized["personal_relevance"]}'
        )
        if verdict.get("verdict") != "PASS":
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

    # ----------------------------
    # Response
    # ----------------------------
    return GenerateInsightsResponse(
        customer_id=req.payload.user.customer_id,
        as_of=req.payload.wealth_snapshot.as_of,
        insights=insights,
        audit=Audit(
            model=req.options.llm_provider,
            providers_used=[p.name for p in providers],
            trace_id=f"trace_{uuid.uuid4()}",
        ),
    )
