# -*- coding: utf-8 -*-
'''
    pyvantagepro
    ------------

    The public API and command-line interface to PyVPDriver.

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''
import sys, os
import argparse
from pylink import link_from_url

# Make sure the logger is configured early:
from .logger import LOGGER, active_logger
from .device import VantagePro2
from .utils import dict_to_csv, dict_to_xml

VERSION = '0.1dev'
__version__ = VERSION
