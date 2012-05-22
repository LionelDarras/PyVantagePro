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
        '''
        Write a single command. If `wait_ack` is not None, the function must
        check that acknowledgement is the one expected.
        '''
        if self.last_wake_up is None:
            self.wake_up()
        elif self.last_wake_up + self.WAKE_TIME < datetime.now():
            self.wake_up()
        LOGGER.info("try send: " + cmd)
        self.link.write( cmd + '\n')
#        time.sleep(1)
        if wait_ack is not None:
            ack = self.link.read(len(wait_ack))
            if wait_ack == ack:
                return
            raise BadAckException()

    @property
    def version(self):
        self.run_cmd("VER", self.OK)
        return self.link.read()

    def __del__(self):
        """Close link when object is deleted."""
        self.link.close()
