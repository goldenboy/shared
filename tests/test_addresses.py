#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
test_postal_code.py

Test suite for shared/modules/postal_code.py

"""

from applications.shared.modules.test_runner import LocalTestSuite, \
        ModuleTestSuite
from applications.shared.modules.addresses import CanadianPostalCode, \
        PostalCode, USAZipCode, best_guess_code, best_guess_address
import sys
import unittest
import gluon.main
from gluon.shell import env


# pylint: disable=C0111,R0904

# The test script requires an existing database to work with. The
# shared database should have tables city, province, country and postal_code.
# The models/db.py should define the tables.
APP_ENV = env(__file__.split('/')[-3], import_models=True)
DBH = APP_ENV['db']

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
            ('', '', 'empty string'),
            (None, '', 'none'),
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
            ('', '', 'empty string'),
            (None, '', 'none'),
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
            ('', '', 'empty string'),
            (None, '', 'none'),
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
            ('', '', 'empty string'),
            (None, '', 'none'),
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
            ('', PostalCode, 'empty string'),
            (None, PostalCode, 'none'),
            ('A1B 2C3', CanadianPostalCode, 'CAN'),
            ('A1B2C3',  CanadianPostalCode, 'CAN no space'),
            ('a1b 2c3', CanadianPostalCode, 'CAN lowercase'),
            ('12345', USAZipCode, 'USA 5'),
            ('123456789', USAZipCode, 'USA 9'),
            ('12345-6789', USAZipCode, 'USA 9 hyphen'),
            ('Not available', PostalCode, 'notice'),
            ('!@#!%$!@$#!', PostalCode, 'gibberish'),
            ('1234', PostalCode, 'too few digits'),
            ('123456', PostalCode, 'unmatching digits'),
            ('1234567890', PostalCode, 'too many digits'),
            ('A1B 2C', PostalCode, 'Invalid CAN'),
            ('A1B 2C3D', PostalCode, 'Invalid CAN'),
            ('_fake_pc_', PostalCode, 'fake code'),
            ]

        for t in tests:
            postal_code = best_guess_code(t[0])
            self.assertEqual(type(postal_code), t[1])

    def test_best_guess_address(self):
        # These tests assume city, province and postal_code have Canadian
        # data.

        # (city, province, postal_code)
        tests = [
            ('', '', 'B9A 3T5', {
                    'city': 'Troy',
                    'province': 'Nova Scotia',
                    'country': 'Canada',
                    'postal_code': 'B9A 3T5',
                    }),
            ('', '', 'b9a3t5', {
                    'city': 'Troy',
                    'province': 'Nova Scotia',
                    'country': 'Canada',
                    'postal_code': 'B9A 3T5',
                    }),
            ('Capstick', '', '', {
                    'city': 'Capstick',
                    'province': 'Nova Scotia',
                    'country': 'Canada',
                    'postal_code': 'B0C 1E0',
                    }),
            ('Halifax', '', '', {
                    'city': 'Halifax',
                    'province': 'Nova Scotia',
                    'country': 'Canada',
                    'postal_code': '',
                    }),
            ('', 'ON', '', {
                    'city': '',
                    'province': 'Ontario',
                    'country': 'Canada',
                    'postal_code': '',
                    }),
            ('', 'Ontario', '', {
                    'city': '',
                    'province': 'Ontario',
                    'country': 'Canada',
                    'postal_code': '',
                    }),
            ('_fake_city_', '', 'B9A 3T5', {
                    'city': 'Troy',
                    'province': 'Nova Scotia',
                    'country': 'Canada',
                    'postal_code': 'B9A 3T5',
                    }),
            ('_fake_city_', '_fake_prov_', '_fake_pc_', {
                    'city': '_fake_city_',
                    'province': '_fake_prov_',
                    'country': '',
                    'postal_code': '_fake_pc_',
                    }),
            ]

        for t in tests:
            self.assertEqual(best_guess_address(DBH, t[0], t[1], t[2]), t[3])

def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
