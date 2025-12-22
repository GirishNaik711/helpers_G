from __future__ import annotations

import httpx

from core.config.settings import settings


class InternalContentProvider:
    """
    Placeholder "Connect Coach" style provider.
    If not configured, returns [] safely.
    """

    def __init__(self) -> None:
        self.base_url = (getattr(settings, "connect_coach_base_url", None) or "").strip()
        self.api_key = (getattr(settings, "connect_coach_api_key", None) or "").strip()
        self.http = httpx.Client(timeout=20)

    def search(self, query: str, limit: int = 3) -> list[dict]:
        if not self.base_url:
            return []
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        r = self.http.get(f"{self.base_url.rstrip('/')}/search", params={"q": query, "limit": limit}, headers=headers)
        r.raise_for_status()
        items = r.json()
        for it in items:
            it["provider"] = "connect_coach"
        return items[:limit]
