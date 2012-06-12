# coding: utf8
'''
    pyvantagepro.utils
    ------------------

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''
from __future__ import unicode_literals
import sys
import os
import time
import csv
import binascii
import struct
from blist import sorteddict
from xml.dom.minidom import parseString

# Type compatibilite between python3 and python2
if sys.version_info[0] >= 3:
    # Python 3
    import io as StringIO
    text_type = str
    byte_type = bytes
else:
    # Python 2
    text_type = unicode
    byte_type = str
    import cStringIO as StringIO


def is_text(data):
    return isinstance(data, text_type)


def is_bytes(data):
    return isinstance(data, byte_type)


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
                    if ret:
                        return ret
                    elif i == self.tries - 1:
                        return ret
                except Exception as e:
                    if i == self.tries - 1:
                        # last chance
                        raise e
                if self.delay > 0:
                    time.sleep(self.delay)

        return wrapped_f


def byte_to_string(byte):
    '''Convert a byte string to it's hex string representation.'''
    if sys.version_info[0] >= 3:
        hexstr = str(binascii.hexlify(byte), "utf-8")
    else:
        hexstr = str(binascii.hexlify(byte))
    data = []
    for i in range(0, len(hexstr), 2):
        data.append("%s" % hexstr[i:i + 2].upper())
    return ' '.join(data)


def byte_to_binary(byte):
    '''Convert byte to binary string representation.
    E.g.
    >>> hex_to_binary_string("\x4A")
    '0000000001001010'
    '''
    return ''.join(str((byte & (1 << i)) and 1) for i in reversed(range(8)))


def bytes_to_binary(list_bytes):
    '''Convert bytes to binary string representation.
    E.g.
    >>> hex_to_binary_string(b"\x4A\xFF")
    '0100101011111111'
    '''
    if sys.version_info[0] >= 3:
        # TODO: Python 3 convert \x00 to integer 0 ?
        if list_bytes == 0:
            data = '00000000'
        else:
            data = ''.join([byte_to_binary(b) for b in list_bytes])
    else:
        data = ''.join(byte_to_binary(ord(b)) for b in list_bytes)
    return data


def hex_to_binary(hexstr):
    '''Convert hexadecimal string to binary string representation.
    E.g.
    >>> hex_to_binary_string("FF")
    '11111111'
    '''
    if sys.version_info[0] >= 3:
        return ''.join(byte_to_binary(b) for b in hex_to_byte(hexstr))
    return ''.join(byte_to_binary(ord(b)) for b in hex_to_byte(hexstr))

def bin_to_integer(buf, start=0, stop=None):
    '''Convert binary string representation to integer.
    E.g.
    >>> bin_to_integer('1111110')
    126
    >>> bin_to_integer('1111110', 0, 2)
    2
    >>> bin_to_integer('1111110', 0, 3)
    6
    '''
    return int(buf[::-1][start:(stop or len(buf))][::-1], 2)


def hex_to_byte(hexstr):
    '''Convert a string hex byte values into a byte string.'''
    return binascii.unhexlify(hexstr.replace(' ', '').encode('utf-8'))


def csv_to_dict(file_input, delimiter=','):
    '''Deserialize csv to list of dictionaries.'''
    delimiter = str(delimiter)
    table = []
    reader = csv.DictReader(file_input, delimiter=delimiter, skipinitialspace=True)
    for d in reader:
        table.append(d)
    return ListDict(table)


def dict_to_csv(items, delimiter, header):
    '''Serialize list of dictionaries to csv.'''
    content = ""
    if len(items) > 0:
        delimiter = str(delimiter)
        output = StringIO.StringIO()
        csvwriter = csv.DictWriter(output, fieldnames=items[0].keys(),
                                   delimiter=delimiter)
        if header:
            csvwriter.writerow(dict((key,key) for key in items[0].keys()))
            # writeheader is not supported in python2.6
            # csvwriter.writeheader()
        for item in items:
          csvwriter.writerow(dict(item))

        content = output.getvalue()
        output.close()
    return content


def dict_to_xml(items, root, key_title):
    '''Serialize a list of dictionaries to XML.'''
    xml = ''
    if len(items) > 0:
        for i, item in enumerate(items):
            if key_title is not None:
                try:
                    title = normalize_string(item[key_title])
                except:
                    title = "%d" % i
            else:
                title = "%d" % i
            xml = "%s<Data-%s>" % (xml, title)
            for key, value in item.items():
                    key = "%s" % key
                    value = "%s" % value
                    xml = "%s<%s>%s</%s>" % (xml, key, value, key)
            xml = "%s</Data-%s>" % (xml, title)
        xml = "<%s>%s</%s>" % (root, xml, root)
        xml = parseString(xml).toprettyxml()
    return xml


class Dict(object):
    '''Implements sorteddict with somes additional methods.'''
    def __init__(self, initial_dict = None):
        initial_dict = initial_dict or {}
        self.store = sorteddict(initial_dict)

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def copy(self):
        return Dict(self)

    def keys(self):
        return self.store.keys()

    def values(self):
        return self.store.values()

    def items(self):
        return self.store.items()

    def __contains__(self, key):
        return key in self.store.keys()

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def filter(self, keys):
        data = self.store.copy()
        unused_keys = set(data.keys()) - set(keys)
        for key in unused_keys:
            del data[key]
        return Dict(data)

    def to_xml(self, root="VantagePro", key_title="Datetime"):
        return dict_to_xml([self.store], root, key_title)

    def to_csv(self, delimiter=',', header=True):
        return dict_to_csv([self.store], delimiter, header)

    def __unicode__(self):
        return "%s" % self.store

    def __str__(self):
        return "%s" % self.store.__str__()

    def __repr__(self):
        return self.store.__repr__()


class ListDict(list):
    '''Implements list of sorteddicts with somes additional methods.'''
    def to_xml(self, root="VantagePro", key_title="Datetime"):
        return dict_to_xml(list(self), root, key_title)

    def to_csv(self, delimiter=',', header=True):
        return dict_to_csv(list(self), delimiter, header)

    def filter(self, keys):
        return list(self.filter_generator(keys))

    def filter_generator(self, keys):
        for item in self:
            data = item.copy()
            unused_keys = set(data.keys()) - set(keys)
            for key in unused_keys:
                del data[key]
            yield Dict(data)

    def sorted_by(self, keyword, reverse=False):
        return ListDict(sorted(self, key=lambda k: k[keyword],
                                     reverse=reverse))


def normalize_string(string):
    '''Remove special char in string'''
    import unicodedata
    string = "%s" % string
    string = string.replace('\'', '-')
    string = string.replace(':', '-')
    string = unicodedata.normalize('NFKD', string)
    string = string.replace(' ','_').lower()
    final_string = string
    for char in string:
        if not unicodedata.category(char) in ['Nd','Ll','Pd','Pc']:
            final_string = final_string.replace(char,'')
    final_string = final_string.lower().replace('_','-')
    while final_string.find('--') != -1:
        final_string = final_string.replace('--','-')
    return final_string
