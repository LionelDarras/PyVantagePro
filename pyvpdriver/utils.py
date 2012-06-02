# coding: utf8
'''
    pyvpdriver.utils
    ~~~~~~~~~~~~~~~~

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''
from __future__ import division, unicode_literals
import sys
import os
import time
import csv
if sys.version_info[0] >= 3:
    # Python 3
    import io as StringIO
else:
    # Python 2
    import cStringIO as StringIO

from xml.dom.minidom import parseString

class cached_property(object):
    '''A decorator that converts a function into a lazy property evaluated
    only once within TTL period. The function wrapped is called the first
    time to retrieve the result and then that calculated result is used
    the next time you access the value.

    The default time-to-live (TTL) is 300 seconds (5 minutes). Set the TTL to
    zero for the cached value to never expire.

    To expire a cached property value manually just do::

        del instance._cache[<property name>]

    Stolen from:
    http://wiki.python.org/moin/PythonDecoratorLibrary#Cached_Properties
    '''
    def __init__(self, ttl=300):
        self.ttl = ttl

    def __call__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__
        return self

    def __get__(self, inst, owner):
        now = time.time()
        try:
            value, last_update = inst._cache[self.__name__]
            if self.ttl is not None:
                if self.ttl > 0 and now - last_update > self.ttl:
                    raise AttributeError
        except (KeyError, AttributeError):
            value = self.fget(inst)
            try:
                cache = inst._cache
            except AttributeError:
                cache = inst._cache = {}
            cache[self.__name__] = (value, now)
        return value

class retry(object):
    '''Retries a function or method until it returns True.
    delay sets the initial delay in seconds, and backoff sets the factor by
    which the delay should lengthen after each failure.
    Tries must be at least 0, and delay greater than 0.'''

    def __init__(self, tries=3, delay=1):
        self.tries = tries
        self.delay = delay

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            for i in range(self.tries):
                try:
                    ret = f(*args, **kwargs)
                    if ret == True:
                        return True
                    elif i == self.tries - 1:
                        return ret
                except Exception as e:
                    if i == self.tries - 1:
                        # last chance
                        raise e
                if self.delay > 0:
                    time.sleep(self.delay)

        return wrapped_f

def byte_to_int(s):
    '''return the integer value of a hexadecimal byte s'''
    return int("%02X " % ord( s ),  16)

def byte_to_string(byte):
    '''Convert a byte string to it's hex string representation.'''
    return ''.join( [ "%02X " % ord( x ) for x in byte ] ).strip()

def hex_to_binary_string(buf, num_of_bits):
    """Convert byte to binary string representation.
    e.g.
    >>> hex_to_binary_string("FF", 8)
    '11111111'
    >>> 
    >>> hex_to_binary_string("4A", 16)
    '0000000001001010'
    """
    scale = 16 ## equals to hexadecimal
    return bin(int(buf, scale))[2:].zfill(num_of_bits)

def bin_to_integer(buf, start=0, stop=None):
    """Convert binary string representation to integer.
    e.g.
    >>> bin_to_integer('1111110')
    126
    >>> bin_to_integer('1111110', 0, 2)
    2
    >>> bin_to_integer('1111110', 0, 3)
    6
    >>> 
    """
    if stop is None:
        stop = len(buf)
    return int(buf[::-1][start:stop][::-1], 2)

def hex_to_byte( hexstr ):
    """Convert a string hex byte values into a byte string.
    The Hex Byte values mayor may not be space separated."""
    bytes = []
    
    hexstr = hexstr.replace(' ', '')
    for i in range(0, len(hexstr), 2):
        bytes.append( chr( int (hexstr[i:i+2], 16 ) ) )
    return b''.join(bytes)

def dict_to_csv(items, delimiter=',', quotechar='"'):
    '''Serialize list of dictionaries to csv'''
    output = StringIO.StringIO()
    csvwriter = csv.DictWriter(output, fieldnames=items[0].keys(),
                               delimiter=delimiter, quotechar=quotechar)
    csvwriter.writeheader()
    for item in items:
      csvwriter.writerow(item)

    content = output.getvalue()
    output.close()
    return content

def dict_to_xml(items, root="vantagepro2"):
    '''Serialize a list of dictionaries to XML'''
    xml = ''
    for i, item in enumerate(items):
        xml = "%s<data%d>" % (xml, i)
        for key, value in item.iteritems():
            xml = "%s<%s>%s</%s>" % (xml, str(key), str(value), str(key))
        xml = "%s</data%d>" % (xml, i)
    xml = "<%s>%s</%s>" % (root, xml, root)
    return parseString(xml).toprettyxml()

def fahrenheit_to_celsius(f):
    'Degrees Fahrenheit (F) to degrees Celsius (C)'
    return (f - 32.0) * 0.555556
