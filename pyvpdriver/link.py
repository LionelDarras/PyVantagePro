# coding: utf8
'''
    pyvpdriver.link
    ~~~~~~~~~~~~~~~

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''
from __future__ import unicode_literals
import sys
import socket
import time
import serial

from .logger import LOGGER


class Link(object):
    '''Abstract base class for all links.'''
    MAX_STRING_SIZE = 4048

    def open(self):
        '''Open the link.'''
        pass

    def close(self):
        '''Close the link.'''
        pass

    def byte_to_string(self, byte):
        '''Convert a byte string to it's hex string representation.'''
        return ''.join( [ "%02X " % ord( x ) for x in byte ] ).strip()

    def log(self, message, data, is_byte):
        if is_byte:
            LOGGER.info("%s : <%s>" % (message, self.byte_to_string(data)))
        else:
            LOGGER.info("%s : <%s>" % (message,repr(data)))

    def __del__(self):
        '''Close link when object is deleted.'''
        self.close()

    def __unicode__(self):
        name = self.__class__.__name__
        return "<%s %s>" % (name, self.url)

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return str(self.__unicode__())


class TCPLink(Link):
    '''TCPLink class allows TCP/IP protocol communication with File-like
    API.'''
    def __init__(self, host, port, timeout=1):
        self.timeout = timeout
        self.host = host
        self.port = port
        self._socket = None

    @property
    def url(self):
        '''Make a connection url from `host` and `port`.'''
        return 'tcp:%s:%d' % (self.host, self.port)

    def open(self):
        '''Open the socket.'''
        if self._socket is None:
            self._socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self._socket.connect((self.host,self.port))
            self._socket.settimeout(self.timeout)
            LOGGER.info('new %s was initialized' % self)

    def close(self):
        '''Close the socket.'''
        if self._socket is not None:
            self._socket.close()
            LOGGER.info('Connection %s was closed' % self)
            self._socket = None

    @property
    def socket(self):
        '''Return an opened socket object.'''
        self.open()
        return self._socket

    def write(self, data, is_byte=False):
        '''Write all `data` to socket.'''
        if sys.version_info[0] >= 3:
            # Python 3
            self.socket.sendall(bytes(data, encoding='utf8'))
        else:
            # Python 2
            self.socket.sendall(data)
        self.log("Write", data, is_byte)

    def read(self, size=None, is_byte=False):
        '''Read data from socket. The maximum amount of data to be received at
        once is specified by `size`. If `is_byte` is True, the data will be
        convert to hexadecimal array.'''
        size = size or self.MAX_STRING_SIZE
        data = self.recv_timeout(size, is_byte)
        self.log("Write", data, is_byte)
        return data

    def recv_timeout(self, size, is_byte=False):
        '''Uses a non-blocking sockets in order to continue trying to get data
        as long as the client manages to even send a single byte.
        This is useful for moving data which you know very little about
        (like encrypted data), so cannot check for completion in a sane way.'''

        self.socket.setblocking(0)
        timeout = self.timeout or 1
        begin = time.time()
        data = bytearray()
        total_data = []

        while True:
            #if you got some data, then break after wait sec
            if time.time()- begin > timeout:
                break
            try:
                data = self.socket.recv(size)
                if data:
                    total_data.append(data)
                    size = size - len(data)
                    if size == 0:
                        break
                    begin = time.time()
                else:
                    time.sleep(0.1)
            except:
                # just need to get out of recv form time to time to check if
                # still alive
                time.sleep(0.1)
                pass
        self.socket.settimeout(self.timeout)
        if is_byte:
            return b"".join(total_data)
        else:
            return b"".join(total_data).decode("utf-8")


class SerialLink(Link):
    '''SerialLink class allows serial communication with File-like API.
    Possible values for the parameter port:
      - Number: number of device, numbering starts at zero.
      - Device name: depending on operating system.
          e.g. /dev/ttyUSB0 on GNU/Linux or COM3 on Windows.'''
    def __init__(self, port, baudrate=19200, bytesize=8, parity='N',
                                             stopbits=1, timeout=1):
        self.port = port
        self.timeout = timeout
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self._serial = None

    @property
    def url(self):
        '''Make a connection url.'''
        return 'serial:%s:%d:%d%s%d' % (self.port, self.baudrate,
                                          self.bytesize, self.parity,
                                          self.stopbits)

    def open(self):
        '''Open the serial connection.'''
        if self._serial is None:
            self._serial = serial.Serial(self.port, self.baudrate,
                                    timeout=self.timeout,
                                    bytesize=self.bytesize, parity=self.parity,
                                    stopbits=self.stopbits)
            LOGGER.info('new %s was initialized' % self)

    def close(self):
        '''Close the serial connection.'''
        if self._serial is not None:
            if self._serial.isOpen():
                self._serial.close()
                LOGGER.info('Connection %s was closed' % self)
            self._serial = None

    @property
    def serial(self):
        '''Return an opened serial object.'''
        self.open()
        return self._serial

    def write(self, data, is_byte=False):
        '''Write all `data` to the serial connection.'''
        self.serial.write(data)
        self.log("Write", data, is_byte)

    def read(self, size=None, is_byte=False):
        '''Read data from the serial connection. The maximum amount of data
        to be received at once is specified by `size`. If `is_byte` is True,
        the data will be convert to byte array.'''
        size = size or self.MAX_STRING_SIZE
        data = self.serial.read(size)
        self.log("Read", data, is_byte)
        return data
