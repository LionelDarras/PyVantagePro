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

import sys, os
import argparse
# Make sure the logger is configured early:
from .logger import LOGGER

from .device import VantagePro
from .link import TCPLink


VERSION = '0.1dev'
__version__ = VERSION


def extract(argv=None, stdout=sys.stdout, stdin=sys.stdin):
    """Parse command-line arguments and extract data from VP2 device."""
    format_values = ['csv', 'xml']
    formats = 'CSV or XML'
    extensions = '.csv or .xml'

    parser = argparse.ArgumentParser(prog='pyvpextract',
        description='Extract data from VantagePro 2 station')
    parser.add_argument('--version', action='version',
                        version='PyVPDriver version %s' % VERSION,
                        help='Print PyVPDriver’s version number and exit.')

    args = parser.parse_args(argv)


def config(argv=None, stdout=sys.stdout, stdin=sys.stdin):
    """Parse command-line arguments and configure VP2 device."""

    parser = argparse.ArgumentParser(prog='pyvpconfig',
        description='Extract data from VantagePro 2 station')
    parser.add_argument('--version', action='version',
                        version='PyVPDriver version %s' % VERSION,
                        help='Print PyVPDriver’s version number and exit.')

    args = parser.parse_args(argv)
