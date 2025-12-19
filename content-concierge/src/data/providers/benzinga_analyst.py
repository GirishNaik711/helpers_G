from __future__ import annotations

import httpx
from core.config.settings import settings


class BenzingaAnalystInsightsProvider:
    """
    Benzinga Analyst Insights:
    GET https://api.benzinga.com/api/v1/analyst/insights?token=...&symbols=AAPL,MSFT
    """

    def __init__(self) -> None:
        if not settings.benzinga_api_key:
            raise ValueError("BENZINGA_API_KEY is required")
        self.base_url = settings.benzinga_analyst_base_url.rstrip("/")
        self.api_key = settings.benzinga_api_key
        self.http = httpx.Client(timeout=30)

    def fetch(self, symbols: list[str], page: int = 1, page_size: int = 10) -> list[dict]:
        if not symbols:
            return []

        params = {
            "token": self.api_key,
            "symbols": ",".join(sorted(set(symbols))),
            "page": page,
            "pageSize": page_size,
        }
        r = self.http.get(self.base_url, params=params)
        r.raise_for_status()

        # Benzinga returns: {"insights": [...] } OR sometimes a raw list depending on endpoint version.
        data = r.json()

# Benzinga returns analyst insights under "analyst-insights"
        insights = []
        if isinstance(data, dict):
            insights = data.get("analyst-insights") or data.get("analyst_insights") or data.get("insights") or []
        elif isinstance(data, list):
            insights = data
        else:
            insights = []
            
        if not insights:
            return []

        out = []
        for it in insights:
            sec = it.get("security") or {}
            symbol = sec.get("symbol") or it.get("symbol") or ""

            out.append(
                {
                    "provider": "benzinga",
                    "title": f"{symbol} — {it.get('action','')} / {it.get('rating','')}".strip(),
                    "url": "",  # Benzinga payload doesn't provide URL here
                    "published_at": it.get("date"),
                    "symbol": symbol,
                    "firm": it.get("firm"),
                    "rating": it.get("rating"),
                    "pt": it.get("pt"),
                    "analyst_insights": it.get("analyst_insights"),
                    "raw": it,
                }
            )
        return out
