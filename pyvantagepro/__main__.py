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
    '''Gettime command.'''
    args.output.write("%s - %s\n" % (vp.time, vp.timezone))

def settime_cmd(args, vp):
    '''Settime command.'''
    old_time = vp.time
    vp.time = datetime.strptime(args.datetime, "%Y-%m-%d %H:%M")
    args.output.write("Old value : %s - %s\n" % old_time, vp.timezone)
    args.output.write("New value : %s - %s\n" % vp.time, vp.timezone)

def getinfo_cmd(args, vp):
    '''Getinfo command.'''
    info = "Firmware date : %s\n" % vp.firmware_date
    info = "%sFirmware version : %s\n" % (info, vp.firmware_version)
    info = "%sDiagnostics : %s\n" % (info, vp.diagnostics)
    args.output.write("%s" % info)


def getdata_cmd(args, vp):
    '''Get real-time data command'''
    args.delim = args.delim.decode("string-escape")
    data = vp.get_current_data().to_csv(delimiter=args.delim)
    args.output.write("%s" % data)


def getarchives(args, vp):
    '''Getarchive with progressbar if `args.debug` is True.'''
    from .utils import ListDict
    if args.debug:
        return vp.get_archives(args.start, args.stop)
    from progressbar import ProgressBar, Percentage, Bar
    records = ListDict()
    generator = vp.get_archives_generator(args.start, args.stop)
    widgets = ['Archives download: ', Percentage(), ' ', Bar()]
    pbar = ProgressBar(widgets=widgets, maxval=2600).start()
    for step, record in enumerate(generator):
        pbar.update(step)
        records.append(record)
    pbar.finish()
    return records


def getarchives_cmd(args, vp):
    '''Getarchive command.'''
    args.delim = args.delim.decode("string-escape")
    if args.start is not None:
        args.start = datetime.strptime(args.start, "%Y-%m-%d %H:%M")
    if args.stop is not None:
        args.stop = datetime.strptime(args.stop, "%Y-%m-%d %H:%M")
    args.output.write(getarchives(args, vp).to_csv(delimiter=args.delim))


def get_cmd_parser(cmd, subparsers, help, func):
    '''Make a subparser command.'''
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
                             "E.g. tcp:iphost:port " \
                             "or serial:/dev/ttyUSB0:19200:8N1")
    parser.set_defaults(func=func)
    return parser


def main():
    '''Parse command-line arguments and extract data from VP2 device.'''
    parser = argparse.ArgumentParser(prog='pyvantagepro',
                        description='Extract data from VantagePro 2 station')

    parser.add_argument('--version', action='version',
                        version='PyVPDriver version %s' % VERSION,
                        help='Print PyVPDriver’s version number and exit.')

    subparsers = parser.add_subparsers(title='The pyvantagepro commands')
    # gettime command
    subparser = get_cmd_parser('gettime', subparsers,
                        help='Print the current date on the station.',
                        func=gettime_cmd)

    # settime command
    subparser = get_cmd_parser('settime', subparsers,
                        help='Set the datetime argument on the station.',
                        func=settime_cmd)
    subparser.add_argument('datetime', help='The chosen datetime value. '\
                                      '(like : "%s")' % NOW)

    # getinfo command
    subparser = get_cmd_parser('getinfo', subparsers,
                        help='Print VantagePro information.',
                        func=getinfo_cmd)

    # getarchives command
    subparser = get_cmd_parser('getarchives', subparsers,
                        help='Extract archives data from the station between'\
                             ' `start` date and `stop` date. By default the '\
                             'entire contents of the data archive will be '\
                             'downloaded.',
                        func=getarchives_cmd)
    subparser.add_argument('--start', help="The beging date record. "\
                                      "(like : \"%s\")" % NOW)
    subparser.add_argument('--stop', help="The stoping date record. "\
                                      "(like : \"%s\")" % NOW)
    subparser.add_argument('--delim', action="store", default=",",
                        help='CSV char delimiter')

    # getdata command
    subparser = get_cmd_parser('getdata', subparsers,
                        help='Extract real-time data from the station.',
                        func=getdata_cmd)
    subparser.add_argument('--delim', action="store", default=",",
                        help='CSV char delimiter')

    # update command
    subparser = get_cmd_parser('update', subparsers,
                        help='Update csv database records with getting '\
                             'automaticly new records.',
                        func=getdata_cmd)
    subparser.add_argument('db', action="store", type=argparse.FileType('wb', 0),
                        help='The CSV database')

    # Parse argv arguments
    args = parser.parse_args()

    if args.debug:
        LOGGER = active_logger()

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
