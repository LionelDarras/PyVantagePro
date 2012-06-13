# coding: utf8
"""
    pyvantagepro.logger
    -------------------

    Logging setup.

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

"""

from __future__ import unicode_literals
import logging


LOGGER = logging.getLogger('pyvpdriver')
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
LOGGER.addHandler(NullHandler())

def active_logger():
    '''Initialize a speaking logger with stream handler (stderr).'''
    LOGGER = logging.getLogger('pyvpdriver')

    LOGGER.setLevel(logging.INFO)
    logging.getLogger('pylink').setLevel(logging.INFO)

    # Default to logging to stderr.
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s ')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    LOGGER.addHandler(stream_handler)
    logging.getLogger('pylink').addHandler(stream_handler)	
