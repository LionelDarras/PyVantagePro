# -*- coding: utf-8 -*-
'''
    pyvantagepro.parser
    -------------------

    Allows parsing Vantage Pro2 data.

    Original Author: Patrick C. McGinty (pyweather@tuxcoder.com)
    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''
from __future__ import division, unicode_literals
import struct
from datetime import datetime
from array import array

from .logger import LOGGER
from .utils import (cached_property, byte_to_string, DataDict,
                    bytes_to_binary, bin_to_integer)


class VantageProCRC(object):
    '''Implements CRC algorithm, necessary for encoding and verifying data from
    the Davis Vantage Pro unit.'''
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

    def __init__(self, data):
        self.data = data

    @cached_property()
    def checksum(self):
        '''Return CRC calc value from raw serial data.'''
        crc = 0
        for byte in array(str('B'), self.data):
            crc = (self.CRC_TABLE[ (crc >> 8) ^ byte ] ^ ((crc & 0xFF) << 8))
        return crc

    @cached_property()
    def data_with_checksum(self):
        '''Return packed raw CRC from raw data.'''
        checksum = struct.pack(b'>H', self.checksum)
        return b''.join([self.data, checksum])

    def check(self):
        '''Perform CRC check on raw serial data, return true if valid.
        A valid CRC == 0.'''
        if len(self.data) != 0 and self.checksum == 0:
            LOGGER.info("Check CRC : OK")
            return True
        else:
            LOGGER.error("Check CRC : BAD")
            return False


class DataParser(DataDict):
    '''Implements a reusable class for working with a binary data structure.
    It provides a named fields interface, similiar to C structures.'''

    def __init__(self, data, data_format, order='='):
        self.fields, format_t = zip(*data_format)
        self.crc_error = False
        if "CRC" in self.fields:
            self.crc_error = not VantageProCRC(data).check()
        format_t = str("%s%s" % (order, ''.join(format_t)))
        self.struct = struct.Struct(format = format_t)

        self.raw_bytes = data
        # Unpacks data from `raw_bytes` and returns a dication of named fields
        data = self.struct.unpack_from(self.raw_bytes, 0)
        super(DataParser, self).__init__(dict(zip(self.fields, data)))

    @cached_property()
    def raw(self):
        return byte_to_string(self.raw_bytes)

    def tuple_to_dict(self, key):
        '''Convert {key<->tuple} to {key1<->value2, key2<->value2 ... }.'''
        for i, value in enumerate(self[key]):
            self["%s%.2d" % (key, i+1)] = value
        del self[key]

    def __unicode__(self):
        name = self.__class__.__name__
        return "<%s %s>" % (name, self.raw)

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return str(self.__unicode__())

class LoopDataParserRevB(DataParser):
    '''Parse data returned by the 'LOOP' command. It contains all of the
    real-time data that can be read from the Davis VantagePro2.'''
    # Loop data format (RevB)
    LOOP_FORMAT = (
        ('LOO',         '3s'), ('BarTrend',    'B'),  ('PacketType',  'B'),
        ('NextRec',      'H'), ('Barometer',   'H'),  ('TempIn',      'H'),
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
        super(LoopDataParserRevB, self).__init__(data, self.LOOP_FORMAT)
        self['Date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self['Barometer'] = self['Barometer'] / 1000
        self['TempIn'] = self['TempIn'] / 10
        self['TempOut'] = self['TempOut'] / 10
        self['RainRate'] = self['RainRate'] / 100
        self['RainStorm'] = self['RainStorm'] / 100
        # Given a packed storm date field, unpack and return date
        self['StormStartDate'] = self.unpack_storm_date()
        # rain totals
        self['RainDay'] = self['RainDay'] / 100
        self['RainMonth'] = self['RainMonth'] / 100
        self['RainYear'] = self['RainYear'] / 100
        # evapotranspiration totals
        self['ETDay'] = self['ETDay'] / 1000
        self['ETMonth'] = self['ETMonth'] / 100
        self['ETYear'] = self['ETYear'] / 100
        # battery statistics
        self['BatteryVolts'] = self['BatteryVolts'] * 300 / 512 / 100
        # sunrise / sunset
        self['SunRise'] = self.unpack_time(self['SunRise'])
        self['SunSet'] = self.unpack_time(self['SunSet'])
        # convert to int
        self['HumExtra']    = struct.unpack(b'7B', self['HumExtra'])
        self['ExtraTemps']  = struct.unpack(b'7B', self['ExtraTemps'])
        self['SoilMoist']   = struct.unpack(b'4B', self['SoilMoist'])
        self['SoilTemps']   = struct.unpack(b'4B', self['SoilTemps'])
        self['LeafWetness'] = struct.unpack(b'4B', self['LeafWetness'])
        self['LeafTemps'] = struct.unpack(b'4B', self['LeafTemps'])

        # Inside Alarms bits extraction, only 7 bits are used
        self['AlarmIn'] = bytes_to_binary(self.raw_bytes[70])
        self['AlarmInFallBarTrend'] = int(self['AlarmIn'][0])
        self['AlarmInRisBarTrend'] = int(self['AlarmIn'][1])
        self['AlarmInLowTemp'] = int(self['AlarmIn'][2])
        self['AlarmInHighTemp'] = int(self['AlarmIn'][3])
        self['AlarmInLowHum'] = int(self['AlarmIn'][4])
        self['AlarmInHighHum'] = int(self['AlarmIn'][5])
        self['AlarmInTime'] = int(self['AlarmIn'][6])
        del self['AlarmIn']
        # Rain Alarms bits extraction, only 5 bits are used
        self['AlarmRain'] = bytes_to_binary(self.raw_bytes[71])
        self['AlarmRainHighRate'] = int(self['AlarmRain'][0])
        self['AlarmRain15min'] = int(self['AlarmRain'][1])
        self['AlarmRain24hour'] = int(self['AlarmRain'][2])
        self['AlarmRainStormTotal'] = int(self['AlarmRain'][3])
        self['AlarmRainETDaily'] = int(self['AlarmRain'][4])
        del self['AlarmRain']
        # Oustide Alarms bits extraction, only 13 bits are used
        self['AlarmOut'] = bytes_to_binary(self.raw_bytes[72])
        self['AlarmOutLowTemp'] = int(self['AlarmOut'][0])
        self['AlarmOutHighTemp'] = int(self['AlarmOut'][1])
        self['AlarmOutWindSpeed'] = int(self['AlarmOut'][2])
        self['AlarmOut10minAvgSpeed'] = int(self['AlarmOut'][3])
        self['AlarmOutLowDewpoint'] = int(self['AlarmOut'][4])
        self['AlarmOutHighDewPoint'] = int(self['AlarmOut'][5])
        self['AlarmOutHighHeat'] = int(self['AlarmOut'][6])
        self['AlarmOutLowWindChill'] = int(self['AlarmOut'][7])
        self['AlarmOut'] = bytes_to_binary(self.raw_bytes[73])
        self['AlarmOutHighTHSW'] = int(self['AlarmOut'][0])
        self['AlarmOutHighSolarRad'] = int(self['AlarmOut'][1])
        self['AlarmOutHighUV'] = int(self['AlarmOut'][2])
        self['AlarmOutUVDose'] = int(self['AlarmOut'][3])
        self['AlarmOutUVDoseEnabled'] = int(self['AlarmOut'][4])
        del self['AlarmOut']
        # AlarmExTempHum bits extraction, only 3 bits are used, but 7 bytes
        for i in range(1, 8):
            data = self.raw_bytes[74+i]
            self['AlarmExTempHum'] = bytes_to_binary(data)
            self['AlarmEx%.2dLowTemp' % i] = int(self['AlarmExTempHum'][0])
            self['AlarmEx%.2dHighTemp' % i] = int(self['AlarmExTempHum'][1])
            self['AlarmEx%.2dLowHum' % i] = int(self['AlarmExTempHum'][2])
            self['AlarmEx%.2dHighHum' % i] = int(self['AlarmExTempHum'][3])
        del self['AlarmExTempHum']
        # AlarmSoilLeaf 8bits, 4 bytes
        for i in range(1, 5):
            data = self.raw_bytes[81+i]
            self['AlarmSoilLeaf'] = bytes_to_binary(data)
            self['Alarm%.2dLowLeafWet' % i] = int(self['AlarmSoilLeaf'][0])
            self['Alarm%.2dHighLeafWet' % i] = int(self['AlarmSoilLeaf'][0])
            self['Alarm%.2dLowSoilMois' % i] = int(self['AlarmSoilLeaf'][0])
            self['Alarm%.2dHighSoilMois' % i] = int(self['AlarmSoilLeaf'][0])
            self['Alarm%.2dLowLeafTemp' % i] = int(self['AlarmSoilLeaf'][0])
            self['Alarm%.2dHighLeafTemp' % i] = int(self['AlarmSoilLeaf'][0])
            self['Alarm%.2dLowSoilTemp' % i] = int(self['AlarmSoilLeaf'][0])
            self['Alarm%.2dHighSoilTemp' % i] = int(self['AlarmSoilLeaf'][0])
        del self['AlarmSoilLeaf']
        # delete unused values
        del self['LOO']
        del self['NextRec']
        del self['PacketType']
        del self['EOL']
        del self['CRC']
        # Tuple to dict
        self.tuple_to_dict("ExtraTemps")
        self.tuple_to_dict("LeafTemps")
        self.tuple_to_dict("SoilTemps")
        self.tuple_to_dict("HumExtra")
        self.tuple_to_dict("LeafWetness")
        self.tuple_to_dict("SoilMoist")

    def unpack_storm_date(self):
        '''Given a packed storm date field, unpack and return date.'''
        date = bytes_to_binary(self.raw_bytes[48:50])
        year = bin_to_integer(date, 0, 7) + 2000
        day = bin_to_integer(date, 7, 12)
        month = bin_to_integer(date, 12, 16)
        return "%s-%s-%s" % (year, month, day)

    def unpack_time(self, time):
        '''Given a packed time field, unpack and return "HH:MM" string.'''
        # format: HHMM, and space padded on the left.ex: "601" is 6:01 AM
        return "%02d:%02d" % divmod(time,100)  # covert to "06:01"


class ArchiveDataParserRevB(DataParser):
    '''Parse data returned by the 'LOOP' command. It contains all of the
    real-time data that can be read from the Davis VantagePro2.'''

    ARCHIVE_FORMAT = (
        ('DateStamp',   'H'),  ('TimeStamp',   'H'),  ('TempOut',     'H'),
        ('TempOutHi',   'H'),  ('TempOutLow',  'H'),  ('RainRate',    'H'),
        ('RainRateHi',  'H'),  ('Barometer',    'H'), ('SolarRad',    'H'),
        ('WindSamps',   'H'),  ('TempIn',      'H'),  ('HumIn',       'B'),
        ('HumOut',      'B'),  ('WindAvg',     'B'),  ('WindHi',      'B'),
        ('WindHiDir',   'B'),  ('WindAvgDir',  'B'),  ('UV',          'B'),
        ('ETHour',      'B'),  ('SolarRadHi',  'H'),  ('UVHi',        'B'),
        ('ForecastRuleNo','B'),('LeafTemps',  '2s'),  ('LeafWetness','2s'),
        ('SoilTemps',  '4s'),  ('RecType',     'B'),  ('ExtraHum',   '2s'),
        ('ExtraTemps', '3s'),  ('SoilMoist',  '4s'),
    )

    def __init__(self, data):
        super(ArchiveDataParserRevB, self).__init__(data, self.ARCHIVE_FORMAT)
        self['raw_datestamp'] = bytes_to_binary(self.raw_bytes[0:4])
        self['Datetime'] = unpack_dmp_date_time(self['DateStamp'],
                                                self['TimeStamp'])
#        del self['DateStamp']
#        del self['TimeStamp']
        self['TempOut'] = self['TempOut'] / 10
        self['TempOutHi'] = self['TempOutHi'] / 10
        self['TempOutLow'] = self['TempOutLow'] / 10
        self['Barometer'] = self['Barometer'] / 1000
        self['TempIn'] = self['TempIn'] / 10
        self['UV'] = self['UV'] / 10
        self['ETHour'] = self['ETHour'] / 1000
        self['WindHiDir'] = int(self['WindHiDir'] * 22.5)
        self['WindHiDir'] = int(self['WindAvgDir'] * 22.5)
        self['SoilTemps'] = tuple(
                t-90 for t in struct.unpack(b'4B', self['SoilTemps']))
        self['ExtraHum'] = struct.unpack(b'2B', self['ExtraHum'])
        self['SoilMoist'] = struct.unpack(b'4B', self['SoilMoist'])
        self['LeafTemps']   = tuple(
                t-90 for t in struct.unpack(b'2B', self['LeafTemps']))
        self['LeafWetness'] = struct.unpack(b'2B', self['LeafWetness'])
        self['ExtraTemps'] = tuple(
                t-90 for t in struct.unpack(b'3B', self['ExtraTemps']))
        self.tuple_to_dict("SoilTemps")
        self.tuple_to_dict("LeafTemps")
        self.tuple_to_dict("ExtraTemps")


class DmpHeaderParser(DataParser):
    DMP_FORMAT = (
        ('Pages',   'H'),  ('Offset',   'H'),  ('CRC',     'H'),
    )

    def __init__(self, data):
        super(DmpHeaderParser, self).__init__(data, self.DMP_FORMAT)


class DmpPageParser(DataParser):
    DMP_FORMAT = (
        ('Index',   'B'),  ('Records',   '260s'),  ('unused',     '4B'),
        ('CRC',   'H'),
    )

    def __init__(self, data):
        super(DmpPageParser, self).__init__(data, self.DMP_FORMAT)


def pack_dmp_date_time(d):
    '''Pack `datetime` to DateStamp and TimeStamp VantagePro2 with CRC.'''
    vpdate = d.day + d.month * 32 + (d.year - 2000) * 512
    vptime = 100 * d.hour + d.minute
    data = struct.pack(b'HH', vpdate, vptime)
#    import pdb; pdb.set_trace()
    return VantageProCRC(data).data_with_checksum


def unpack_dmp_date_time(date, time, crc=None):
    '''Unpack `date` and `time` to datetime'''
#    print ("Recv datestamp : %s %s" % (date, time))
    if date != 0xffff and time != 0xffff:
        day   = date & 0x1f                     # 5 bits
        month = (date >> 5) & 0x0f              # 4 bits
        year  = ((date >> 9) & 0x7f) + 2000     # 7 bits
        hour, min_  = divmod(time,100)
        return datetime(year, month, day, hour, min_)


def pack_datetime(dtime):
    '''Returns packed `dtime` with CRC.'''
    data = struct.pack(b'>BBBBBB', dtime.second, dtime.minute,
                                       dtime.hour, dtime.day,
                                       dtime.month, dtime.year - 1900)
    return VantageProCRC(data).data_with_checksum

def unpack_datetime(data):
    '''Return unpacked datetime `data` and check CRC.'''
    VantageProCRC(data).check()
    s, m, h, day, month, year = struct.unpack(b'>BBBBBB', data[:6])
    return datetime(year+1900, month, day, h, m, s)
