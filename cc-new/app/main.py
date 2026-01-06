from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from dotenv import load_dotenv
load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.include_router(router)
    return app


app = create_app()
