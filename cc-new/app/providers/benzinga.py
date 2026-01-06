#app.providers.benzinga.py

from __future__ import annotations

import httpx
from typing import List

from app.providers.base import (
    Provider,
    ProviderRequest,
    ProviderResponse,
    ProviderStatus,
    ProviderItem,
    ProviderCitation,
)
from app.core.config import settings
from dotenv import load_dotenv
load_dotenv()

class BenzingaAnalystInsightsProvider(Provider):
    name = "benzinga"

    def __init__(self) -> None:
        if not settings.benzinga_api_key:
            raise ValueError("BENZINGA_API_KEY is required")
        self.base_url = settings.benzinga_analyst_base_url.rstrip("/")
        self.api_key = settings.benzinga_api_key
        self.http = httpx.Client(timeout=30)

    def healthcheck(self) -> ProviderStatus:
        return ProviderStatus(ok=True, configured=True, message="OK")

    def fetch(self, request: ProviderRequest) -> ProviderResponse:
        symbols: List[str] = request.context.get("tickers", [])
        if not symbols:
            return ProviderResponse(self.name, [], [], raw={})

        params = {
            "token": self.api_key,
            "symbols": ",".join(sorted(set(symbols))),
            "page": 1,
            "pageSize": 10,
        }

        r = self.http.get(self.base_url, params=params)
        r.raise_for_status()
        data = r.json()

        insights = (
            data.get("analyst-insights")
            or data.get("analyst_insights")
            or data.get("insights")
            or []
        )

        items: list[ProviderItem] = []
        citations: list[ProviderCitation] = []

        for it in insights:
            sec = it.get("security") or {}
            symbol = sec.get("symbol") or it.get("symbol")
            if not symbol:
                continue

            items.append(
                ProviderItem(
                    kind="analyst_context",
                    title=f"{symbol} analyst commentary",
                    summary=(
                        f"Recent analyst commentary from {it.get('firm')} "
                        f"discusses outlook and expectations."
                    ),
                    url="",  # Benzinga does not expose a public URL here
                    published_at=it.get("date"),
                    extra={
                        "symbol": symbol,
                        "firm": it.get("firm"),
                        "rating": it.get("rating"),
                        "price_target": it.get("pt"),
                    },
                )
            )

            citations.append(
                ProviderCitation(
                    source="Benzinga",
                    title=f"Benzinga analyst insight for {symbol}",
                    url="https://www.benzinga.com",
                    published_at=it.get("date"),
                )
            )

        return ProviderResponse(
            provider=self.name,
            items=items,
            citations=citations,
            raw=data,
        )
