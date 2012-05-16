# coding: utf8
"""
    pyvpdriver.tests.testing_utils
    ------------------------------

    Helpers for tests.

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: BSD, see LICENSE for details.

"""

from __future__ import division, unicode_literals, print_function

import sys
import logging
import contextlib
import functools

from ..logger import LOGGER


class CallbackHandler(logging.Handler):
    """A logging handler that calls a function for every message."""
    def __init__(self, callback):
        logging.Handler.__init__(self)
        self.emit = callback


@contextlib.contextmanager
def capture_logs():
    """Return a context manager that captures all logged messages."""
    loggers = [LOGGER,]
    previous_handlers = []
    messages = []

    def emit(record):
        message = '%s: %s' % (record.levelname.upper(), record.getMessage())
        messages.append(message)
        print(message, file=sys.stderr)

    for logger in loggers:
        previous_handlers.append((logger, logger.handlers))
        logger.handlers = []
        logger.addHandler(CallbackHandler(emit))
    try:
        yield messages
    finally:
        for logger, handlers in previous_handlers:
            logger.handlers = handlers


def assert_no_logs(function):
    """Decorator that asserts that nothing is logged in a function."""
    @functools.wraps(function)
    def wrapper():
        with capture_logs() as logs:
            try:
                function()
            except Exception:  # pragma: no cover
                if logs:
                    print('%i errors logged:' % len(logs), file=sys.stderr)
                raise
            else:
                assert len(logs) == 0, '%i errors logged:' % len(logs)
    return wrapper
