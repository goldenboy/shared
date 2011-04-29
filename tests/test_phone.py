#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
test_phone.py

Test suite for shared/modules/phone.py

"""

from applications.shared.modules.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.phone import PhoneNumber
import sys
import unittest

# pylint: disable=C0111,R0904


class TestPhoneNumber(unittest.TestCase):

    def test____init__(self):
        phone = PhoneNumber('')
        self.assertEqual(phone.npa, '')
        phone = PhoneNumber('5192915554123')
        self.assertEqual(phone.npa, '519')
        self.assertEqual(phone.nxx, '291')
        self.assertEqual(phone.xxxx, '5554')
        self.assertEqual(phone.ext, '123')

    def test____repr__(self):
        phone = PhoneNumber('5192915554123')
        self.assertEqual(str(phone), '(519) 291-5554 x123')
        # See test__format_display for more comprehensive testing.

    def test____str__(self):
        # See test____repr__
        pass

    def test__area_code(self):
        phone = PhoneNumber('')
        self.assertEqual(phone.area_code(), '')
        phone.npa = '519'
        self.assertEqual(phone.area_code(), '519')

    def test__exchange(self):
        phone = PhoneNumber('')
        self.assertEqual(phone.exchange(), '')
        phone.nxx = '291'
        self.assertEqual(phone.exchange(), '291')

    def test__extension(self):
        phone = PhoneNumber('')
        self.assertEqual(phone.extension(), '')
        phone.ext = '123'
        self.assertEqual(phone.extension(), '123')

    def test__format_display(self):
        # (npa, nxx, xxxx, ext, expect, label)
        tests = [
            ('519', '291', '5554', '123', '(519) 291-5554 x123', 'all parts'),
            ('',    '291', '5554', '123', '291-5554 x123',       'no npa'),
            ('519', '291', '5554', '',    '(519) 291-5554',      'no ext'),
            ('',    '291', '5554', '',    '291-5554',            '7 digits'),
            ('',    '',     '',    '',    '',                    'no parts'),
            ]

        for t in tests:
            phone = PhoneNumber('')
            phone.npa = t[0]
            phone.nxx = t[1]
            phone.xxxx = t[2]
            phone.ext = t[3]
            self.assertEqual(phone.format_display(), t[4])

        # Handle non-typical phone number
        value = 'Not Available'
        phone = PhoneNumber(value)
        self.assertEqual(phone.format_display(), value)

    def test__format_storage(self):
        # (npa, nxx, xxxx, ext, expect, label)
        tests = [
            ('519', '291', '5554', '123', '5192915554123', 'all parts'),
            ('519', '291', '5554', '',    '5192915554',    'no ext'),
            ('',    '291', '5554', '123', '',              'no npa'),
            ('519', '',    '5554', '123', '',              'no nxx'),
            ('519', '291', '',     '123', '',              'no xxxx'),
            ('',    '',     '',    '',    '',              'no parts'),
            ]

        for t in tests:
            phone = PhoneNumber('')
            phone.npa = t[0]
            phone.nxx = t[1]
            phone.xxxx = t[2]
            phone.ext = t[3]
            self.assertEqual(phone.format_storage(), t[4])

        # Handle non-typical phone number
        value = 'Not Available'
        phone = PhoneNumber(value)
        self.assertEqual(phone.format_storage(), value)
        phone = PhoneNumber(' ' + value + ' ')
        self.assertEqual(phone.format_storage(), value)

    def test__parse(self):
        # (value, npa, nxx, xxxx, ext, label)
        tests = [
            ('5192915554123',       '519', '291', '5554', '123', 'all parts'),
            ('15192915554123',      '519', '291', '5554', '123', 'all, w/ 1'),
            (' 5192915554123 ',     '519', '291', '5554', '123', 'strip'),
            ('(519) 291-5554 x123', '519', '291', '5554', '123', 'rm punct'),
            ('5192915554',          '519', '291', '5554', '',    'no ext'),
            ('15192915554',         '519', '291', '5554', '',    'no ext, 1'),
            ('987',                 '',    '',     '',    '',    'too few'),
            ('',                    '',    '',     '',    '',    'no value'),
            ('Not Available',       '',    '',     '',    '',    'atypical'),
            ]

        for t in tests:
            phone = PhoneNumber(t[0])
            self.assertEqual(phone.npa, t[1])
            self.assertEqual(phone.nxx, t[2])
            self.assertEqual(phone.xxxx, t[3])
            self.assertEqual(phone.ext, t[4])

    def test__station(self):
        phone = PhoneNumber('')
        self.assertEqual(phone.station(), '')
        phone.xxxx = '5554'
        self.assertEqual(phone.station(), '5554')


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
