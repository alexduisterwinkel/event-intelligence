from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class Event(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)

    event_type: str
    source: str

    timestamp: datetime
    ingestion_timestamp: datetime

    correlation_id: Optional[UUID] = None
    causation_id: Optional[UUID] = None

    version: str = "1.0"

    payload: Dict[str, Any]
    metadata: Dict[str, Any] = {}
