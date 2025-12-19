from datetime import datetime, timezone

import pytest

from core.citations.validator import CitationValidationError, validate_session_citations
from core.schemas.citations import Citation, Provider
from core.schemas.insights import Insight, InsightSession


def test_validate_session_citations_pass():
    session = InsightSession(
        session_id="s1",
        user_id="u1",
        created_at=datetime.now(timezone.utc),
        insights=[
            Insight(
                insight_id="i1",
                headline="Headline",
                explanation="Two sentences here.",
                personal_relevance="Because you hold X.",
                sources=[
                    Citation(
                        citation_id="c1",
                        provider=Provider.benzinga,
                        title="Some title",
                        url="https://example.com",
                        published_at=None,
                        claim_ids=[],
                    )
                ],
            )
        ],
    )
    validate_session_citations(session)


def test_validate_session_citations_fails_on_missing_sources():
    session = InsightSession(
        session_id="s1",
        user_id="u1",
        created_at=datetime.now(timezone.utc),
        insights=[
            Insight(
                insight_id="i1",
                headline="Headline",
                explanation="Two sentences here.",
                personal_relevance="Because you hold X.",
                sources=[],
            )
        ],
    )
    with pytest.raises(CitationValidationError):
        validate_session_citations(session)


def test_validate_session_citations_fails_on_empty_url():
    session = InsightSession(
        session_id="s1",
        user_id="u1",
        created_at=datetime.now(timezone.utc),
        insights=[
            Insight(
                insight_id="i1",
                headline="Headline",
                explanation="Two sentences here.",
                personal_relevance="Because you hold X.",
                sources=[
                    Citation(
                        citation_id="c1",
                        provider=Provider.benzinga,
                        title="Some title",
                        url="",
                        published_at=None,
                        claim_ids=[],
                    )
                ],
            )
        ],
    )
    with pytest.raises(CitationValidationError):
        validate_session_citations(session)
