# coding: utf8
"""
    PyVantagePro
    ------------

    Communication driver for VantagePro 2 station

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: GNU GPL v3.

"""

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
    'pylink',
    'blist',
    'progressbar>=2.3',
]

if sys.version_info < (2, 7) or (3,) <= sys.version_info < (3, 2):
    # In the stdlib from 2.7:
    REQUIREMENTS.append('argparse')

setup(
    name='PyVantagePro',
    version='0.1',
    url='https://github.com/SalemHarrache/PyVantagePro',
    license='GNU GPL v3',
    description='Communication driver for VantagePro 2 station',
    long_description=README + '\n\n' + CHANGES,
    author='Salem Harrache',
    author_email='salem.harrache@gmail.com',
    maintainer='Lionel Darras',
    maintainer_email='Lionel.Darras@obs.ujf-grenoble.fr',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Topic :: Internet',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=find_packages(),
    zip_safe=False,
    install_requires=REQUIREMENTS,
    test_suite='pyvantagepro.tests',
    entry_points={
        'console_scripts': [
            'pyvantagepro = pyvantagepro.__main__:main'
        ],
    },
)
