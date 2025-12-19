from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from core.schemas.citations import Citation, Provider


def assemble_basic_citations(*, sources: list[dict]) -> list[Citation]:
    """
    PoC-level citation assembly:
    - Converts provider items (news/market data) into Citation objects.
    - Claim mapping is added in later phases (Phase 5/6).
    """
    citations: list[Citation] = []
    for s in sources:
        citations.append(
            Citation(
                citation_id=str(uuid.uuid4()),
                provider=Provider(s.get("provider", "unknown")),
                title=s.get("title", "Source"),
                url=s.get("url", ""),
                published_at=_parse_dt(s.get("published_at")),
                quote_span=None,
                claim_ids=[],
            )
        )
    return citations


def _parse_dt(v: Any):
    if not v:
        return None
    if isinstance(v, datetime):
        return v
    try:
        return datetime.fromisoformat(str(v)).astimezone(timezone.utc)
    except Exception:
        return None
