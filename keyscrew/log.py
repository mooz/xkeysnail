# -*- coding: utf-8 -*-

"""keyscrew log module."""

import logging
from os.path import join
from keyscrew import CONFIG


logging.basicConfig(
    filemode='a',
    filename=join(CONFIG, "keyscrew.log"),
    level=logging.DEBUG,
    format="%(asctime)s | %(message)s"
)


def log_msg(msg):
    """Function write messege to log file."""
    logging.info(msg)


def wrap_logger(func):
    """Decorator to log functions."""
    def wrap(*args, **kwargs):
        result = func(*args, **kwargs)
        args = ', '.join([str(i) for i in args])
        log_msg(' --> '.join([args, str(kwargs)]))
        return result
    return wrap
