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
    parser.add_argument('-f', '--format', choices=format_values, default="csv",
                        help='Output data format.')
    parser.add_argument('--delimiter', action="store", default=",",
                        help='CSV delimiter')
    parser.add_argument('-o', '--output', action="store", default=stdout,
                        help='Filename where output is written')

    parser.add_argument('url', action="store",
                        help='Specifiy URL for connection link ' +
                             'E.g. tcp:localhost:1111 ' +
                             'or serial:/dev/ttyUSB0:19200:8N1')
    parser.add_argument('--timeout', default=1, type=float,
                        help="Connection link timeout")
    parser.add_argument('--debug', action="store_true", default=False,
                        help='Display log')
    args = parser.parse_args(argv)

    if args.debug:
        LOGGER = active_logger()

    def output_parse_error():
        parser.error('Either sepecify a format with -f')

    if args.url:
        try:
            link = link_from_url(args.url)
            link.settimeout(args.timeout)
        except Exception as e:
            parser.error('%s' % e)
    else:
        parser.error('Either sepecify an url link')

    vp = VantagePro2(link)

    format_ = args.format.lower()
    if format_ == "xml":
        data = vp.get_current_data().to_xml()
    elif format_ == "csv":
        delimiter = args.delimiter.decode("string-escape")
        data = vp.get_current_data().to_csv(delimiter)
    else:
        parser.error('Either sepecify a format with -f in ' + extensions)

    output = args.output
    if output == stdout:
        output.write(data)
    else:
        path = os.path.abspath(output.encode('utf8'))
        with open(path, "w") as fd:
            fd.write(data)


def config(argv=None, stdout=sys.stdout, stdin=sys.stdin):
    '''Parse command-line arguments and configure VP2 device.'''

    parser = argparse.ArgumentParser(prog='pyvpconfig',
        description='configure VantagePro 2 station')
    parser.add_argument('--version', action='version',
                        version='PyVPDriver version %s' % VERSION,
                        help='Print PyVPDriver’s version number and exit.')

    args = parser.parse_args(argv)
