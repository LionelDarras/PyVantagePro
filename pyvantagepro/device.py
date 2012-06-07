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
from .utils import cached_property, retry, byte_to_string, hex_to_byte
from .parser import (LoopDataParserRevB, pack_datetime,
                    unpack_datetime)


class NoDeviceException(Exception):
    '''Can not access weather station.'''
    value = __doc__


class BadAckException(Exception):
    '''The acknowledgement is not the one expected.'''
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
            LOGGER.info("Check ACK: OK")
            return True
        else:
            LOGGER.error("Check ACK: BAD")
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

    def get_data(self, start_date=None, stop_date=None):
        '''Get archive records until `start_date` and `stop_date`.'''
        if start_date is None:
            pass
            # download all archive
        else:
            pass
            # download partial archive
        if stop_date is not None:
            pass
            # split archive
        return

    def __del__(self):
        '''Close link when object is deleted.'''
        try:
            self.link.close()
        except:
            pass
