from core.events import Event


def serialize_event(event: Event) -> dict:
    return {"data": event.model_dump_json()}


def deserialize_event(data: dict) -> Event:
    return Event.model_validate_json(data["data"])
