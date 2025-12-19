from datetime import datetime, timezone

import api.routes.insights as insights_route
import api.routes.qa as qa_route

from core.schemas.citations import Citation, Provider
from core.schemas.insights import Insight, InsightSession
from core.schemas.qa import Answer


def test_post_insights_contract(client, monkeypatch):
    # Stub out flow + persistence inside route module
    def fake_run_insights_flow(*, user_id, deps):
        return InsightSession(
            session_id="sess_test",
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
            insights=[
                Insight(
                    insight_id="i1",
                    headline="Headline",
                    explanation="Two sentences here.",
                    personal_relevance="Because you hold VOO.",
                    sources=[
                        Citation(
                            citation_id="c1",
                            provider=Provider.benzinga,
                            title="News title",
                            url="https://example.com",
                            published_at=None,
                            claim_ids=[],
                        )
                    ],
                )
            ],
        )

    def fake_persist(db, session):
        return None

    monkeypatch.setattr(insights_route, "run_insights_flow", fake_run_insights_flow)
    monkeypatch.setattr(insights_route, "persist_insight_session", fake_persist)

    # Also avoid DI needing real DB/LLM by overriding dependencies
    import api.deps as deps

    def fake_get_db():
        yield object()

    def fake_get_llm():
        return object()

    client.app.dependency_overrides[deps.get_db] = fake_get_db
    client.app.dependency_overrides[deps.get_llm] = fake_get_llm

    r = client.post("/insights", json={"user_id": "cust_001"})
    assert r.status_code == 200
    data = r.json()

    assert data["session_id"] == "sess_test"
    assert data["user_id"] == "cust_001"
    assert isinstance(data["insights"], list) and len(data["insights"]) >= 1
    assert "headline" in data["insights"][0]
    assert "sources" in data["insights"][0]
    assert data["insights"][0]["sources"][0]["provider"] == "benzinga"

    client.app.dependency_overrides.clear()


def test_post_ask_contract(client, monkeypatch):
    def fake_run_qa_flow(*, session_id, question, conversation, deps):
        return Answer(
            answer_text="Educational answer.",
            direct_portfolio_relevance="Relevance text.",
            risks_and_considerations=["Risk 1"],
            citations=[
                Citation(
                    citation_id="c1",
                    provider=Provider.benzinga,
                    title="News title",
                    url="https://example.com",
                    published_at=None,
                    claim_ids=["c1"],
                )
            ],
            confidence="medium",
            disclaimer=None,
        )

    monkeypatch.setattr(qa_route, "run_qa_flow", fake_run_qa_flow)

    import api.deps as deps

    def fake_get_db():
        yield object()

    def fake_get_llm():
        return object()

    client.app.dependency_overrides[deps.get_db] = fake_get_db
    client.app.dependency_overrides[deps.get_llm] = fake_get_llm

    r = client.post("/sessions/sess_test/ask", json={"question": "What is this?", "conversation": []})
    assert r.status_code == 200
    data = r.json()

    assert "answer_text" in data
    assert "citations" in data
    assert data["citations"][0]["provider"] == "benzinga"

    client.app.dependency_overrides.clear()
