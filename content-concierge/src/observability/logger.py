from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from core.config.settings import settings


def _json_default(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


class JsonLogger:
    def __init__(self, name: str = "content-concierge"):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(handler)

    def info(self, event: str, *, fields: Optional[Mapping[str, Any]] = None) -> None:
        self._logger.info(self._format(event, fields))

    def warning(self, event: str, *, fields: Optional[Mapping[str, Any]] = None) -> None:
        self._logger.warning(self._format(event, fields))

    def error(self, event: str, *, fields: Optional[Mapping[str, Any]] = None) -> None:
        self._logger.error(self._format(event, fields))

    def _format(self, event: str, fields: Optional[Mapping[str, Any]]) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "app": settings.app_name,
            "env": settings.app_env,
            **(dict(fields) if fields else {}),
        }
        return json.dumps(payload, default=_json_default)


logger = JsonLogger()
