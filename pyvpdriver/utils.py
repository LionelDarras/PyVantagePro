# coding: utf8
'''
    pyvpdriver.utils
    ~~~~~~~~~~~~~~~~

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''
import time
import math

import functools, inspect

def decorator(func):
    ''' Allow to use decorator either with arguments or not. '''

    def isFuncArg(*args, **kw):
        return len(args) == 1 and len(kw) == 0 and (
            inspect.isfunction(args[0]) or isinstance(args[0], type))

    if isinstance(func, type):
        def class_wrapper(*args, **kw):
            if isFuncArg(*args, **kw):
                return func()(*args, **kw) # create class before usage
            return func(*args, **kw)
        class_wrapper.__name__ = func.__name__
        class_wrapper.__module__ = func.__module__
        return class_wrapper

    @functools.wraps(func)
    def func_wrapper(*args, **kw):
        if isFuncArg(*args, **kw):
            return func(*args, **kw)

        def functor(userFunc):
            return func(userFunc, *args, **kw)

        return functor

    return func_wrapper


class cached_property(object):
    '''A decorator that converts a function into a lazy property. The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value.'''
    def __init__(self, ttl=300):
        self.ttl = ttl

    def __call__(self, func, doc=None):
        self.func = func
        self.__doc__ = doc or func.__doc__
        self.__name__ = func.__name__
        self.__module__ = func.__module__

    def __get__(self, inst, owner):
        now = time.time()
        try:
            value, last_update = inst._cache[self.__name__]
            if self.ttl > 0 and now - last_update > self.ttl:
                raise AttributeError
        except (KeyError, AttributeError):
            value = self.func(inst)
            try:
                cache = inst._cache
            except AttributeError:
                cache = inst._cache = {}
            cache[self.__name__] = (value, now)
        return value


def byte_to_int(s):
    '''return the integer value of a hexadecimal byte s'''
    return int("%02X " % ord( s ),  16)

def byte_to_string(byte):
    '''Convert a byte string to it's hex string representation.'''
    return ''.join( [ "%02X " % ord( x ) for x in byte ] ).strip()


class retry(object):
    '''Retries a function or method until it returns True.
    delay sets the initial delay in seconds, and backoff sets the factor by
    which the delay should lengthen after each failure.
    Tries must be at least 0, and delay greater than 0.'''

    def __init__(self, tries=3, delay=1):
        self.tries = tries
        self.delay = delay

    def __call__(self, f):
        def wrapped_f(*args):
            for i in xrange(self.tries):
                try:
                    ret = f(*args)
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
