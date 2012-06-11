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

from datetime import datetime
from pylink import link_from_url

# Make sure the logger is configured early:
from . import VERSION
from .logger import LOGGER, active_logger
from .device import VantagePro2


NOW = datetime.now().strftime("%Y-%m-%d %H:%M")
# stdout.buffer on Py3, stdout on Py2
stdout = sys.stdout
stdout = getattr(stdout, 'buffer', stdout)

def gettime_cmd(args, vp):
    args.output.write("%s\n" % vp.time)

def getinfo_cmd(args, vp):
    info = "Firmware date : %s\n" % vp.firmware_date
    info = "%sFirmware version : %s\n" % (info, vp.firmware_version)
    info = "%sDiagnostics : %s\n" % (info, vp.diagnostics)
    args.output.write("%s" % info)


def getarchives(args, vp):
    from .utils import ListDict
    if args.debug:
        return vp.get_archives(args.start, args.stop)
    from progressbar import ProgressBar, Percentage, Bar, RotatingMarker, FileTransferSpeed, ETA, AnimatedMarker
    records = ListDict()
    generator = vp.get_archives_generator(args.start, args.stop)
    widgets = ['Archives download: ', Percentage(), ' ',
               Bar()]
    pbar = ProgressBar(widgets=widgets, maxval=2600).start()
    for step, record in enumerate(generator):
        pbar.update(step)
        records.append(record)
    pbar.finish()
    return records


def getarchives_cmd(args, vp):
    if args.start is not None:
        args.start = datetime.strptime(" ".join(args.start), "%Y-%m-%d %H:%M")
    if args.stop is not None:
        args.stop = datetime.strptime(" ".join(args.stop), "%Y-%m-%d %H:%M")
    args.output.write(getarchives(args, vp).to_csv())


def get_cmd_parser(cmd, subparsers, help, func):
    parser = subparsers.add_parser(cmd, help=help, description=help)
    parser.add_argument('--output', action="store", default=stdout,
                        type=argparse.FileType('wb', 0),
                        help='Filename where output is written')
    parser.add_argument('--timeout', default=1, type=float,
                        help="Connection link timeout")
    parser.add_argument('--debug', action="store_true", default=False,
                        help='Display log')
    parser.add_argument('url', action="store",
                        help="Specifiy URL for connection link. " \
                             "E.g. tcp:localhost:1111 " \
                             "or serial:/dev/ttyUSB0:19200:8N1")
    parser.set_defaults(func=func)
    return parser


def add_datetime_argument(parser, name, help):
    parser.add_argument(name, action="store", default=None, nargs=2,
            help= "%s Format is like : %s" % (help, NOW))


def main():
    '''Parse command-line arguments and extract data from VP2 device.'''
    parser = argparse.ArgumentParser(prog='pyvantagepro',
                        description='Extract data from VantagePro 2 station')

    parser.add_argument('--version', action='version',
                        version='PyVPDriver version %s' % VERSION,
                        help='Print PyVPDriver’s version number and exit.')

    parser.add_argument('--output', action="store", default=stdout,
                        type=argparse.FileType('wb', 0),
                        help='Filename where output is written')

    parser.add_argument('--delim', action="store", default=",",
                        help='CSV char delimiter')

    parser.add_argument('--timeout', default=1, type=float,
                        help="Connection link timeout")

    subparsers = parser.add_subparsers(title='The pyvantagepro commands')
    # gettime command
    subparser = get_cmd_parser('gettime', subparsers,
                        help='Print the current date on the station.',
                        func=gettime_cmd)

    # getinfo command
    subparser = get_cmd_parser('getinfo', subparsers,
                        help='Print VantagePro information.',
                        func=getinfo_cmd)


    # getarchives command
    subparser = get_cmd_parser('getarchives', subparsers,
                        help='Extract archives data from the station.',
                        func=getarchives_cmd)
    add_datetime_argument(subparser, '--start', 'Start date.')
    add_datetime_argument(subparser, '--stop', 'Start date.')


    # getdata command
    subparser = get_cmd_parser('getdata', subparsers,
                        help='Extract real-time data from the station.',
                        func=getinfo_cmd)

    # Parse argv arguments
    args = parser.parse_args()

    if args.debug:
        LOGGER = active_logger()

    args.delim = args.delim.decode("string-escape")

    if args.url:
        try:
            link = link_from_url(args.url)
            link.settimeout(args.timeout)
            link.open()
        except Exception as e:
            parser.error('%s' % e)
    else:
        parser.error('Either sepecify an url link')

    try:
        vp = VantagePro2(link)
        args.func(args, vp)
    except Exception as e:
        if args.debug:
            raise e
        else:
            print("Error: %s" % e)




if __name__ == '__main__':  # pragma: no cover
    main()
