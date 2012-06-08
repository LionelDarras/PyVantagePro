# -*- coding: utf-8 -*-
'''
    pyvantagepro.device
    -------------------

    Allows data query of Davis Vantage Pro2 devices

    This part of code is inspired by PyWeather projet
    by Patrick C. McGinty <pyweather@tuxcoder.com>

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''
from __future__ import division, unicode_literals
import time
from datetime import datetime

from .logger import LOGGER
from .utils import (cached_property, retry, byte_to_string, hex_to_byte,
                    ListDataDict)

from .parser import (LoopDataParserRevB, DmpHeaderParser, DmpPageParser,
                     ArchiveDataParserRevB, pack_datetime, unpack_datetime,
                     pack_dmp_date_time)


class NoDeviceException(Exception):
    '''Can not access weather station.'''
    value = __doc__


class BadAckException(Exception):
    '''The acknowledgement is not the one expected.'''
    value = __doc__


class BadCRCException(Exception):
    '''The CRC is not correct.'''
    value = __doc__


class VantagePro2(object):
    '''A class capable of reading raw (binary) weather data from a
    Vantage Pro 2 console.'''

    # device reply commands
    WAKE_STR = '\n'
    WAKE_ACK = '\n\r'
    ACK = '\x06'
    NACK = '\x21'
    DONE = 'DONE\n\r'
    CANCEL = '\x18'
    ESC = '\x1b'
    OK = '\n\rOK\n\r'

    def __init__(self, link):
        self.link = link

    def wake_up(self):
        '''Wakeup the console.'''
        LOGGER.info("try wake up console")
        self.link.write(self.WAKE_STR)
        if self.check_ack(self.WAKE_ACK):
            self.last_wake_up = time.time()
            return True
        raise NoDeviceException()

    @retry(tries=3, delay=1)
    def run_cmd(self, cmd, wait_ack=None, is_byte=False):
        '''Write a single command. If `wait_ack` is not None, the function must
        check that acknowledgement is the one expected.'''
        self.wake_up()
        if is_byte:
            LOGGER.info("try send : %s" % byte_to_string(cmd))
            self.link.write(cmd, is_byte)
        else:
            LOGGER.info("try send : %s" % cmd)
            self.link.write("%s\n" % cmd)
        if wait_ack is None:
            return True
        else:
            if self.check_ack(wait_ack):
                return True
            raise BadAckException()

    def check_ack(self, wait_ack):
        '''Read and check acknowledgement.'''
        ack = self.link.read(len(wait_ack))
        if wait_ack == ack:
            message = "Check ACK: OK (%s == %s)" % (repr(wait_ack), repr(ack))
            LOGGER.info(message)
            return True
        else:
            message = "Check ACK: BAD (%s != %s)" % (repr(wait_ack), repr(ack))
            LOGGER.error(message)
            return False

    @cached_property(ttl=3600)
    def firmware_date(self):
        '''Return the firmware date code'''
        self.run_cmd("VER", self.OK)
        data = self.link.read(13)
        return datetime.strptime(data.strip('\n\r'), '%b %d %Y').date()

    @cached_property(ttl=3600)
    def firmware_version(self):
        '''Return the firmware version as string'''
        self.run_cmd("NVER", self.OK)
        data = self.link.read()
        return data.strip('\n\r')

    def get_time(self):
        '''Return the current date on the console.'''
        self.run_cmd("GETTIME", self.ACK)
        data = self.link.read(8, is_byte=True)
        return unpack_datetime(data)

    def set_time(self, dtime):
        '''Set the datetime `dtime` on the console.'''
        self.run_cmd("SETTIME", self.ACK)
        self.run_cmd(pack_datetime(dtime), self.ACK, is_byte=True)

    time = property(get_time, set_time, "VantagePro2 date on the console")

    @cached_property(ttl=3600)
    def diagnostics(self):
        '''Return the Console Diagnostics report :
            - Total packets received.
            - Total packets missed.
            - Number of resynchronizations.
            - The largest number of packets received in a row.
            - The number of CRC errors detected.
        All values are recorded since midnight, or since the diagnostics are
        cleared manualy.'''
        self.run_cmd("RXCHECK", self.OK)
        data = self.link.read().strip('\n\r').split(' ')
        data = [int(i) for i in data]
        return dict(total_received = data[0], total_missed = data[1],
                    resyn = data[2], max_received = data[3],
                    crc_errors = data[4])

    def get_current_data(self):
        '''Get real-time data.'''
        self.run_cmd("LOOP 1", self.ACK)
        data = self.link.read(99, is_byte=True)
        return LoopDataParserRevB(data)

    def get_archives(self, start_date=None, stop_date=None):
        '''Get archive records until `start_date` and `stop_date`.'''
        return ListDataDict(self.get_archives_generator(start_date, stop_date))

    def get_archives_generator(self, start_date=None, stop_date=None):
        '''Get archive records until `start_date` and `stop_date` with
        generator.'''
        # 2000-01-01 0:00:01
        # start_date = start_date or datetime(2012, 6, 8, 15, 20, 0)
        start_date = start_date or datetime(2000, 1, 1, 0, 0, 1)
        self.run_cmd("DMPAFT", self.ACK)
        # I think that date_time_crc is incorrect...
        self.link.write(pack_dmp_date_time(start_date), is_byte=True)
        # timeout must be at least 2 seconds
        timeout = (self.link.timeout or 1) * 2
        ack = self.link.read(len(self.ACK), timeout=timeout)
        if ack != self.ACK:
            raise BadAckException()
        # Read dump header and get number of pages
        header = DmpHeaderParser(self.link.read(8, is_byte=True))
        # Write ACK if crc is good. Else, send cancel.
        if header.crc_error:
            self.link.write(self.CANCEL)
            raise BadCRCException()
        else:
            self.link.write(self.ACK)
        LOGGER.info('Begin downloading %d dump pages' % header['Pages'])
        finish = False
        r_index = 0
        for i in range(header['Pages']):
            # Read one dump page
            raw_dump = self.link.read(267, is_byte=True)
            # Parse dump page
            dump = DmpPageParser(raw_dump)
            LOGGER.info('Dump page no %d ' % dump['Index'])
            # Get the 5 raw records
            raw_records = dump["Records"]
            # loop through archive records
            offsets = zip(range(0, 260, 52), range(52, 261, 52))
            # offsets = [(0, 52), (52, 104), ... , (156, 208), (208, 260)]
            for offset in offsets:
                raw_record = raw_records[offset[0]:offset[1]]
                record = ArchiveDataParserRevB(raw_record)
                # verify that record has valid data, and store
                r_time = record['Datetime']
                if r_time is None:
                    LOGGER.error('Invalid record detected')
                    finish = True
                    break
                record.crc_error = dump.crc_error
                LOGGER.info("Record-%.4d - Datetime : %s" % (r_index, r_time))
                yield record
                r_index += 1
            if finish:
                LOGGER.info('Canceling download')
                self.link.write(self.ESC)
                break
            else:
                if header['Pages'] - 1 == i:
                    LOGGER.info('Start downloading next page')
                self.link.write(self.ACK)
        LOGGER.info('Pages Downloading process was finished')
