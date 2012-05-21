# coding: utf8
"""
    pyvpdriver.logger
    -----------------

    Logging setup.

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

"""

from __future__ import division, unicode_literals

import logging

def init_logger():
    logger = logging.getLogger('pyvpdriver')

    # Default to logging to stderr.
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s ')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)

    return logger

LOGGER = init_logger()
