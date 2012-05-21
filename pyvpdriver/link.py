# coding: utf8
"""
    pyvpdriver.link
    ~~~~~~~~~~~~~~~

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

"""
from __future__ import division, unicode_literals
import serial

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

    @property
    def status(self):
        """Return status of the link."""
        status = self._socket and not self._socket.closed
        return 'Opened' if status else 'Closed'

    def open(self):
        """Open the socket."""
        if self._socket is None:
            self._socket = serial.serial_for_url(self.url,timeout=self.timeout)
            LOGGER.info('new %s was initialized' % self)
        else:
            if self._socket.closed:
                self._socket = None
                self.open()


    def close(self):
        """Close the socket."""
        if self._socket is not None and self._socket.closed:
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
        num = self.socket.write(message)
        LOGGER.info('Write : <%s>' % message[:num].encode("string-escape"))
        return num

    def read(self, size=None):
        """Read data from socket."""
        data = ""
        if size is None:
            line = ""
            while len(data) < Link.MAX_STRING_SIZE:
                line = self.socket.readline()
                if line == "":
                    break
                data = "%s%s" % (data, line)
        else:
            data = self.socket.read(size)
        LOGGER.info('Read : <%s>' % data.encode("string-escape"))
        return data

    def readline(self):
        """ Read a line from socket."""
        data = self.socket.readline()
        LOGGER.info('Read : <%s>' % data.encode("string-escape"))
        return data

    def __del__(self):
        """Close link when object is deleted."""
        self.close()

    def __unicode__(self):
        name = self.__class__.__name__
        return u"<%s %s %s>" % (name,self.url, self.status)

    def __str__(self):
        return str(self.__unicode__)

    def __repr__(self):
        return "%s" % self

    def __iter__(self):
        """ Read lines, implemented as generator"""
        return iter(self._socket)
