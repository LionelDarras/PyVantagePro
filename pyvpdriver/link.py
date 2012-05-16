#!/usr/bin/env python
# coding: utf8
"""
    pyvpdriver.link
    ~~~~~~~~~~~~~~~

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: BSD, see LICENSE for more details.

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
        return 'socket://%s:%d' % (self.host, self.port)

    @property
    def status(self):
        status = self._socket and not self._socket.closed
        return 'Opened' if status else 'Closed'

    def open(self):
        if self._socket is None:
            self._socket = serial.serial_for_url(self.url)
            self._socket._timeout = self.timeout
        else:
            if self._socket.closed:
                self._socket = None
                self.open()
        LOGGER.info('new %s was initialized' % self)

    def close(self):
        if self._socket is not None and self._socket.closed:
            self._socket.close()
            self._socket = None

    @property
    def socket(self):
        self.open()
        return self._socket

    def write(self, message):
        return self.socket.write(message)

    def read(self, size=None):
        data = ""
        if size is None:
            line = ""
            while len(data) < Link.MAX_STRING_SIZE:
                line = self.readline()
                if line == "":
                    break
                data = "%s%s" % (data, line)
        else:
            data = self.socket.read(size)
        return data

    def readline(self):
        """ Read lines, implemented as generator"""
        return self.socket.readline()

    def lines(self):
        """ Read lines, implemented as generator"""
        while True:
            yield self.readline()

    def __del__(self):
        self.close()

    def __unicode__(self):
        name = self.__class__.__name__
        return u"<%s %s %s>" % (name,self.url, self.status)

    def __str__(self):
        return str(self.__unicode__)

    def __repr__(self):
        return "%s" % self

    def __iter__(self):
        return iter(self._socket)


from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    r = "GET / HTTP/1.1\r\n\r\n"

    link = TCPLink("pypi.python.org", 80)
    link.write(r)
    1/0

if __name__ == "__main__":
    app.run(debug=True, port=9090)
