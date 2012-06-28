PyVantagePro
============

.. image:: https://secure.travis-ci.org/SalemHarrache/PyVantagePro.png?branch=master

.. module:: pyvantagepro

PyVantagePro is a python project which aims to make the communication with
weather stations Davis VantagePro2 easier and funnier...i.e. more pythonic.

The main feature of this project is to get data automatically. In order to do
so, it uses the basic methods `get_archives()`_ (to get archive data) and
`get_current_data()`_ (to get real-time data).

About configuration, it only uses `gettime()`_ and `settime()`_ because we
are assuming that stations are already configured.

.. _`get_archives()`: #pyvantagepro.VantagePro2.get_archives
.. _`get_current_data()`: #pyvantagepro.VantagePro2.get_current_data
.. _`gettime()`: #pyvantagepro.VantagePro2.gettime
.. _`settime()`: #pyvantagepro.VantagePro2.settime

.. note::
    PyVantagePro uses the `PyLink <http://pypi.python.org/pypi/PyLink>`_ lib,
    offers a universal communication interface with File-Like API.

Examples::

    >>> from pyvantagepro import VantagePro2
    >>>
    >>> device = VantagePro2.from_url('tcp:host-ip:port')
    >>> device.gettime()
    2012-06-13 16:44:56
    >>> data = device.get_current_data()
    >>> data['TempIn']
    87.1
    >>> data.raw
    4C 4F 4F ... 0D E6 3B
    >>> data.filter(('TempIn', 'TempOut', 'SunRise', 'SunSet')).to_csv()
    TempIn,TempOut,SunRise,SunSet
    87.3,71.5,03:50,19:25


Features
--------

* Collecting real-time data as a python dictionary
* Collecting archives as a list of dictionaries
* Collecting data in a CSV file
* Updating station time
* Getting some information about the station, such as date and firmware version.
* Various types of connections are supported
* Comes with a command-line script
* Compatible with Python 2.6+ and 3.x


Installation
------------

You can install, upgrade, uninstall PyVantagePro with these commands::

  $ pip install pyvantagepro
  $ pip install --upgrade pyvantagepro
  $ pip uninstall pyvantagepro

Or if you don't have pip::

  $ easy_install pyvantagepro

Or you can get the `source code from github
<https://github.com/SalemHarrache/PyVantagePro>`_.

Command-line usage
------------------

PyVantagePro has a command-line script that interacts with the station.::

  $ pyvantagepro -h

  usage: pyvantagepro [-h] [--version]
              {gettime,settime,getinfo,getarchives,getdata,update} ...

  Extract data from VantagePro 2 station

  optional arguments:
    -h, --help            show this help message and exit
    --version             Print PyVPDriver’s version number and exit.

  The pyvantagepro commands:
    {gettime,settime,getinfo,getarchives,getdata,update}
      gettime             Print the current date on the station.
      settime             Set the datetime argument on the station.
      getinfo             Print VantagePro information.
      getarchives         Extract archives data from the station between
                          `start` date and `stop` date. By default the
                          entire contents of the data archive will be
                          downloaded.
      getdata             Extract real-time data from the station.
      update              Update csv database records with getting
                          automatically new records.


Gettime
~~~~~~~

The `gettime` command gives, as its name suggests, the current datetime of
the station (with the timezone offset).

Usage::

  pyvantagepro gettime [-h] [--timeout TIMEOUT] [--debug] url

  positional arguments:
    url                Specifiy URL for connection link.
                       E.g. tcp:iphost:port or serial:/dev/ttyUSB0:19200:8N1

  optional arguments:
    -h, --help         show this help message and exit
    --timeout TIMEOUT  Connection link timeout
    --debug            Display log

Example::

  $ pyvantagepro gettime tcp:192.168.0.18:1111
  2012-06-12 15:14:23 - Localtime


Settime
~~~~~~~

Allows us to update the station date and time(no timezone for now).

Usage::

  pyvantagepro settime [-h] [--timeout TIMEOUT] [--debug] url datetime

  Set the given datetime argument on the station

  positional arguments:
    url                Specifiy URL for connection link.
                       E.g. tcp:iphost:port or serial:/dev/ttyUSB0:19200:8N1
    datetime           The chosen datetime value. (like : "2012-06-12 17:31")

  optional arguments:
    -h, --help         show this help message and exit
    --timeout TIMEOUT  Connection link timeout
    --debug            Display log


Example::

  $ pyvantagepro settime tcp:192.168.0.18:1111 "2012-06-12 17:32"
  Old value : 2012-06-12 16:24:15 - Localtime
  New value : 2012-06-12 17:32:02 - Localtime


Getinfo
~~~~~~~

Gives some information about the station,  such as date and firmware version.

Usage::

  pyvantagepro getinfo [-h] [--timeout TIMEOUT] [--debug] url

  Print VantagePro 2 information.

  positional arguments:
    url                Specifiy URL for connection link.
                       E.g. tcp:iphost:port or serial:/dev/ttyUSB0:19200:8N1

  optional arguments:
    -h, --help         show this help message and exit
    --timeout TIMEOUT  Connection link timeout
    --debug            Display log


Example::

  $ pyvantagepro getinfo tcp:192.168.0.18:1111 --timeout 2
  Firmware date : 2009-11-27
  Firmware version : 1.90
  Diagnostics : {'max_received': 21211, 'crc_errors': 0,
  'total_missed': 0, 'total_received': 21211, 'resyn': 0}


Getarchives
~~~~~~~~~~~

Downloads the archive records from the station between two dates.
By default all records are downloaded. If no stop date is specified, the
download will stop at the last record available in the station memory.

