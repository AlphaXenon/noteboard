import logging
import time
import datetime


def raise_error(exception):
    logger = logging.getLogger("noteboard")
    logger.error(str(exception))
    raise exception


def get_time():
    date = datetime.date.today().strftime("%a %d %b %Y")
    timestamp = int(time.time())
    return date, timestamp
