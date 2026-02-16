def create_service(service_cls, name: str, event_bus):
    return service_cls(name=name, event_bus=event_bus)
