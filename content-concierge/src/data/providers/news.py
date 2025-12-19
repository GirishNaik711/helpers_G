from __future__ import annotations

import httpx
from core.config.settings import settings


class NewsAggregator:
    """
    Benzinga-only news provider.
    """

    def __init__(self) -> None:
        if not settings.benzinga_base_url or not settings.benzinga_api_key:
            raise ValueError("Benzinga BASE_URL and API_KEY are required")

        self.base_url = settings.benzinga_base_url.rstrip("/")
        self.api_key = settings.benzinga_api_key
        self.http = httpx.Client(timeout=30)

    def search(self, query: str, tickers: list[str], limit: int = 5) -> list[dict]:
        params = {
            "token": self.api_key,
            "q": query,
            "tickers": ",".join(tickers) if tickers else None,
            "limit": limit,
        }

        r = self.http.get(self.base_url, params=params)
        r.raise_for_status()

        items = r.json()
        results = []

        for it in items:
            results.append(
                {
                    "title": it.get("title"),
                    "url": it.get("url"),
                    "published_at": it.get("created"),
                    "provider": "benzinga",
                    "tickers": it.get("stocks", []),
                }
            )

        return results
