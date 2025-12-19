from datetime import datetime, timezone

from core.agent.qa_flow import QAFlowDeps, run_qa_flow
from core.llm.factory import get_llm_client
from data.providers.internal_content import InternalContentProvider
from data.providers.market_data import MarketDataProvider
from data.providers.news import NewsAggregator
from data.providers.user_context import UserContextProvider
from data.relational.db import SessionLocal
from data.relational.repo import RelationalRepo
from data.relational.session_repo import InsightSessionRepo


def main():
    llm = get_llm_client()

    with SessionLocal() as db:
        # Ensure you already saved an InsightSession row for session_id below
        session_id = input("Enter existing insight session_id: ").strip()

        repo = RelationalRepo(db)
        user_ctx = UserContextProvider(repo)

        deps = QAFlowDeps(
            llm=llm,
            db_session=db,
            user_context_provider=user_ctx,
            market_data_provider=MarketDataProvider(),
            news_provider=NewsAggregator(),
            internal_provider=InternalContentProvider(),
        )

        conversation = [
            {"role": "user", "content": "What does this mean for me?", "created_at": datetime.now(timezone.utc).isoformat()}
        ]

        ans = run_qa_flow(session_id=session_id, question="How does AAPL relate to my portfolio risk?", conversation=conversation, deps=deps)
        print(ans.model_dump())


if __name__ == "__main__":
    main()
