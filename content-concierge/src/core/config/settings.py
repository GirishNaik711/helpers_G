from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "local"
    app_name: str = "content-concierge"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
