import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logger(service_name: str):
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)

    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s "
        "%(event_id)s %(correlation_id)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

#usage:
# logger.info(
#     "Event processed",
#     extra={
#         "event_id": str(event.event_id),
#         "correlation_id": str(event.correlation_id),
#     },
# )
