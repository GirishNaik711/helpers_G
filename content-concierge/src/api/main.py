#content-concierge/api/main.py`

from fastapi import FastAPI
from api.routes import insights as insights_routes
from api.routes import qa as qa_routes

def create_app() -> FastAPI:
    app=FastAPI(title="Content Concierge", version="0.0.1")
    
    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}
    
    app.include_router(insights_routes.router, prefix="")
    app.include_router(qa_routes.router, prefix="")
    
    return app

app = create_app()
    