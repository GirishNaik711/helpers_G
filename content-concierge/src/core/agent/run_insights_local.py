from sqlalchemy.orm import Session

from core.agent.insights_flow import InsightsFlowDeps, run_insights_flow
from core.llm.factory import get_llm_client
from data.providers.market_data import MarketDataProvider
from data.providers.news import NewsAggregator
from data.providers.user_context import UserContextProvider
from data.relational.db import SessionLocal
from data.relational.repo import RelationalRepo


def main():
    llm = get_llm_client()
    with SessionLocal() as session: 
        repo = RelationalRepo(session)
        user_ctx = UserContextProvider(repo)
        market = MarketDataProvider()
        news = NewsAggregator()

        deps = InsightsFlowDeps(
            llm=llm,
            user_context_provider=user_ctx,
            market_data_provider=market,
            news_provider=news,
        )

        out = run_insights_flow(user_id="cust_001", deps=deps)
        print(out.model_dump())


if __name__ == "__main__":
    main()
