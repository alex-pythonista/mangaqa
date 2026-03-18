import logging
import sys

from app.config import settings

DEV_FORMAT = "%(levelname)-5s | %(name)s | %(message)s"
PROD_FORMAT = "%(asctime)s | %(levelname)-5s | %(name)s | %(message)s"


def setup_logging() -> None:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    is_prod = settings.ENV == "production"

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(PROD_FORMAT if is_prod else DEV_FORMAT))

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    # Quiet noisy third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
