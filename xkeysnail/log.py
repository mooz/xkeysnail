# -*- coding: utf-8 -*-

"""Xkeysnail log module."""

import logging
from os.path import join
from xkeysnail import CONFIG


logging.basicConfig(
    filemode='w',
    filename=join(CONFIG, "xkeysnail.log"),
    level=logging.DEBUG,
    format="%(asctime)s | %(message)s"
)


def log_msg(msg):
    logging.warning(msg)


def wrap_logger(func):
    '''Decorator that reports the execution time.'''
    def wrap(*args, **kwargs):
        result = func(*args, **kwargs)
        args = ', '.join([str(i) for i in args])
        log_msg(' --> '.join([args, str(kwargs)]))
        return result
    return wrap
