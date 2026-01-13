# app/core/logging.py
from __future__ import annotations
import logging, sys
from app.core.config import settings

def setup_logging() -> None:
    level = getattr(logging, (settings.log_level or "INFO").upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        stream=sys.stdout,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


    # quiet noisy libs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
