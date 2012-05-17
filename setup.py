# coding: utf8
"""
    PyVPDriver
    ~~~~~~~~~~

    Communication driver for VantagePro 2 station

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: BSD, see LICENSE for more details.

"""

import re
import sys
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

README = ''
CHANGES = ''
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except:
    pass

REQUIREMENTS = [
    'pyserial',
]

if sys.version_info < (2, 7) or (3,) <= sys.version_info < (3, 2):
    # In the stdlib from 2.7:
    REQUIREMENTS.append('argparse')

setup(
    name='PyVPDriver',
    version='0.1',
    url='https://github.com/SalemHarrache/PyVPDriver',
    license='GNU GPL v3',
    description='Communication driver for VantagePro 2 station',
    long_description=README + '\n\n' + CHANGES,
    author='Salem Harrache',
    author_email='contact@salem.harrache.info',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering'
    ],
    packages=find_packages(),
    zip_safe=False,
    install_requires=REQUIREMENTS,
    test_suite='pyvpdriver.tests',
    entry_points={
        'console_scripts': [
            'pyvpextract = pyvpdriver.__init__:extract',
            'pyvpconfig = pyvpdriver.__init__:config'
        ],
    },
)
