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
        # flush reception buffer
#        self.link.read()

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
        # 1. init empty records
        records = ListDataDict()
        # 2012-06-08 10:00:00
        start_date = start_date or datetime(2012, 6, 8, 10, 30, 0)
        self.run_cmd("DMPAFT", self.ACK)
        self.link.write(pack_dmp_date_time(start_date), is_byte=True)
        if not self.check_ack(self.ACK):
            raise BadAckException()
        # 5. read header data
        header = DmpHeaderParser(self.link.read(8, is_byte=True))
        # Write ACK
        if header.crc_error:
            raise BadCRCException()
        else:
            self.link.write(self.ACK)
        LOGGER.info('try reading %d dmp pages' % header['Pages'])
        old_record_datetime = None
        finish = False
        for i in range(header['Pages']):
            # 5. read page data
            raw_dump = self.link.read(267, is_byte=True)
            dump = DmpPageParser(raw_dump)
            LOGGER.info('Dump page no %d ' % dump['Index'])
            raw_records = dump["Records"]
            self.link.write(self.ACK)
            # 6. loop through archive records
            offsets = zip(range(0, 260, 52), range(52, 261, 52))
            for offset in offsets:
                raw_record = raw_records[offset[0]:offset[1]]
                record = ArchiveDataParserRevB(raw_record)
                print ">>>>> record['Datetime'] = %s" % record['Datetime']
                if record['Datetime'] is not None:
                    if old_record_datetime is not None:
                        if record['Datetime'] < old_record_datetime:
                            finish = True
                            break
                    # 7. verify that record has valid data, and store
                    record.crc_error = dump.crc_error
                    records.append(record)
                else:
                    finish = True
                    break
                old_record_datetime = record['Datetime']
            if finish:
                break
        self.link.write(self.ESC)
        data = self.link.read(is_byte=True)
        dump = DmpPageParser(data)
        LOGGER.info('Dump page no %d ' % dump['Index'])
        LOGGER.info('pages download finish')
        return records
