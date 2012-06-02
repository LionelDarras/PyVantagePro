# coding: utf8
'''
    pyvpdriver.tests.test_link
    --------------------------

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

from __future__ import division, unicode_literals

from ..device import LoopDataParser
from ..utils import hex_to_byte

class TestLoopParser:

    def setup_class(self):
        """Setup common data."""
        data =  str("4c4f4f14003e032175da0239d10204056301ffffffffffffffffffff" \
                "ffffffffff4effffffffffffff0000ffff7f0000ffff000000000000" \
                "000000000000ffffffffffffff000000000000000000000000000000" \
                "0000002703064b26023e070a0d1163")
        self.data = hex_to_byte(data)

    def test_unpack(self):
        """Test echo."""
        values = LoopDataParser(self.data).values()
        assert values["TempIn"] == 22.777796000000002
