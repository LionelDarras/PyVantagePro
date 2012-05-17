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

from logger import LOGGER

class NoDeviceException(Exception):
    """Can not access weather station."""
    value = __doc__

class VantagePro(object):
    '''
    A class capable of reading raw (binary) weather data from a
    vantage pro console.
    '''
    def __init__(self, link):
        self.link = link

    # device reply commands
    WAKE_ACK = '\n\r'
    ACK = '\x06'
    ESC = '\x1b'
    OK = '\n\rOK\n\r'

    def wake_up(self):
        """Wakeup the console."""
        LOGGER.info("send: WAKEUP")
        for i in xrange(3):
            self.link.write('\n')
            ack = self.link.read(len(self.WAKE_ACK))
            LOGGER.info("recv: %s", ack)
            if ack == self.WAKE_ACK:
                return
        raise NoDeviceException

    def __del__(self):
        """Close link when object is deleted."""
        self.link.close()
