from __future__ import annotations

import uuid
from typing import Iterable

from core.schemas.citations import Citation, Provider
from core.schemas.qa import Claim


def pool_sources(*, insight_citations: list[Citation], tool_news: list[dict], tool_market: dict, tool_internal: list[dict]) -> list[Citation]:
    pooled: list[Citation] = []
    pooled.extend(insight_citations)

    # news
    for it in tool_news:
        url = it.get("url") or ""
        if not url:
            continue
        pooled.append(
            Citation(
                citation_id=str(uuid.uuid4()),
                provider=Provider(it.get("provider", "unknown")),
                title=it.get("title", "News"),
                url=url,
                published_at=_dt(it.get("published_at")),
                quote_span=None,
                claim_ids=[],
            )
        )

    # market data (one synthetic citation for the snapshot call)
    if tool_market:
        pooled.append(
            Citation(
                citation_id=str(uuid.uuid4()),
                provider=Provider.market_data_api,
                title="Market data snapshot",
                url="market_data://snapshot",
                published_at=None,
                quote_span=None,
                claim_ids=[],
            )
        )

    # internal
    for it in tool_internal:
        url = it.get("url") or ""
        if not url:
            continue
        pooled.append(
            Citation(
                citation_id=str(uuid.uuid4()),
                provider=Provider.connect_coach,
                title=it.get("title", "Internal content"),
                url=url,
                published_at=_dt(it.get("published_at")),
                quote_span=None,
                claim_ids=[],
            )
        )

    return pooled


def attach_claims_to_citations(*, citations: list[Citation], claims: Iterable[Claim]) -> list[Citation]:
    """
    PoC mapping:
    - If there are any requires_citation claims, attach all such claim_ids to all citations.
    Later phases can do fine-grained mapping.
    """
    claim_ids = [c.claim_id for c in claims if c.requires_citation]
    if not claim_ids:
        return citations
    for cit in citations:
        cit.claim_ids = sorted(set(cit.claim_ids + claim_ids))
    return citations


def validate_claims_have_sources(*, claims: Iterable[Claim], citations: list[Citation]) -> None:
    has_any = len(citations) > 0
    for c in claims:
        if c.requires_citation and not has_any:
            raise ValueError(f"Claim {c.claim_id} requires citation but no citations available.")


def _dt(v):
    if not v:
        return None
    try:
        from datetime import datetime
        return datetime.fromisoformat(str(v))
    except Exception:
        return None
