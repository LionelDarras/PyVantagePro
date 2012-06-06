# coding: utf8
'''
    pyvantagepro.tests.test_link
    ----------------------------

    The pyvantagepro test suite.

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

from __future__ import division, unicode_literals

from . import LOGGER
from ..device import LoopDataParserRevB
from ..utils import hex_to_byte

class TestLoopParser:
    ''' Test parser.'''
    def setup_class(self):
        '''Setup common data.'''
        data =  str("4c4f4f14003e032175da0239d10204056301ffffffffffffffff" \
                "ffffffffffffff4effffffffffffff0000ffff7f0000ffff00000000" \
                "0000000000000000ffffffffffffff00000000000000000000000000" \
                "00000000002703064b26023e070a0d1163")
        self.data = hex_to_byte(data)

    def test_unpack(self):
        '''Test unpack loop packet.'''
        item = LoopDataParserRevB(self.data)
        assert item["TempIn"] == 73.0
