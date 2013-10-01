PyVantagePro
============

.. image:: https://pypip.in/v/PyVantagePro/badge.png
   :target: https://crate.io/package/PyVantagePro
.. image:: https://pypip.in/d/PyVantagePro/badge.png
   :target: https://crate.io/packages/PyVantagePro
.. image:: https://travis-ci.org/SalemHarrache/PyVantagePro.png?branch=master
   :target: https://travis-ci.org/SalemHarrache/PyVantagePro



PyVantagePro is a python project which aims to make the communication with
weather stations Davis VantagePro2 easier and funnier...i.e. more Pythonic.

The main feature of this project is to get data automatically.
In order to do so, it uses the basic methods `get_archives()`
(to get archive data) and `get_current_data()` (to get real-time data).

About configuration, it only uses `gettime()` and `settime()` because we are
assuming that stations are already configured.

**Note:** PyVantagePro uses the `PyLink <http://pypi.python.org/pypi/PyLink>`_ lib, offers a universal communication interface with File-Like API.

Examples
--------

::

    >>> from pyvantagepro import VantagePro2
    >>>
    >>> device = VantagePro2.from_url('tcp:host-ip:port')
    >>> device.gettime()
    2012-06-13 16:44:56
    >>> data = device.get_current_data()
    >>> data['TempIn']
    87.3
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


Documentation
-------------

See documentation here: http://pyvantagepro.readthedocs.org
