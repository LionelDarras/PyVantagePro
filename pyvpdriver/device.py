# -*- coding: utf-8 -*-
'''
    pyvpdriver.device
    ~~~~~~~~~~~~~~~~~

    Allows data query of Davis Vantage Pro2 devices

    This part of code is inspired by PyWeather projet
    by Patrick C. McGinty <pyweather@tuxcoder.com>

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''
from __future__ import division, unicode_literals
import time
import struct
from datetime import datetime
from array import array

from .logger import LOGGER
from .utils import cached_property, retry, hex_to_byte

class NoDeviceException(Exception):
    '''Can not access weather station.'''
    value = __doc__

class BadAckException(Exception):
    '''The acknowledgement is not the one expected.'''
    value = __doc__

class DataParser(struct.Struct):
    ''' Implements a reusable class for working with a binary data structure.
    It provides a named fields interface, similiar to C structures.'''
    def __init__(self, format, order='='):
        self.fields, format_t = zip(*format)
        format_t = str("%s%s" % (order, ''.join(format_t)))
        super(DataParser,self).__init__(format_t)


    def unpack(self, buf):
        '''Unpacks data from 'buf' and returns a dication of named fields.'''
        data = self.unpack_from( buf, 0)
        item = dict(zip(self.fields,data))
        return item

class LoopDataParser(DataParser):
    # Loop data format (RevB)
    LOOP_FORMAT = (
        ('LOO',         '3s'), ('BarTrend',    'B'),  ('PacketType',  'B'),
        ('NextRec',      'H'), ('Pressure',    'H'),  ('TempIn',      'H'),
        ('HumIn',        'B'), ('TempOut',     'H'),  ('WindSpeed',   'B'),
        ('WindSpeed10Min','B'),('WindDir',     'H'),  ('ExtraTemps',  '7s'),
        ('SoilTemps',   '4s'), ('LeafTemps',  '4s'),  ('HumOut',      'B'),
        ('HumExtra',    '7s'), ('RainRate',    'H'),  ('UV',          'B'),
        ('SolarRad',     'H'), ('RainStorm',   'H'),  ('StormStartDate','H'),
        ('RainDay',      'H'), ('RainMonth',   'H'),  ('RainYear',    'H'),
        ('ETDay',        'H'), ('ETMonth',     'H'),  ('ETYear',      'H'),
        ('SoilMoist',   '4s'), ('LeafWetness','4s'),  ('AlarmIn',     'B'),
        ('AlarmRain',    'B'), ('AlarmOut' ,  '2s'),  ('AlarmExTempHum','8s'),
        ('AlarmSoilLeaf','4s'),('BatteryStatus','B'), ('BatteryVolts','H'),
        ('ForecastIcon','B'),  ('ForecastRuleNo','B'),('SunRise',     'H'),
        ('SunSet',      'H'),  ('EOL',         '2s'), ('CRC',         'H'),
    )

    def __init__(self, data):
        super(LoopDataParser,self).__init__(self.LOOP_FORMAT)
        self.data = data

    def values(self):
        item = self.unpack(self.data)

        item['Pressure'] = item['Pressure'] / 1000
        item['TempIn'] = item['TempIn'] / 10
        item['TempOut'] = item['TempOut'] / 10

        item['RainRate'] = item['RainRate']   /  100.0
        item['RainStorm']      = item['RainStorm']  /  100.0
        item['StormStartDate'] = self.unpack_storm_date(item['StormStartDate'])
        # rain totals
        item['RainDay']     = item['RainDay']   /  100.0
        item['RainMonth']   = item['RainMonth'] /  100.0
        item['RainYear']    = item['RainYear']  /  100.0
        # convert to int
        item['HumExtra']    = struct.unpack(b'7B',item['HumExtra'])
        item['ExtraTemps']  = struct.unpack(b'7B',item['ExtraTemps'])
        item['AlarmSoilLeaf'] = struct.unpack(b'4B',item['AlarmSoilLeaf'])
        item['AlarmOut'] = struct.unpack(b'2B',item['AlarmOut'])
        item['AlarmExTempHum'] = struct.unpack(b'8B',item['AlarmExTempHum'])
        item['SoilMoist']   = struct.unpack(b'4B',item['SoilMoist'])
        item['SoilTemps']   = struct.unpack(b'4B',item['SoilTemps'])
        item['LeafWetness'] = struct.unpack(b'4B',item['LeafWetness'])
        item['LeafTemps'] = struct.unpack(b'4B',item['LeafTemps'])
        # evapotranspiration totals
        item['ETDay']       = item['ETDay']     / 1000.0
        item['ETMonth']     = item['ETMonth']   /  100.0
        item['ETYear']      = item['ETYear']    /  100.0
        # battery statistics
        item['BatteryVolts'] = item['BatteryVolts'] * 300 / 512.0 / 100.0
        # sunrise / sunset
        item['SunRise'] = self.unpack_time( item['SunRise'] )
        item['SunSet']  = self.unpack_time( item['SunSet'] )
        del item['LOO']
        del item['NextRec']
        del item['PacketType']
        del item['EOL']
        del item['CRC']
        return item

    def unpack_storm_date(self, date):
        '''Given a packed storm date field, unpack and return date.'''
        year  = (date & 0x7f) + 2000        # 7 bits
        day   = (date >> 7) & 0x01f         # 5 bits
        month = (date >> 12) & 0x0f         # 4 bits
        return "%s-%s-%s" % (year, month, day)

    def unpack_time(self, time):
        '''Given a packed time field, unpack and return "HH:MM" string.'''
        # format: HHMM, and space padded on the left.ex: "601" is 6:01 AM
        return "%02d:%02d" % divmod(time,100)  # covert to "06:01"


class VantagePro2(object):
    '''A class capable of reading raw (binary) weather data from a
    Vantage Pro 2 console.'''
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
        if (self.last_wake_up is None or
                self.last_wake_up + self.WAKE_TIME < time.time()):
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
        '''Read and check ACK.'''
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
        self.verify_checksum(data)
        s, m, h, day, month, year = struct.unpack(b'>BBBBBB', data[:6])
        return datetime(year+1900, month, day, h, m, s)

    def set_time(self, dtime):
        '''Set the datetime `dtime` on the console.'''
        date = struct.pack(b'>BBBBBB', dtime.second, dtime.minute,
                                           dtime.hour, dtime.day,
                                           dtime.month, dtime.year - 1900)
        # crc in big-endian format
        checksum = struct.pack(b'>H',self.get_checksum(date))
        self.run_cmd("SETTIME", self.ACK)
        self.run_cmd(b''.join([date, checksum]), self.ACK, is_byte=True)

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
#        data = str("4c4f4f14003e032175da0239d10204056301ffffffffffffffffffff" \
#                "ffffffffff4effffffffffffff0000ffff7f0000ffff000000000000" \
#                "000000000000ffffffffffffff000000000000000000000000000000" \
#                "0000002703064b26023e070a0d1163")
#        data = hex_to_byte(data)
        self.run_cmd("LOOP 1", self.ACK)
        data = self.link.read(99, is_byte=True)
        self.verify_checksum(data)
        item = LoopDataParser(data).values()
        return [item]

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
