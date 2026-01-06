#app.providers.base.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol


@dataclass(frozen=True)
class ProviderStatus:
    ok: bool
    configured: bool
    message: str


@dataclass(frozen=True)
class ProviderRequest:
    customer_id: str
    as_of: datetime
    # Later phases can add: tickers, asset mix, etc.
    context: Dict[str, Any]


@dataclass(frozen=True)
class ProviderCitation:
    source: str
    title: str
    url: str
    published_at: Optional[datetime] = None


@dataclass(frozen=True)
class ProviderItem:
    """
    Generic “content chunk” returned by providers.
    In later phases, we’ll standardize types (news, market, education).
    """
    kind: str  # e.g. "news", "market", "education"
    title: str
    summary: str
    url: str
    published_at: Optional[datetime] = None
    extra: Dict[str, Any] | None = None


@dataclass(frozen=True)
class ProviderResponse:
    provider: str
    items: List[ProviderItem]
    citations: List[ProviderCitation]
    raw: Dict[str, Any] | None = None


class Provider(Protocol):
    name: str

    def healthcheck(self) -> ProviderStatus: ...
    def fetch(self, request: ProviderRequest) -> ProviderResponse: ...
