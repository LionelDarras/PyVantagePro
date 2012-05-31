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
    parser.add_argument('-f', '--format', choices=format_values, default="csv",
                        help='Output data format.')
    parser.add_argument('--delimiter', action="store", default=",",
                        help='CSV delimiter')
    parser.add_argument('-o', '--output', action="store",
                        default=stdout,
                        help='Filename where output is written')

    parser.add_argument('link', action="store",
                    help='Specifiy URL for connection link ' +
                         'E.g. tcp:localhost:1111 ' +
                         'or serial:/dev/ttyUSB0:19200:8N1')
    parser.add_argument('--timeout', default=1, type=float,
                        help="Connection link timeout")
    parser.add_argument('--debug', action="store_true", default=False,
                        help='Display log')
    args = parser.parse_args(argv)

    if not args.debug:
        LOGGER.disabled = True

    def output_parse_error():
        parser.error('Either sepecify a format with -f or choose an '
                     'output filename that ends in ' + extensions)

    def link_parse_error():
        parser.error('Bad url link sepecified')

    timeout = args.timeout
    if args.link:
        link_args = args.link.split(':')
        if len(link_args) <= 1:
            link_parse_error()
        mode = link_args[0].lower()
        if mode == "tcp":
            try:
                host = link_args[1]
                port = int(link_args[2])
            except Exception as e:
                LOGGER.error("%s" % e)
                link_parse_error()
            link = TCPLink(host, port)
        if mode == "serial":
            if len(link_args) == 2:
                port = link_args[1]
                link = SerialLink(port)
            elif len(link_args) == 2:
                try:
                    port = link_args[1]
                    baudrate = int(link_args[2])
                    link = SerialLink(port, baudrate)
                except Exception as e:
                    LOGGER.error("%s" % e)
                    link_parse_error()
            elif len(link_args) == 2:
                try:
                    port = link_args[1]
                    baudrate = int(link_args[2])
                    bytesize=int(link_args[3][1])
                    parity= link_args[3][2]
                    stopbits= int(link_args[3][3])
                    link = SerialLink(port, baudrate, bytesize, parity,
                                            stopbits, timeout)
                except Exception as e:
                    LOGGER.error("%s" % e)
                    link_parse_error()
        else:
            link_parse_error()
    else:
        parser.error('Either sepecify an url link sepecified')
    vp = VantagePro2(link)
    format_ = args.format.lower()

    if format_ == "csv":
        delimiter = args.delimiter.decode("string-escape")
        data = dict_to_csv(vp.get_current_data(), delimiter)
    else:
        data = dict_to_xml(vp.get_current_data())

    output = args.output
    if output == stdout:
        output.write(data)
    else:
        path = os.path.abspath(output.encode('utf8'))
        with open(path, "w") as fd:
            fd.write(data)
    print vp.firmware_date




def config(argv=None, stdout=sys.stdout, stdin=sys.stdin):
    '''Parse command-line arguments and configure VP2 device.'''

    parser = argparse.ArgumentParser(prog='pyvpconfig',
        description='configure VantagePro 2 station')
    parser.add_argument('--version', action='version',
                        version='PyVPDriver version %s' % VERSION,
                        help='Print PyVPDriver’s version number and exit.')

    args = parser.parse_args(argv)
