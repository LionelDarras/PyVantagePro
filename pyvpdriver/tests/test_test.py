# coding: utf8
"""
    weasyprint.tests.test_text
    --------------------------

    Test the text layout.

    :copyright: Copyright 2012 Salem Harrache and contributors, see AUTHORS.
    :license: BSD, see LICENSE for details.

"""

from __future__ import division, unicode_literals

from .testing_utils import assert_no_logs


def addition(x, b):
    return x+b

@assert_no_logs
def test_addition():
    """Test addition example."""
    assert addition(3,2) == 3+5
