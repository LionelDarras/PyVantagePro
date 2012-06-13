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
    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::

        class Foo(object):

            @cached_property
            def foo(self):
                # calculate something important here
                return 42

    The class has to have a `__dict__` in order for this property to
    work.

    .. versionchanged:: 0.6
       the `writeable` attribute and parameter was deprecated.  If a
       cached property is writeable or not has to be documented now.
       For performance reasons the implementation does not honor the
       writeable setting and will always make the property writeable.
    Stolen from:
    https://raw.github.com/mitsuhiko/werkzeug/master/werkzeug/utils.py
    """

    # implementation detail: this property is implemented as non-data
    # descriptor.  non-data descriptors are only invoked if there is
    # no entry with the same name in the instance's __dict__.
    # this allows us to completely get rid of the access function call
    # overhead.  If one choses to invoke __get__ by hand the property
    # will still work as expected because the lookup logic is replicated
    # in __get__ for manual invocation.

    def __init__(self, func, name=None, doc=None, writeable=False):
        if writeable:
            from warnings import warn
            warn(DeprecationWarning('the writeable argument to the '
                                    'cached property is a noop since 0.6 '
                                    'because the property is writeable '
                                    'by default for performance reasons'))

        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__)
        if value is None:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
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
        wrapped_f.__doc__ = f.__doc__
        wrapped_f.__name__ = f.__name__
        wrapped_f.__module__ = f.__module__
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


class Dict(object):
    '''A sorted dict with somes additional methods.'''
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

    def to_csv(self, delimiter=',', header=True):
        '''Serialize list of dictionaries to csv.'''
        return dict_to_csv([self.store], delimiter, header)

    def __unicode__(self):
        return "%s" % self.store

    def __str__(self):
        return "%s" % self.store.__str__()

    def __repr__(self):
        return self.store.__repr__()


class ListDict(list):
    '''List of sorteddicts with somes additional methods.'''

    def to_csv(self, delimiter=',', header=True):
        '''Serialize list of dictionaries to csv.'''
        return dict_to_csv(list(self), delimiter, header)

    def filter(self, keys):
        items = ListDict()
        for item in self:
            data = item.copy()
            unused_keys = set(data.keys()) - set(keys)
            for key in unused_keys:
                del data[key]
            items.append(data)
        return ListDict()

    def sorted_by(self, keyword, reverse=False):
        return ListDict(sorted(self, key=lambda k: k[keyword],
                                     reverse=reverse))
