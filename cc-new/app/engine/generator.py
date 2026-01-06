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
from app.engine.candidates import build_candidates
from app.llm.registry import resolve_llm
from app.providers.base import ProviderRequest
from app.providers.registry import resolve_providers


def generate_insights(req: GenerateInsightsRequest) -> GenerateInsightsResponse:
    """
    Pipeline Payload -> Normalize -> Providers -> Facts -> LLM -> Insights
    Both goal and market insights are LLM-written.
    """

    context = normalize_pipeline_payload(req.payload)

    llm = resolve_llm(req.options.llm_provider)
    insights: List[Insight] = []

    if context.get("goal_progress_pct") is not None:
        goal_facts = [
            f"The user is {context['goal_progress_pct']:.0f}% of the way toward their retirement goal.",
        ]

        if context.get("retirement_goal_year"):
            goal_facts.append(
                f"The retirement goal year is {context['retirement_goal_year']}."
            )

        realized = llm.realize(
            {
                "facts": goal_facts,
                "allowed_claims": [],
                "audience": "long-term investor",
                "style": "educational exploration",
            }
        )

        enforce_non_advisory_or_raise(
            [
                realized["headline"],
                realized["explanation"],
                realized["personal_relevance"],
            ]
        )

        verdict = llm.judge(
            f'{realized["headline"]}\n'
            f'{realized["explanation"]}\n'
            f'{realized["personal_relevance"]}'
        )
        if verdict.get("verdict") == "PASS":
            insights.append(
                Insight(
                    id=str(uuid.uuid4()),
                    type=InsightType.GOAL_PROGRESS,
                    headline=realized["headline"],
                    explanation=realized["explanation"],
                    personal_relevance=realized["personal_relevance"],
                    citations=[],
                )
            )

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

    candidates = build_candidates(provider_payloads)

    for cand in candidates:
        if len(insights) >= req.options.count:
            break

        realized = llm.realize(
            {
                "facts": cand["facts"],
                "allowed_claims": cand.get("allowed_claims", []),
                "audience": "long-term investor",
                "style": "educational exploration",
            }
        )

        enforce_non_advisory_or_raise(
            [
                realized["headline"],
                realized["explanation"],
                realized["personal_relevance"],
            ]
        )

        verdict = llm.judge(
            f'{realized["headline"]}\n'
            f'{realized["explanation"]}\n'
            f'{realized["personal_relevance"]}'
        )
        if verdict.get("verdict") != "PASS":
            continue

        insights.append(
            Insight(
                id=str(uuid.uuid4()),
                type=InsightType.MARKET_TREND,
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
                    for c in cand["citations"]
                ],
            )
        )

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
