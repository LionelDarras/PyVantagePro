# coding: utf8
"""
    pyvpdriver.device
    ~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: BSD, see LICENSE for more details.

"""



class NoDeviceException(Exception):
    pass

class VantagePro(object):
    '''
    A class capable of reading raw (binary) weather data from a
    vantage pro console.
    '''
    def __init__(self, link):
        self.link = link

    # device reply commands
    WAKE_ACK = '\n\r'
    ACK = '\x06'
    ESC = '\x1b'
    OK = '\n\rOK\n\r'

    def wake_up(self):
        '''
        Wakeup the console.
        '''
        log.info("send: WAKEUP")
        for i in xrange(3):
            self.link.write('\n')
            ack = self.link.read(len(self.WAKE_ACK))
            log.info("send: %s", ack)
            if ack == self.WAKE_ACK:
                return
        raise NoDeviceException('Can not access weather station')

    def __del__(self):
        '''
        close link when object is deleted.
        '''
        self.link.close()

class VPData(object):
    pass
