# coding: utf8
"""
    pyvpdriver.link
    ~~~~~~~~~~~~~~~

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

"""
from __future__ import division, unicode_literals

import socket
import time
import serial

from logger import LOGGER

class Link(object):
    """Abstract base class for all links."""
    MAX_STRING_SIZE = 4048
    def byte_to_string(self, byte ):
        """Convert a byte string to it's hex string representation."""
        return ''.join( [ "%02X " % ord( x ) for x in byte ] ).strip()

class TCPLink(Link):
    """TCPLink class allows TCP/IP protocol communication with File-like
    API."""
    def __init__(self, host, port, timeout=1):
        self.timeout = timeout
        self.host = host
        self.port = port
        self._socket = None

    @property
    def url(self):
        """Make a connection url from `host` and `port`."""
        return 'socket://%s:%d' % (self.host, self.port)

    def open(self):
        """Open the socket."""
        if self._socket is None:
            self._socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self._socket.connect((self.host,self.port))
            self._socket.settimeout(self.timeout)
            LOGGER.info('new %s was initialized' % self)

    def close(self):
        """Close the socket."""
        if self._socket is not None:
            self._socket.close()
            LOGGER.info('Connection %s was closed' % self)
            self._socket = None

    @property
    def socket(self):
        """Return an opened socket object."""
        self.open()
        return self._socket

    def write(self, message):
        """Write all `message` to socket."""
        num = self.socket.sendall(message)
        LOGGER.info(u'Write : <%s>' % repr(message[:num]))
        return num

    def recv_timeout(self, size, byte=False):
        """Uses a non-blocking sockets in order to continue trying to get data
        as long as the client manages to even send a single byte.
        This is useful for moving data which you know very little about
        (like encrypted data), so cannot check for completion in a sane way."""
        timeout = self.timeout or 1
        self.socket.setblocking(0)

        begin = time.time()
        data = bytearray()

        while True:
            #if you got some data, then break after wait sec
            if data and time.time()- begin > self.timeout:
                break
            #if you got no data at all, wait a little longer
            elif time.time() - begin > timeout * 2:
                break
            try:
                # an implementation with internal buffer would be better
                # performing...
                data = self._socket.recv(size)
            except socket.error:
                # just need to get out of recv form time to time to check if
                # still alive
                continue
            if not data:
                time.sleep(0.1)
            size = size - len(data)
            if size <= 0:
                break
            begin = time.time()

        self.socket.settimeout(self.timeout)
        if byte:
            return data
        else:
            return str(data)

    def read(self, size=None, byte=False):
        """Read data from socket. The maximum amount of data to be received at
        once is specified by `size`. If `byte` is True, the data will be
        convert to hexadecimal array."""
        size = size or self.MAX_STRING_SIZE
        data = self.recv_timeout(size, byte)
        if byte:
            LOGGER.info(u'Read : <%s>' % self.byte_to_string(data))
        else:
            LOGGER.info(u'Read : <%s>' % repr(data))
        return data

    def __del__(self):
        """Close link when object is deleted."""
        self.close()

    def __unicode__(self):
        name = self.__class__.__name__
        return u"<%s %s>" % (name,self.url)

    def __str__(self):
        return str(self.__unicode__)

    def __repr__(self):
        return "%s" % self
