#src/api/main.py
from fastapi import FastAPI

from api.routes import insights as insights_routes
from api.routes import users as users_routes
from api.routes import debug as debug_routes


def create_app() -> FastAPI:
    app = FastAPI(title="Content Concierge", version="0.0.1")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    app.include_router(insights_routes.router)
    app.include_router(users_routes.router)
    app.include_router(debug_routes.router)

    return app


app = create_app()
