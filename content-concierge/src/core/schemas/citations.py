#core/schemas/citations.py
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

class Provider(str, Enum):
    mt_newswires = "mt_newswires"
    benzinga = "benzinga"
    market_data_api = "market_data_api"
    connect_coach = "connect_coach"  
    unknown = "unknown"


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    citation_id: str
    provider: Provider = Provider.unknown
    title: str
    url: str
    published_at: Optional[datetime] = None
    quote_span: Optional[str] = Field(
        default=None, description="Optional short excerpt pointer; keep minimal"
    )
    claim_ids: list[str] = Field(default_factory=list)