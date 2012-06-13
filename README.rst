============
PyVantagePro
============

Communication tools for VantagePro 2 station.

Command-line usage
==================

PyVantagePro has a command-line script that provides to interact with the station.::

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
      getarchives         Extract archives data from the station between `start`
                          date and `stop` date. By default the entire contents
                          of the data archive will be downloaded.
      getdata             Extract real-time data from the station.
      update              Update csv database records with getting automatically
                          new records.


Gettime
-------

The "gettime" command gives, as its name suggests, the current datetime of
the station. (with the timezone offset)

Usage::

  pyvantagepro gettime [-h] [--timeout TIMEOUT] [--debug] url

  positional arguments:
    url                Specifiy URL for connection link. E.g. tcp:iphost:port or
                       serial:/dev/ttyUSB0:19200:8N1

  optional arguments:
    -h, --help         show this help message and exit
    --timeout TIMEOUT  Connection link timeout
    --debug            Display log

Exemple::

  $ pyvantagepro gettime tcp:192.168.0.18:1111
  2012-06-12 15:14:23 - Localtime


Settime
-------

Allows to update the date and time of the station. (No timezone for now)

Usage::

  pyvantagepro settime [-h] [--timeout TIMEOUT] [--debug] url datetime

  Set the given datetime argument on the station

  positional arguments:
    url                Specifiy URL for connection link. E.g. tcp:iphost:port or
                       serial:/dev/ttyUSB0:19200:8N1
    datetime           The chosen datetime value. (like : "2012-06-12 17:31")

  optional arguments:
    -h, --help         show this help message and exit
    --timeout TIMEOUT  Connection link timeout
    --debug            Display log


Exemple::

  $ pyvantagepro settime tcp:192.168.0.18:1111 "2012-06-12 17:32"
  Old value : 2012-06-12 16:24:15 - Localtime
  New value : 2012-06-12 17:32:02 - Localtime


Getinfo
-------

Gives some information about the station,  such as date and version of firmware.

Usage::

  pyvantagepro getinfo [-h] [--timeout TIMEOUT] [--debug] url

  Print VantagePro 2 information.

  positional arguments:
    url                Specifiy URL for connection link. E.g. tcp:iphost:port or
                       serial:/dev/ttyUSB0:19200:8N1

  optional arguments:
    -h, --help         show this help message and exit
    --timeout TIMEOUT  Connection link timeout
    --debug            Display log


Exemple::

  $ pyvantagepro getinfo tcp:192.168.0.18:1111 --timeout 2
  Firmware date : 2009-11-27
  Firmware version : 1.90
  Diagnostics : {'max_received': 21211, 'crc_errors': 0, 'total_missed': 0, 'total_received': 21211, 'resyn': 0}


Getarchives
-----------

Downloads the archive records from the station between two dates.
By default all records are downloaded. If no stop date is specified, the
download will stop at the last record in the station memory.

Usage::

  pyvantagepro getarchives [-h] [--timeout TIMEOUT] [--debug]
                                  [--output OUTPUT] [--start START]
                                  [--stop STOP] [--delim DELIM]
                                  url

  Extract the archive records from the station between `start` date and `stop` date.
  By default the entire contents of the data archive will be downloaded.

  positional arguments:
    url                Specifiy URL for connection link. E.g. tcp:iphost:port or
                       serial:/dev/ttyUSB0:19200:8N1

  optional arguments:
    -h, --help         show this help message and exit
    --timeout TIMEOUT  Connection link timeout
    --debug            Display log
    --output OUTPUT    Filename where output is written
    --start START      The beginning date record. (like : "2012-06-12 17:36")
    --stop STOP        The stopping date record. (like : "2012-06-12 17:36")
    --delim DELIM      CSV char delimiter


Exemple::

  $ pyvantagepro getarchives tcp:192.168.0.18:1111 --start "2012-06-12 16:19" --stop "2012-06-12 16:21" --output archive.csv
  Archives download: 100% |#####################################################|
  1 record was found

if you want to get all records, you can use this command without any specific date::

  $ pyvantagepro getarchives tcp:192.168.0.18:1111 --output archive.csv
  Archives download: 100% |#####################################################|
  2145 records were found


Update
------

This command is useful for maintaining a database which is updated regularly
(e.g. with a crontab). The database is a simple CSV file that contains all
archive records. You can certainly use 'getarchives' with a specific date range
and manually update your data.
However, the update command automatically analyzes the CSV file, retrieves the
datetime of the last record, then downloads the data from the station and add
them to the end of the file.

Finally we have a csv file with all the data which is updated automatically﻿.


Usage::

  pyvantagepro update [-h] [--timeout TIMEOUT] [--debug] [--delim DELIM]
                             url db

  Update csv database records by getting automatically new archive records.

  positional arguments:
    url                Specifiy URL for connection link. E.g. tcp:iphost:port or
                       serial:/dev/ttyUSB0:19200:8N1
    db                 The CSV database

  optional arguments:
    -h, --help         show this help message and exit
    --timeout TIMEOUT  Connection link timeout
    --debug            Display log
    --delim DELIM      CSV char delimiter

Exemple

If the file does not exist, it will be created automatically﻿::

  $ pyvantagepro update tcp:192.168.0.18:1111 ./database.csv --timeout 2
  Archives download: 100% |#####################################################|
  2145 new records

again...::


$ pyvantagepro update tcp:192.168.0.18:1111 ./database.csv --timeout 2
Archives download: 100% |#####################################################|
No new records were found﻿


Debug mode
----------

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
