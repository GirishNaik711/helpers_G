from __future__ import annotations

import httpx
from core.config.settings import settings


class MarketDataProvider:
    """
    Optional market data provider.
    If MARKET_DATA_BASE_URL is not set, calls return {} (no crash).
    """

    def __init__(self) -> None:
        self.base_url = (settings.market_data_base_url or "").strip()
        self.api_key = (settings.market_data_api_key or "").strip()
        self.enabled = bool(self.base_url)
        self.http = httpx.Client(timeout=30) if self.enabled else None

    def get_snapshot(self, tickers: list[str]) -> dict:
        if not self.enabled or not tickers:
            return {}

        params = {"tickers": ",".join(tickers)}
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        r = self.http.get(f"{self.base_url.rstrip('/')}/snapshot", params=params, headers=headers)
        r.raise_for_status()
        return r.json()
