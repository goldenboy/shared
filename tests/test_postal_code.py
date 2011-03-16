#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
test_postal_code.py

Test suite for shared/modules/postal_code.py

"""

from applications.shared.modules.local.test_runner import LocalTestSuite, \
        ModuleTestSuite
from applications.shared.modules.postal_code import CanadianPostalCode, \
        PostalCode, USAZipCode, best_guess_code
import sys
import unittest

# pylint: disable=C0111,R0904


class TestPostalCode(unittest.TestCase):

    def test____init__(self):
        postal_code = PostalCode('')
        self.assertEqual(postal_code.value, '')
        postal_code = PostalCode('A1B 2C3')
        self.assertEqual(postal_code.value, 'A1B 2C3')

    def test____repr__(self):
        postal_code = PostalCode('A1B 2C3')
        self.assertEqual(str(postal_code), 'A1B 2C3')
        # See test__format_display for more comprehensive testing.

    def test____str__(self):
        # See test____repr__
        pass

    def test__format_display(self):
        # (value, expect, label)
        tests = [
            ('A1B 2C3', 'A1B 2C3', 'typical can'),
            ('a1b 2c3', 'a1b 2c3', 'typical can lowercase'),
            ('A1B2C3', 'A1B2C3', 'typical can no space'),
            ('123456789', '123456789', 'typical usa 9'),
            ('12345', '12345', 'typical usa 5'),
            ]

        for t in tests:
            postal_code = PostalCode(t[0])
            self.assertEqual(postal_code.format_display(), t[1])

        # Handle non-typical postal_code number
        value = 'Not Available'
        postal_code = PostalCode(value)
        self.assertEqual(postal_code.format_display(), value)

    def test__format_storage(self):
        # (value, expect, label)
        tests = [
            ('A1B 2C3', 'A1B2C3', 'typical can'),
            ('a1b 2c3', 'A1B2C3', 'typical can lowercase'),
            ('A1B2C3', 'A1B2C3', 'typical can no space'),
            ('123456789', '123456789', 'typical usa 9'),
            ('12345', '12345', 'typical usa 5'),
            ('abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                'lowercase letters'),
            ('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                'uppercase letters'),
            ('!@#$%^&*()<>?/|\[]{};:"_+-=', '', 'non-alphanumeric'),
            ]

        for t in tests:
            postal_code = PostalCode(t[0])
            self.assertEqual(postal_code.format_storage(), t[1])

        # Handle non-typical postal_codes
        value = 'Not Available'
        expect = 'NOTAVAILABLE'
        postal_code = PostalCode(value)
        self.assertEqual(postal_code.format_storage(), expect)
        postal_code = PostalCode(' ' + value + ' ')
        self.assertEqual(postal_code.format_storage(), expect)


class TestCanadianPostalCode(unittest.TestCase):

    def test____init__(self):
        postal_code = CanadianPostalCode('')
        self.assertEqual(postal_code.value, '')
        postal_code = CanadianPostalCode('A1B 2C3')
        self.assertEqual(postal_code.value, 'A1B 2C3')

    def test__format_display(self):
        # (value, expect, label)
        tests = [
            ('A1B 2C3', 'A1B 2C3', 'typical can'),
            ('a1b 2c3', 'A1B 2C3', 'typical can lowercase'),
            ('A1B2C3', 'A1B 2C3', 'typical can no space'),
            ('12345', '123 45', 'atypical 5'),
            ('123456789', '123 456789', 'atypical 9'),
            ]

        for t in tests:
            postal_code = CanadianPostalCode(t[0])
            self.assertEqual(postal_code.format_display(), t[1])

        # Handle non-typical postal_code number
        # Note: this works only by coincidence since the string has a space in
        # the third character.
        value = 'Not Available'
        expect = 'NOT AVAILABLE'
        postal_code = CanadianPostalCode(value)
        self.assertEqual(postal_code.format_display(), expect)


class TestUSAZipCode(unittest.TestCase):

    def test____init__(self):
        postal_code = USAZipCode('')
        self.assertEqual(postal_code.value, '')
        postal_code = USAZipCode('A1B 2C3')
        self.assertEqual(postal_code.value, 'A1B 2C3')

    def test__format_display(self):
        # (value, expect, label)
        tests = [
            ('12345', '12345', 'atypical 5'),
            ('123456789', '12345-6789', 'atypical 9'),
            ('A1B 2C3', 'A1B2C-3', 'typical can'),
            ('a1b 2c3', 'A1B2C-3', 'typical can lowercase'),
            ('A1B2C3', 'A1B2C-3', 'typical can no space'),
            ]

        for t in tests:
            postal_code = USAZipCode(t[0])
            self.assertEqual(postal_code.format_display(), t[1])

        # Handle non-typical postal_code number
        # Obviously this is not handled well.
        value = 'Not Available'
        expect = 'NOTAV-AILABLE'
        postal_code = USAZipCode(value)
        self.assertEqual(postal_code.format_display(), expect)


class TestFunctions(unittest.TestCase):

    def test_best_guess_code(self):
        # (value, expect, label)
        tests = [
            ('A1B 2C3', CanadianPostalCode, 'CAN'),
            ('A1B2C3',  CanadianPostalCode, 'CAN no space'),
            ('a1b 2c3', CanadianPostalCode, 'CAN lowercase'),
            ('12345', USAZipCode, 'USA 5'),
            ('123456789', USAZipCode, 'USA 9'),
            ('12345-6789', USAZipCode, 'USA 9 hyphen'),
            ('', PostalCode, 'empty string'),
            ('Not available', PostalCode, 'notice'),
            ('!@#!%$!@$#!', PostalCode, 'gibberish'),
            ('1234', PostalCode, 'too few digits'),
            ('123456', PostalCode, 'unmatching digits'),
            ('1234567890', PostalCode, 'too many digits'),
            ('A1B 2C', PostalCode, 'Invalid CAN'),
            ('A1B 2C3D', PostalCode, 'Invalid CAN'),
            ]

        for t in tests:
            postal_code = best_guess_code(t[0])
            self.assertTrue(isinstance(postal_code, t[1]))


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
