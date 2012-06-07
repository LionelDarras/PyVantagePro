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
from ..utils import (cached_property, retry)

class TestCachedProperty:
    ''' Test cached_property decorator.'''

    @cached_property()
    def random_bool(self):
        '''Return random bool'''
        return bool(random.getrandbits(1))

    def test_cached_property(self):
        '''Test cached_property decorator.'''
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
        '''Return random bool'''
        self.retries += 1
        if self.retries == num:
            return True
        else:
            return False

    def test_cached_property(self):
        '''Test retry decorator.'''
        assert self.retries_func(3) == True
        self.retries = 0
        assert self.retries_func(5) == False
