# coding: utf8
"""
    pyvpdriver.logger
    -----------------

    Logging setup.

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: BSD, see LICENSE for details.

"""

from __future__ import division, unicode_literals

import logging

LOGGER = logging.getLogger('pyvpdriver')

# Default to logging to stderr.
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.INFO)
