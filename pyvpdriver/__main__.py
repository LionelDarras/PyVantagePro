# coding: utf8
"""
    pyvpdriver.__main__
    -------------------

    Command-line interface to PyVPDriver.

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: BSD, see LICENSE for details.

"""

from __future__ import division, unicode_literals

import sys, os
from logging.handlers import RotatingFileHandler
import argparse

from . import VERSION
from .logger import LOGGER


def main(argv=None, stdout=sys.stdout, stdin=sys.stdin):
    """Parse command-line arguments and convert the given document."""
    format_values = ['csv', 'xml']
    formats = 'CSV or XML'
    extensions = '.csv or .xml'

    parser = argparse.ArgumentParser(prog='pyvpdriver',
        description='Read data from VantagePro 2 station')
    parser.add_argument('--version', action='version',
                        version='PyVPDriver version %s' % VERSION,
                        help='Print PyVPDriver’s version number and exit.')

    args = parser.parse_args(argv)


if __name__ == '__main__':  # pragma: no cover
    main()
