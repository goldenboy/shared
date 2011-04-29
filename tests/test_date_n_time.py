#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
test_date_n_time.py

Test suite for shared/modules/date_n_time.py

"""

from applications.shared.modules.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.date_n_time import str_to_date
import datetime
import sys
import unittest

# pylint: disable=C0111,R0904


class TestFunctions(unittest.TestCase):

    def test__str_to_date(self):
        date = str_to_date('2011-04-14')
        self.assertTrue(isinstance(date, datetime.date))
        self.assertEqual(str(date), '2011-04-14')

        # Invalid dates
        self.assertEqual(str_to_date('2011-06-31'), None)
        self.assertEqual(str_to_date('abc'), None)
        self.assertEqual(str_to_date(''), None)


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