Usage::

  pyvantagepro getarchives [-h] [--timeout TIMEOUT] [--debug]
                                  [--output OUTPUT] [--start START]
                                  [--stop STOP] [--delim DELIM]
                                  url

  Extract the archive records from the station between `start` date
  and `stop` date. By default the entire contents of the data archive
  will be downloaded.

  positional arguments:
    url                Specifiy URL for connection link.
                       E.g. tcp:iphost:port or serial:/dev/ttyUSB0:19200:8N1

  optional arguments:
    -h, --help         Show this help message and exit
    --timeout TIMEOUT  Connection link timeout
    --debug            Display log
    --output OUTPUT    Filename where output is written
    --start START      The beginning date record. (like : "2012-06-12 17:36")
    --stop STOP        The stopping date record. (like : "2012-06-12 17:36")
    --delim DELIM      CSV char delimiter


Example::

  $ pyvantagepro getarchives tcp:192.168.0.18:1111 \
    --start "2012-06-12 16:19" --stop "2012-06-12 16:21" \
    --output archive.csv
  Archives download: 100% |##############################################|
  1 record was found

If you want to get all records, you can use this command without specifying
any date

::

  $ pyvantagepro getarchives tcp:192.168.0.18:1111 --output archive.csv
  Archives download: 100% |##############################################|
  2145 records were found


Update
~~~~~~

This command is useful for maintaining a database which is updated regularly
(e.g. with a crontab). The database is a simple CSV file that contains all
archive records. You can use 'getarchives' with a specific date range
and manually update your data.
However, the update command automatically analyzes the CSV file, retrieves the
datetime of the last record, then downloads the data from the station and add
it to the end of the file.

Finally we have a CSV file with all the data which is updated automatically﻿.


Usage::

  pyvantagepro update [-h] [--timeout TIMEOUT] [--debug] [--delim DELIM]
                             url db

  Update CSV database records by getting automatically new archive records.

  positional arguments:
    url                Specifiy URL for connection link.
                       E.g. tcp:iphost:port or serial:/dev/ttyUSB0:19200:8N1
    db                 The CSV database

  optional arguments:
    -h, --help         Show this help message and exit
    --timeout TIMEOUT  Connection link timeout
    --debug            Display log
    --delim DELIM      CSV char delimiter

Example:

If the file does not exist, it will be created automatically::

  $ pyvantagepro update tcp:192.168.0.18:1111 ./database.csv --timeout 2
  Archives download: 100% |##############################################|
  2145 new records

again...

::

  $ pyvantagepro update tcp:192.168.0.18:1111 ./database.csv --timeout 2
  Archives download: 100% |##############################################|
  No new records were found﻿


Debug mode
~~~~~~~~~~

You can use debug option if you want to print log and see the flowing data::

  $ pyvantagepro settime tcp:192.168.0.18:1111 "2012-06-12 16:24" --debug
  2012-06-12 17:24:45,311 INFO: new <TCPLink tcp:127.0.0.1:1111> was initialized
  2012-06-12 17:24:45,311 INFO: try wake up console
  2012-06-12 17:24:45,311 INFO: Write : <u'\n'>
  2012-06-12 17:24:45,412 INFO: Read : <0A 0D>
  2012-06-12 17:24:45,412 INFO: Check ACK: OK ('\n\r')
  2012-06-12 17:24:45,413 INFO: try send : VER
  2012-06-12 17:24:45,413 INFO: Write : <u'VER\n'>
  2012-06-12 17:24:45,514 INFO: Read : <0A 0D 4F 4B 0A 0D>
  2012-06-12 17:24:45,514 INFO: Check ACK: OK ('\n\rOK\n\r')
  2012-06-12 17:24:45,515 INFO: Read : <41 70 72 20 31 30 20 32 30 30 36 0A 0D>
  2012-06-12 17:24:45,521 INFO: try wake up console
  2012-06-12 17:24:45,521 INFO: Write : <u'\n'>


.. _api:

API reference
-------------

.. autoclass:: VantagePro2
    :members: from_url, get_archives, get_current_data, gettime, settime, timezone, firmware_date, firmware_version, archive_period, diagnostics

    .. automethod:: wake_up()
    .. automethod:: send(data, wait_ack=None, timeout=None)
    .. automethod:: read_from_eeprom(hex_address, size)

.. autoclass:: pyvantagepro.utils.Dict
    :members: to_csv, filter

.. autoclass:: pyvantagepro.utils.ListDict
    :members: to_csv, filter, sorted_by

.. autoexception:: pyvantagepro.device.NoDeviceException

.. autoexception:: pyvantagepro.device.BadAckException

.. autoexception:: pyvantagepro.device.BadCRCException

.. autoexception:: pyvantagepro.device.BadDataException


Feedback & Contribute
---------------------

Your feedback is more than welcome. Write email to the
`PyVantagePro mailing list`_.

.. _`PyVantagePro mailing list`: pyvantagepro@librelist.com

There are several ways to contribute to the project:

#. Post bugs and feature `requests on github`_.
#. Fork `the repository`_ on Github to start making your changes.
#. Write a test which shows that the bug was fixed or that the feature works as expected.
#. Send a pull request and bug the maintainer until it gets merged and published. :) Make sure to add yourself to AUTHORS_.

.. _`requests on github`: https://github.com/SalemHarrache/PyVantagePro/issues
.. _`the repository`: https://github.com/SalemHarrache/PyVantagePro
.. _AUTHORS: https://github.com/SalemHarrache/PyVantagePro/blob/master/AUTHORS.rst


.. include:: ../CHANGES.rst
