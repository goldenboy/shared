#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/stickon/validators.py

"""

from applications.shared.modules.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.stickon.validators import IS_CURRENCY, \
        IS_NOT_ALL_EMPTY, NOT_EMPTY_IF_OTHER, NOT_EMPTY_IF_OTHER_BY_ID
from gluon.shell import env
import gluon.main               # Sets up logging (if logging in module)
import sys
import unittest
import decimal

# C0103: Invalid name
# C0111: Missing docstring
# R0904: Too many public methods
# pylint: disable=C0103,C0111,R0904

# The test script requires an existing database to work with. The
# shared database should have tables account and company. The models/db.py
# should define the tables.
APP_ENV = env(__file__.split('/')[-4], import_models=True)
DBH = APP_ENV['db']


class TestIS_CURRENCY(unittest.TestCase):

    def test____init__(self):
        validator = IS_CURRENCY()
        self.assertTrue(validator)
        self.assertTrue(len(validator.error_message) > 0)

    def test____call__(self):
        self.assertEqual(IS_CURRENCY(1, 5)(4), (decimal.Decimal('4'), None))
        self.assertEqual(IS_CURRENCY(1)(0.4), (0.4,
            'enter a dollar amount greater than or equal to 1'))
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

    error_msg = '_fake_error_msg_'

    def test____init__(self):
        validator = IS_NOT_ALL_EMPTY([''])
        self.assertTrue(validator)
        self.assertTrue(len(validator.error_message) > 0)

    def test____call__(self):
        # (value, others, expect)
        tests = [
            ('', ['', ''], self.error_msg),
            ('aaa', ['', ''], None),
            ('', ['bbb', ''], None),
            ('', ['', 'ccc'], None),
            ('', ['bbb', 'ccc'], None),
            ('aaa', ['bbb', 'ccc'], None),
            ]
        for t in tests:
            self.assertEqual(
                    IS_NOT_ALL_EMPTY(t[1], error_message=self.error_msg)(t[0]),
                    (t[0], t[2]))


class TestNOT_EMPTY_IF_OTHER(unittest.TestCase):

    error_msg = '_fake_error_msg_'

    def test____init__(self):
        validator = NOT_EMPTY_IF_OTHER('__test_not_empty_if_other__')
        self.assertTrue(validator)
        self.assertTrue(len(validator.error_message) > 0)

    def test____call__(self):
        # (value, dropdown_value, expect)
        tests = [
            ('',            '',          None),
            ('',            'Not Other', None),
            ('',            'Other',     self.error_msg),
            ('Input Value', '',          None),
            ('Input Value', 'Not Other', None),
            ('Input Value', 'Other',     None),
            ]
        for t in tests:
            self.assertEqual(
                    NOT_EMPTY_IF_OTHER(t[1], error_message=self.error_msg)(t[0]),
                    (t[0], t[2]))


class TestNOT_EMPTY_IF_OTHER_BY_ID(unittest.TestCase):

    _objects = []
    field = DBH.test.name
    error_msg = '_fake_error_msg_'

    # C0103: *Invalid name "%s" (should match %s)*
    # pylint: disable=C0103
    @classmethod
    def tearDownClass(cls):
        for obj in cls._objects:
            obj.remove()
        DBH.test.truncate()

    @classmethod
    def setUpClass(cls):
        # Create dummy records in test table
        DBH.test.insert(name='Not Other')
        DBH.test.insert(name='Other')

    def test____init__(self):

        validator = NOT_EMPTY_IF_OTHER_BY_ID(self.field, 0)
        self.assertTrue(validator)
        self.assertTrue(len(validator.error_message) > 0)

    def test____call__(self):
        # (value, dropdown_value, expect)
        tests = [
            ('',            '',          None),
            ('',            'Not Other', None),
            ('',            'Other',     self.error_msg),
            ('Input Value', '',          None),
            ('Input Value', 'Not Other', None),
            ('Input Value', 'Other',     None),
            ]
        for t in tests:
            if t[1]:
                selected_id = DBH(DBH.test.name == t[1]).select()[0].id
            else:
                selected_id = 0

            self.assertEqual(
                    NOT_EMPTY_IF_OTHER_BY_ID(self.field, selected_id, error_message=self.error_msg)(t[0]),
                    (t[0], t[2]))


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
