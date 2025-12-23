#src/core/citations/validator.py
from __future__ import annotations

from core.schemas.insights import InsightSession


class CitationValidationError(ValueError):
    pass


def validate_session_citations(session: InsightSession) -> None:
    for ins in session.insights:
        if not ins.sources:
            raise CitationValidationError(f"Insight {ins.insight_id} has no citations.")
        for c in ins.sources:
            if not c.url:
                raise CitationValidationError(f"Insight {ins.insight_id} has citation with empty url.")
