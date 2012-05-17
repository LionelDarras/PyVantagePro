# coding: utf8
"""
    pyvpdriver.tests.test_test
    --------------------------

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

"""

from __future__ import division, unicode_literals


def addition(x, b):
    return x+b

class TestTest:

    def setup_class(self):
        """Setup common data."""
        pass

    def test_positive_addition(self):
        """Test addition example."""
        assert addition(3,2) == 5

    def test_negative_addition(self):
        """Test addition example."""
        assert addition(3,-3) == 0
