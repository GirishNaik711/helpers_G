# app/core/config.py
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "content-concierge"
    env: str = "dev"
    log_level: str = "INFO"

    # LLM toggle
    llm_provider: str = "openai"  # anthropic | openai | bedrock

    # Keys
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None

    # Market data providers
    benzinga_api_key: str | None = None
    benzinga_analyst_base_url: str = "https://api.benzinga.com/api/v1/analyst/insights"

    alphavantage_api_key: str | None = None

    # Bedrock
    aws_region: str | None = None
    bedrock_model_id: str = "claude-sonnet-4-5-20250929"
    
    insights_count: int = 3 

    default_llm_provider: str = "openai" 

    default_market_providers: str = "benzinga,alphavantage"

    @property
    def default_market_providers_list(self) -> list[str]:
        return [p.strip() for p in self.default_market_providers.split(",") if p.strip()]

    risk_mode: str = "strict"


settings = Settings()
