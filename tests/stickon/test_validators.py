#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/stickon/validators.py

"""

from applications.shared.modules.local.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.stickon.validators import IS_CURRENCY, \
        IS_NOT_ALL_EMPTY
import sys
import unittest
import decimal

# C0103: Invalid name
# C0111: Missing docstring
# R0904: Too many public methods
# pylint: disable=C0103,C0111,R0904


class TestIS_CURRENCY(unittest.TestCase):

    def test____init__(self):
        validator = IS_CURRENCY()
        self.assertTrue(validator)
        self.assertTrue(len(validator.error_message) > 0)

    def test____call__(self):
        self.assertEqual(IS_CURRENCY(1, 5)(4), (decimal.Decimal('4'), None))
        self.assertEqual(IS_CURRENCY(1, 5)(5.1), (5.1,
            'enter a dollar amount between 1 and 5'))
        self.assertEqual(IS_CURRENCY(
            1, 5, error_message='Test error message')(5.1),
            (5.1, 'Test error message'))
        self.assertEqual(IS_CURRENCY(
            1, 5, error_message='Test error message')('abc'),
            ('abc', 'Test error message'))

    def test__formatter(self):
        self.assertEqual(IS_CURRENCY(1, 5).formatter(4), '4.00')
        self.assertEqual(IS_CURRENCY(1, 5).formatter(4.777), '4.78')
        self.assertEqual(IS_CURRENCY(1, 5).formatter(-4.777), '-4.78')
        self.assertEqual(IS_CURRENCY(1, 5).formatter(0), '0.00')
        self.assertEqual(IS_CURRENCY(1, 5).formatter(None), '')
        self.assertEqual(IS_CURRENCY(1, 5).formatter('abc'), 'abc')


class TestIS_NOT_ALL_EMPTY(unittest.TestCase):

    def test____init__(self):
        validator = IS_NOT_ALL_EMPTY([''])
        self.assertTrue(validator)
        self.assertTrue(len(validator.error_message) > 0)

    def test____call__(self):
        error_msg = '_fake_error_msg_'
        # (value, others, expect)
        tests = [
            ('', ['', ''], error_msg),
            ('aaa', ['', ''], None),
            ('', ['bbb', ''], None),
            ('', ['', 'ccc'], None),
            ('', ['bbb', 'ccc'], None),
            ('aaa', ['bbb', 'ccc'], None),
            ]
        for t in tests:
            self.assertEqual(
                    IS_NOT_ALL_EMPTY(t[1], error_message=error_msg)(t[0]),
                    (t[0], t[2]))


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
