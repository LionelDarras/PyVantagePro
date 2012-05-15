# coding: utf8
"""
    PyVPDriver
    ~~~~~~~~~

    Communication driver for VantagePro 2 station

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: BSD, see LICENSE for more details.

"""

import re
import sys
from os import path
from setuptools import setup, find_packages

import pyvpdriver

with open(path.join(path.dirname(__file__), 'pyvpriver', '__init__.py')) as fd:
    VERSION = re.search("VERSION = '([^']+)'", fd.read().strip()).group(1)

with open(path.join(path.dirname(__file__), 'README')) as fd:
    LONG_DESCRIPTION = fd.read()


REQUIREMENTS = [
    'pyserial',
]

if sys.version_info < (2, 7) or (3,) <= sys.version_info < (3, 2):
    # In the stdlib from 2.7:
    REQUIREMENTS.append('argparse')

setup(
    name='PyVPDriver',
    version=VERSION,
    url='https://github.com/SalemHarrache/PyVPDriver',
    license='BSD',
    description='Communication driver for VantagePro 2 station',
    long_description=LONG_DESCRIPTION,
    author='Salem Harrache',
    author_email='contact@salem.harrache.info',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Topic :: Scientific/Engineering',
        'Topic :: Terminals'
    ],
    packages=find_packages(),
    zip_safe=False,
    install_requires=REQUIREMENTS,
    test_suite='pygeol.tests',
    entry_points={
        'console_scripts': [
            'pyvpdriver = pyvpdriver.__main__:main',
        ],
    },
)
