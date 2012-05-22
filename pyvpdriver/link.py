# coding: utf8
"""
    pyvpdriver.link
    ~~~~~~~~~~~~~~~

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

"""
from __future__ import division, unicode_literals
import serial
import socket
import time

from logger import LOGGER

class Link(object):
    """
    Abstract base class for all links.
    """
    MAX_STRING_SIZE = 4048

class TCPLink(Link):
    """
    TCPLink class allows TCP/IP protocol communication with File-like API.
    """
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
        """Write data to socket."""
        num = self.socket.sendall(message)
        LOGGER.info('Write : <%s>' % repr(message[:num]))
        return num

    def recv_timeout(self, size):
        timeout = self.timeout or 1
        self.socket.setblocking(0)
        total_data=[];data='';begin=time.time()
        while True:
            #if you got some data, then break after wait sec
            if total_data and time.time()-begin>self.timeout:
                break
            #if you got no data at all, wait a little longer
            elif time.time()-begin>timeout*2:
                break
            try:
                data=self.socket.recv(size)
                if data:
                    total_data.append(data[:size])
                    len_data = len(data)
                    if len_data >= size:
                        break
                    else:
                        size = size - len_data
                    begin=time.time()
                else:
                    time.sleep(0.1)
            except:
                pass
        self.socket.settimeout(self.timeout)
        return ''.join(total_data)

    def read(self, size=None):
        """Read data from socket."""
        data = ""
        if size is None:
            size=Link.MAX_STRING_SIZE
        data = self.recv_timeout(size)
        LOGGER.info('Read : <%s>' % repr(data))
        return data

    def readline(self):
        """ Read a line from socket."""
        pass

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

    def __iter__(self):
        """ Read lines, implemented as generator"""
        while True:
            line = self.readline()
            if line:
                yield line
