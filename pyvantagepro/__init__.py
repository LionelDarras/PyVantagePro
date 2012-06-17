# -*- coding: utf-8 -*-
'''
    pyvantagepro
    ------------

    The public API and command-line interface to PyVPDriver.

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''
# Make sure the logger is configured early:
from .logger import LOGGER, active_logger
from .device import VantagePro2

VERSION = '0.2dev'
__version__ = VERSION
