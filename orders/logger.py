#!/usr/bin/python3
import logging
from logging.handlers import TimedRotatingFileHandler


def rotating_log(path, log_level=logging.INFO):
    # global logger
    logger = logging.getLogger("orders_log")
    logger.setLevel(log_level)

    # add a rotating handler
    formatter = logging.Formatter('%(asctime)s %(module)s [%(lineno)s] %(levelname)s %(message)s')

    handler = TimedRotatingFileHandler(path, when='midnight', backupCount=5)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


