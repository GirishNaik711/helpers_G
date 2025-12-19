from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "local"
    app_name: str = "content-concierge"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str

    # LLM provider toggle
    llm_provider: str = "openai"  # openai | ollama

    # OpenAI
    openai_api_key: str | None = None
    llm_model: str = "gpt-4o-mini"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    
        # External providers (generic; wire your actual endpoints)
    market_data_base_url: str | None = None
    market_data_api_key: str | None = None

    mt_newswires_base_url: str | None = None
    mt_newswires_api_key: str | None = None

    benzinga_base_url: str | None = None
    benzinga_api_key: str | None = None


    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
