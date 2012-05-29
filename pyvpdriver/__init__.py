# -*- coding: utf-8 -*-
'''
    pyvpdriver
    ~~~~~~~~~~

    The public API and command-line interface to PyVPDriver.

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''
import sys, os
import argparse
# Make sure the logger is configured early:
from .logger import LOGGER

from .device import VantagePro2
from .link import TCPLink, SerialLink


VERSION = '0.1dev'
__version__ = VERSION


def extract(argv=None, stdout=sys.stdout, stdin=sys.stdin):
    '''Parse command-line arguments and extract data from VP2 device.'''
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
    '''Parse command-line arguments and configure VP2 device.'''

    parser = argparse.ArgumentParser(prog='pyvpconfig',
        description='configure VantagePro 2 station')
    parser.add_argument('--version', action='version',
                        version='PyVPDriver version %s' % VERSION,
                        help='Print PyVPDriver’s version number and exit.')

    args = parser.parse_args(argv)
