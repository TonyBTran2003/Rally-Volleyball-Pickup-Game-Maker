import logging
import sys


def configure_logging():
    logger = logging.getLogger("rally")

    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    handler = logging.StreamHandler(
        sys.stdout
    )

    formatter = logging.Formatter(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    )

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger