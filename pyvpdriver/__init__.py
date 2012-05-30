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
from .utils import dict_to_csv, dict_to_xml

VERSION = '0.1dev'
__version__ = VERSION


def extract(argv=None, stdout=sys.stdout, stdin=sys.stdin):
    '''Parse command-line arguments and extract data from VP2 device.'''
    format_values = ['csv', 'xml']
    formats = 'CSV or XML'
    extensions = '.csv or .xml'
    stdout = getattr(stdout, 'buffer', stdout)
    parser = argparse.ArgumentParser(prog='pyvpextract',
        description='Extract data from VantagePro 2 station')
    parser.add_argument('--version', action='version',
                        version='PyVPDriver version %s' % VERSION,
                        help='Print PyVPDriver’s version number and exit.')
    parser.add_argument('-f', '--format', choices=format_values,
                        help='Output format. Can be ommited if `output` '
                             'ends with ' + extensions)
    parser.add_argument('-o', '--output', action="store",
                        default=stdout,
                        help='Filename where output is written')

    args = parser.parse_args(argv)

    def output_parse_error():
        parser.error('Either sepecify a format with -f or choose an '
                     'output filename that ends in ' + extensions)

    if args.format is None:
        if args.output == stdout:
            output_parse_error()
        output_lower = args.output.lower()
        for file_format in format_values:
            if output_lower.endswith('.' + file_format):
                format_ = file_format
                break
        else:
            output_parse_error()
    else:
        format_ = args.format.lower()

    if format_ == "csv":
        data = dict_to_csv(VantagePro2(None).get_data())
    else:
        data = dict_to_xml(VantagePro2(None).get_data())

    output = args.output
    if output == stdout:
        output.write(data)
    else:
        path = os.path.abspath(output.encode('utf8'))
        output = open(path, "w")
        output.write(data)
        output.close()




def config(argv=None, stdout=sys.stdout, stdin=sys.stdin):
    '''Parse command-line arguments and configure VP2 device.'''

    parser = argparse.ArgumentParser(prog='pyvpconfig',
        description='configure VantagePro 2 station')
    parser.add_argument('--version', action='version',
                        version='PyVPDriver version %s' % VERSION,
                        help='Print PyVPDriver’s version number and exit.')

    args = parser.parse_args(argv)
