#app.provider.alphavantage.py
from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List

import httpx

from app.providers.base import (
    Provider,
    ProviderRequest,
    ProviderResponse,
    ProviderStatus,
    ProviderItem,
    ProviderCitation,
)
from dotenv import load_dotenv
load_dotenv()

class AlphaVantageProvider(Provider):
    name = "alphavantage"
    base_url = "https://www.alphavantage.co/query"

    def __init__(self) -> None:
        self.api_key = os.getenv("ALPHAVANTAGE_API_KEY")

    def healthcheck(self) -> ProviderStatus:
        if not self.api_key:
            return ProviderStatus(ok=False, configured=False, message="Missing API key")
        return ProviderStatus(ok=True, configured=True, message="OK")

    def fetch(self, request: ProviderRequest) -> ProviderResponse:
        tickers = request.context.get("tickers", [])[:3]  
        items = []
        citations = []

        for symbol in tickers:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": "compact",
                "apikey": self.api_key,
            }

            r = httpx.get(self.base_url, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()

            series = data.get("Time Series (Daily)", {})
            if not series:
                continue

            dates = sorted(series.keys(), reverse=True)[:5]
            closes = [float(series[d]["4. close"]) for d in dates]

            min_c, max_c = min(closes), max(closes)

            items.append(
                ProviderItem(
                    kind="price_context",
                    title=f"{symbol} recent price activity",
                    summary=(
                        f"Recent prices for {symbol} ranged between "
                        f"{min_c:.2f} and {max_c:.2f} over the last few sessions."
                    ),
                    url="https://www.alphavantage.co/documentation/",
                    published_at=None,
                    extra={"symbol": symbol},
                )
            )

            citations.append(
                ProviderCitation(
                    source="Alpha Vantage",
                    title=f"Alpha Vantage TIME_SERIES_DAILY for {symbol}",
                    url="https://www.alphavantage.co/documentation/",
                    published_at=None,
                )
            )

        return ProviderResponse(
            provider=self.name,
            items=items,
            citations=citations,
            raw={},
        )

