#!/usr/bin/env python
# coding: utf8
"""
    pyvpdriver.link
    ~~~~~~~~~~~~~~~

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: BSD, see LICENSE for more details.

"""
import serial


class Link(object):
    """
    Abstract base class for all links.
    """
    MAX_STRING_SIZE = 404800

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
    def socket(self):
        if self._socket is None:
            url = 'socket://%s:%s' % (self.host, self.port)
            self._socket = serial.serial_for_url(url)
            self._socket._timeout = self.timeout
        return self._socket

    def close(self):
        self.socket.close()

    def write(self, message):
        return self.socket.write(message)

    def read(self, size=None):
        data = ""
        if size is None:
            line = ""
            while len(data) < Link.MAX_STRING_SIZE:
                line = link.readline()
                if line == "":
                    break
                data = "%s%s" % (data, line)
        else:
            data = self.socket.read(size)
        return data

    def readline(self):
        return self.socket.readline()


# preparation de la requete
Request = "GET / HTTP/1.1\r\n"
Request+= "Host: localhost\r\n"
Request+= "Connection: Close\r\n\r\n"

link = TCPLink("localhost", 9090)
link.write(Request)
print link.read()
