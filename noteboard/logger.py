import logging
import os

from . import LOG_PATH


def setup_logger():
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] (%(funcName)s in %(filename)s) %(message)s", "")
    handler = logging.FileHandler(LOG_PATH, mode="a+")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    logger = logging.getLogger("noteboard")
    logger.setLevel(logging.DEBUG)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    return logger
