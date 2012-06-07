# coding: utf8
'''
    pyvantagepro.tests.test_link
    ----------------------------

    The pyvantagepro test suite.

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

from __future__ import unicode_literals
from datetime import datetime

from . import LOGGER
import random
from ..utils import (cached_property, retry, DataDict, hex_to_byte,
                     byte_to_string, bytes_to_binary, hex_to_binary,
                     bin_to_integer)


def test_data_dict():
    '''Tests DataDict.'''
    d = DataDict()
    d["f"] = "222"
    d["a"] = "111"
    # sorteddict({'a': '111', 'f': '222'})
    assert d.keys().index('a') == 0
    assert d.keys().index('f') == 1
    d["b"] = "000"
    assert d.keys().index('a') == 0
    assert d.keys().index('b') == 1
    assert d.keys().index('f') == 2

    assert "a" in d.filter(['a', 'b'])
    assert "b" in d.filter(['a', 'b'])
    assert "f" not in d.filter(['a', 'b'])
    new_d = d.filter(['a', 'f'])
    assert "a,f\r\n111,222\r\n" == new_d.to_csv()
    xml = new_d.to_xml().replace("\t", "").replace('\n', '').replace(' ', '')
    assert xml == '<?xmlversion="1.0"?><VantagePro>'\
                  '<Data-0><a>111</a><f>222</f></Data-0>'\
                  '</VantagePro>'


class TestCachedProperty:
    ''' Tests cached_property decorator.'''

    @cached_property()
    def random_bool(self):
        '''Returns random bool'''
        return bool(random.getrandbits(1))

    def test_cached_property(self):
        '''Tests cached_property decorator.'''
        value1 = self.random_bool
        value2 = self.random_bool
        assert value1 == value2


class TestRetry:
    '''Test retry decorator.'''
    def setup_class(self):
        '''Setup common data.'''
        self.retries = 0

    @retry(tries=3, delay=0)
    def retries_func(self, num):
        '''Returns random bool.'''
        self.retries += 1
        if self.retries == num:
            return True
        else:
            return False

    def test_cached_property(self):
        '''Tests retry decorator.'''
        assert self.retries_func(3) == True
        self.retries = 0
        assert self.retries_func(5) == False


def test_byte_to_string():
    '''Tests byte <-> hex and hex <-> byte.'''
    assert byte_to_string(b"\xFF") == "FF"
    assert hex_to_byte(byte_to_string(b"\x4A")) == b"\x4A"
    assert byte_to_string(hex_to_byte("4A")) == "4A"


def test_bytes_binary():
    '''Tests byte <-> binary and binary <-> byte.'''
    assert bytes_to_binary(b'\xFF\x00') == "1111111100000000"
    assert bytes_to_binary(b'\x00\x00') == "0000000000000000"


def test_hex_binary():
    '''Tests hex <-> binary and binary <-> hex.'''
    assert hex_to_binary('FF00') == "1111111100000000"
    assert hex_to_binary('0000') == "0000000000000000"


def test_bin_integer():
    '''Tests bin <-> int conversion.'''
    hexstr = "11111110"
    assert bin_to_integer(hexstr) == 254
    assert bin_to_integer(hexstr, 0, 1) == 0
    assert bin_to_integer(hexstr, 0, 2) == 2
    assert bin_to_integer(hexstr, 0, 3) == 6
