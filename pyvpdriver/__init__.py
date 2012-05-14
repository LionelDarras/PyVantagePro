# coding: utf8
"""
    pyvpdriver
    ~~~~~~~~~~

    The public API is what is accessible from this "root" packages
    without importing sub-modules.

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: BSD, see LICENSE for more details.

"""

from __future__ import division, unicode_literals

# Make sure the logger is configured early:
from .logger import LOGGER


VERSION = '0.1dev'
__version__ = VERSION
