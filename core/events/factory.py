from datetime import datetime
from .schema import Event


def create_event(
    event_type: str,
    source: str,
    payload: dict,
    correlation_id=None,
    causation_id=None,
):
    now = datetime.utcnow()

    return Event(
        event_type=event_type,
        source=source,
        timestamp=now,
        ingestion_timestamp=now,
        payload=payload,
        correlation_id=correlation_id,
        causation_id=causation_id,
    )
