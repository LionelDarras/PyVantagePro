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
from __future__ import unicode_literals
from datetime import datetime, timedelta
from array import array
import time
import struct

from logger import LOGGER
from utils import cached_property, byte_to_int, byte_to_string

class NoDeviceException(Exception):
    """Can not access weather station."""
    value = __doc__

class BadAckException(Exception):
    """The acknowledgement is not the one expected."""
    value = __doc__

class VantagePro(object):
    '''A class capable of reading raw (binary) weather data from a vantage pro
    console.'''
    # device reply commands
    WAKE_TIME = 2*60
    WAKE_STR = '\n'
    WAKE_ACK = '\n\r'
    ACK = '\x06'
    NACK = '\x21'
    DONE = 'DONE\n\r'
    CANCEL = '\x18'
    ESC = '\x1b'
    OK = '\n\rOK\n\r'

    CRC_TABLE = (
        0x0,    0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7, 0x8108,
        0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef, 0x1231, 0x210,
        0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6, 0x9339, 0x8318, 0xb37b,
        0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de, 0x2462, 0x3443, 0x420,  0x1401,
        0x64e6, 0x74c7, 0x44a4, 0x5485, 0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee,
        0xf5cf, 0xc5ac, 0xd58d, 0x3653, 0x2672, 0x1611, 0x630,  0x76d7, 0x66f6,
        0x5695, 0x46b4, 0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d,
        0xc7bc, 0x48c4, 0x58e5, 0x6886, 0x78a7, 0x840,  0x1861, 0x2802, 0x3823,
        0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b, 0x5af5,
        0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0xa50,  0x3a33, 0x2a12, 0xdbfd, 0xcbdc,
        0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a, 0x6ca6, 0x7c87, 0x4ce4,
        0x5cc5, 0x2c22, 0x3c03, 0xc60,  0x1c41, 0xedae, 0xfd8f, 0xcdec, 0xddcd,
        0xad2a, 0xbd0b, 0x8d68, 0x9d49, 0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13,
        0x2e32, 0x1e51, 0xe70,  0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a,
        0x9f59, 0x8f78, 0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e,
        0xe16f, 0x1080, 0xa1,   0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
        0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e, 0x2b1,
        0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256, 0xb5ea, 0xa5cb,
        0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d, 0x34e2, 0x24c3, 0x14a0,
        0x481,  0x7466, 0x6447, 0x5424, 0x4405, 0xa7db, 0xb7fa, 0x8799, 0x97b8,
        0xe75f, 0xf77e, 0xc71d, 0xd73c, 0x26d3, 0x36f2, 0x691,  0x16b0, 0x6657,
        0x7676, 0x4615, 0x5634, 0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9,
        0xb98a, 0xa9ab, 0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x8e1,  0x3882,
        0x28a3, 0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
        0x4a75, 0x5a54, 0x6a37, 0x7a16, 0xaf1,  0x1ad0, 0x2ab3, 0x3a92, 0xfd2e,
        0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9, 0x7c26, 0x6c07,
        0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0xcc1,  0xef1f, 0xff3e, 0xcf5d,
        0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8, 0x6e17, 0x7e36, 0x4e55, 0x5e74,
        0x2e93, 0x3eb2, 0xed1,  0x1ef0,
      )

    def __init__(self, link):
        self.link = link
        self.last_wake_up = None

    def get_checksum(self, data):
        '''Return CRC calc value from raw serial data.'''
        crc = 0
        for byte in array(str('B'),data):
            crc = (self.CRC_TABLE[ (crc>>8) ^ byte ] ^ ((crc&0xFF) << 8))
        return crc

    def verify_checksum(self, data):
        '''Perform CRC check on raw serial data, return true if valid.
        A valid CRC == 0.'''
        if len(data) != 0 and self.get_checksum(data) == 0:
            LOGGER.info("Check CRC : OK")
            return True
        else:
            LOGGER.error("Check CRC : BAD")
            return False

    def wake_up(self):
        """Wakeup the console."""
        for i in xrange(3):
            LOGGER.info("try wake up console (%d)" % (i+1))
            self.link.write(self.WAKE_STR)
            ack = self.link.read(len(self.WAKE_ACK))
            if ack == self.WAKE_ACK:
                self.last_wake_up = time.time()
                return ack
        raise NoDeviceException()

    def read_cmd(self, cmd, byte, i=1):
        """Read str or byte command to link."""
        message = "try send (%d)" % i
        if byte:
            LOGGER.info("%s : %s" % (message, byte_to_string(cmd)))
            self.link.write(cmd, byte)
        else:
            LOGGER.info("%s : %s" % (message, cmd))
            self.link.write("%s\n" % cmd)


    def run_cmd(self, cmd, wait_ack=None, byte=False):
        '''Write a single command. If `wait_ack` is not None, the function must
        check that acknowledgement is the one expected.'''
        if self.last_wake_up is None:
            self.wake_up()
        elif self.last_wake_up + self.WAKE_TIME < time.time():
            self.wake_up()
        if wait_ack is None:
            self.read_cmd(cmd, byte)
        else:
            for i in xrange(3):
                self.read_cmd(cmd, byte)
                if self.check_ack(wait_ack):
                    return
            raise BadAckException()

    def check_ack(self, wait_ack):
        """Read and check ACK."""
        ack = self.link.read(len(wait_ack))
        if wait_ack == ack:
            LOGGER.info("Check ACK: OK")
            return True
        else:
            LOGGER.error("Check ACK: BAD")
            return False

    @cached_property
    def version(self):
        """Return the firmware date code"""
        self.run_cmd("VER", self.OK)
        data = self.link.read()
        return datetime.strptime(data.strip('\n\r'), '%b %d %Y').date()

    def get_time(self):
        """Return the current date on the console."""
        self.run_cmd("GETTIME", self.ACK)
        bytes = self.link.read(8, byte=True)
        second = byte_to_int(bytes[0])
        minute = byte_to_int(bytes[1])
        hour = byte_to_int(bytes[2])
        day = byte_to_int(bytes[3])
        month = byte_to_int(bytes[4])
        year = byte_to_int(bytes[5])
        self.verify_checksum(bytes)
        return datetime(year+1900, month, day, hour, minute, second)

    def set_time(self, dtime):
        """Set the datetime `dtime` on the console."""
        date = struct.pack(str('>BBBBBB'), dtime.second, dtime.minute,
                                           dtime.hour, dtime.day,
                                           dtime.month, dtime.year - 1900)
        # crc in big-endian format
        checksum = struct.pack(str('>H'),self.get_checksum(date))
        self.run_cmd("SETTIME", self.ACK)
        self.run_cmd(b"".join([date, checksum]), self.ACK, byte=True)

    time = property(get_time, set_time, "VantagePro date on the console")

#    def stop_archive(self):
#        """Disables the creation of archive records."""
#        self.run_cmd("STOP")

#    def start_archive(self):
#        """Enables the creation of archive records."""
#        self.run_cmd("START")

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

    def get_data(self):
        """Get data."""
        pass

    def __del__(self):
        """Close link when object is deleted."""
        self.link.close()
