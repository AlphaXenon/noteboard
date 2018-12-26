import logging


def raise_error(exception):
    logger = logging.getLogger("noteboard")
    logger.error(str(exception))
    raise exception
