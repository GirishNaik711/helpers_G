#app.provider.registry

from __future__ import annotations

from typing import Dict, List

from app.providers.base import Provider
from app.providers.connect_coach_stub import ConnectCoachProviderStub
from app.providers.mt_newswire_stub import MTNewswireProviderStub
from app.providers.alphavantage import AlphaVantageProvider
from app.providers.benzinga import BenzingaAnalystInsightsProvider


def build_provider_registry() -> Dict[str, Provider]:
    """
    Registry of available providers. Real providers (alphavantage, benzinga)
    will be added in later phases.
    """
    providers: List[Provider] = [
        ConnectCoachProviderStub(),
        MTNewswireProviderStub(),
        AlphaVantageProvider(),
        BenzingaAnalystInsightsProvider(),
    ]
    return {p.name: p for p in providers}


def resolve_providers(requested: List[str]) -> List[Provider]:
    registry = build_provider_registry()
    selected: List[Provider] = []
    for name in requested:
        p = registry.get(name)
        if p:
            selected.append(p)
    return selected
