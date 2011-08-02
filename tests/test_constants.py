#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/constants.py

"""

from applications.shared.modules.constants import \
    SECONDS_PER_MINUTE, \
    MINUTES_PER_HOUR, \
    HOURS_PER_DAY, \
    MINUTES_PER_DAY, \
    SECONDS_PER_HOUR, \
    SECONDS_PER_DAY, \
    MM_PER_CM, \
    CM_PER_M, \
    MM_PER_M, \
    MM_PER_INCH, \
    CM_PER_INCH, \
    M_PER_INCH
from applications.shared.modules.test_runner import LocalTestSuite, \
    ModuleTestSuite
import sys
import unittest

# pylint: disable=C0111


class TestConstants(unittest.TestCase):

    def test__constants(self):
        # Time
        self.assertTrue(SECONDS_PER_MINUTE, 60)
        self.assertTrue(MINUTES_PER_HOUR, 60)
        self.assertTrue(HOURS_PER_DAY, 24)
        self.assertTrue(MINUTES_PER_DAY, 1440)
        self.assertTrue(SECONDS_PER_HOUR, 3600)
        self.assertTrue(SECONDS_PER_DAY, 86400)

        # Length
        self.assertTrue(MM_PER_CM, 10)
        self.assertTrue(CM_PER_M, 100)
        self.assertTrue(MM_PER_M, 1000)
        self.assertTrue(MM_PER_INCH, 25.4)
        self.assertTrue(CM_PER_INCH, 2.54)
        self.assertTrue(M_PER_INCH, 0.0254)


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()

