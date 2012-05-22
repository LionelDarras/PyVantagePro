# coding: utf8
"""
    pyvpdriver.device
    ~~~~~~~~~~~~~~~~~

     Allows data query of Davis Vantage Pro2 devices

    This part of code is inspired by PyWeather projet
    by Patrick C. McGinty <pyweather@tuxcoder.com>

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

"""

from datetime import datetime, timedelta
import time

from logger import LOGGER
from utils import cached_property

class NoDeviceException(Exception):
    """Can not access weather station."""
    value = __doc__

class BadAckException(Exception):
    """The acknowledgement is not the one expected."""
    value = __doc__

class VantagePro(object):
    '''
    A class capable of reading raw (binary) weather data from a
    vantage pro console.
    '''
    def __init__(self, link):
        self.link = link
        self.last_wake_up = None

    # device reply commands
    WAKE_TIME = timedelta(seconds = 2*60)
    WAKE_STR = '\n'
    WAKE_ACK = '\n\r'
    ACK = '\x06'
    NACK = '\x21'
    DONE = ''
    ESC = '\x1b'
    OK = '\n\rOK\n\r'

    def wake_up(self):
        """Wakeup the console."""
        for i in xrange(3):
            LOGGER.info("try wake up console %d" % (i+1))
            self.link.write(self.WAKE_STR)
            ack = self.link.read(len(self.WAKE_ACK))
            if ack == self.WAKE_ACK:
                self.last_wake_up = datetime.now()
                return ack
        time.sleep(1)
        raise NoDeviceException

    def run_cmd(self, cmd, wait_ack=None):
        '''Write a single command. If `wait_ack` is not None, the function must
        check that acknowledgement is the one expected.'''
        if self.last_wake_up is None:
            self.wake_up()
        elif self.last_wake_up + self.WAKE_TIME < datetime.now():
            self.wake_up()
        LOGGER.info("try send: " + cmd)
        self.link.write( cmd + '\n')
        if wait_ack is not None:
            ack = self.link.read(len(wait_ack))
            if wait_ack == ack:
                return
            raise BadAckException()
        return

    @cached_property
    def version(self):
        """Return the firmware date code"""
        self.run_cmd("VER", self.OK)
        data = self.link.read()
        return datetime.strptime(data.strip('\n\r'), '%b %d %Y').date()

    @cached_property
    def diagnostics(self):
        """Return the Console Diagnostics report :
            - Total packets received.
            - Total packets missed.
            - Number of resynchronizations.
            - The largest number of packets received in a row.
            - The number of CRC errors detected.
        All values are recorded since midnight, or since the diagnostics are
        cleared manualy."""
        self.run_cmd("RXCHECK", self.OK)
        data = self.link.read().strip('\n\r').split(' ')
        data = [int(i) for i in data]
        return dict(total_received = data[0], total_missed = data[1],
                    resyn = data[2], max_received = data[3],
                    crc_errors = data[4])

    def __del__(self):
        """Close link when object is deleted."""
        self.link.close()
