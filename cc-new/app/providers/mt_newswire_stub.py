from __future__ import annotations

from app.providers.base import Provider, ProviderRequest, ProviderResponse, ProviderStatus


class MTNewswireProviderStub(Provider):
    name = "mt_newswires"

    def healthcheck(self) -> ProviderStatus:
        return ProviderStatus(ok=True, configured=False, message="Stub provider (not configured)")

    def fetch(self, request: ProviderRequest) -> ProviderResponse:
        return ProviderResponse(provider=self.name, items=[], citations=[], raw={"stub": True})
