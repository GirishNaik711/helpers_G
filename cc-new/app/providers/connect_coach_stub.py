from __future__ import annotations

from app.providers.base import Provider, ProviderRequest, ProviderResponse, ProviderStatus


class ConnectCoachProviderStub(Provider):
    name = "connect_coach"

    def healthcheck(self) -> ProviderStatus:
        return ProviderStatus(ok=True, configured=False, message="Stub provider (not configured)")

    def fetch(self, request: ProviderRequest) -> ProviderResponse:
        # Stub returns nothing for MVP; plug credentials later.
        return ProviderResponse(provider=self.name, items=[], citations=[], raw={"stub": True})
