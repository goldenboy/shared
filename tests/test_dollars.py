#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/dollars.py

"""

from applications.shared.modules.dollars import Dollars
from applications.shared.modules.local.test_runner import LocalTestSuite, \
    ModuleTestSuite
import decimal
import sys
import unittest

# pylint: disable=C0111


class TestDollars(unittest.TestCase):

    def test____init__(self):
        """
        docstring for __init__
        """

        dollars = Dollars()
        self.assertFalse(dollars.amount)
        dollars = Dollars(amount=0)
        self.assertEqual(str(dollars.amount), '0.00')
        dollars = Dollars(amount=0.00)
        self.assertEqual(str(dollars.amount), '0.00')
        dollars = Dollars(amount=123)
        self.assertEqual(str(dollars.amount), '123.00')
        dollars = Dollars(amount=123.00)
        self.assertEqual(str(dollars.amount), '123.00')
        dollars = Dollars(amount=123.00)
        self.assertEqual(str(dollars.amount), '123.00')
        dollars = Dollars(amount=1234567.89)
        self.assertEqual(str(dollars.amount), '1234567.89')
        dollars = Dollars(amount=1.99999)
        self.assertEqual(str(dollars.amount), '2.00')

        # Test comparitive overrides

        dollars = Dollars(amount=0)
        self.assertTrue(dollars == 0)
        self.assertTrue(dollars == 0.00)
        self.assertFalse(dollars != 0)
        self.assertFalse(dollars > 0)
        self.assertTrue(dollars >= 0)
        self.assertFalse(dollars < 0)
        self.assertTrue(dollars <= 0)
        dollars = Dollars(amount=123.45)
        self.assertTrue(dollars == 123.45)
        self.assertTrue(dollars != 0)
        self.assertTrue(dollars > 0)
        self.assertTrue(dollars >= 0)
        self.assertFalse(dollars < 0)
        self.assertFalse(dollars <= 0)
        dollars = Dollars(amount=-123.45)
        self.assertTrue(dollars == -123.45)
        self.assertTrue(dollars != 0)
        self.assertFalse(dollars > 0)
        self.assertFalse(dollars >= 0)
        self.assertTrue(dollars < 0)
        self.assertTrue(dollars <= 0)

        # Test math overrides

        dollars = Dollars(amount=123.45)
        dollars_2 = Dollars(amount=543.21)
        self.assertEqual(dollars, 123.45)
        self.assertEqual(+dollars, 123.45)
        self.assertEqual(-dollars, -123.45)
        self.assertEqual(dollars + 543.21, 666.66)
        self.assertEqual(dollars + dollars_2, 666.66)
        self.assertEqual(dollars_2 - dollars, 419.76)
        self.assertEqual(dollars + 543.21, 666.66)
        self.assertEqual(dollars - 543.21, -419.76)
        self.assertEqual(dollars * 10, 1234.50)
        self.assertEqual(dollars * 0.05, 6.17)
        self.assertEqual(dollars / 10, 12.35)
        self.assertEqual(dollars / 0.05, 2469.00)
        zero_caught = 0
        try:
            dollars / 0
        except decimal.DivisionByZero:
            zero_caught = 1
        self.assertTrue(zero_caught)

        dollars = Dollars(amount=123.45)
        dollars += 123.45
        self.assertEqual(dollars, 246.90)

        dollars = Dollars(amount=123.45)
        dollars -= 111.11
        self.assertEqual(dollars, 12.34)

        dollars = Dollars(amount=123.45)
        dollars *= 10
        self.assertEqual(dollars, 1234.50)

        dollars = Dollars(amount=123.45)
        dollars /= 10
        self.assertEqual(dollars, 12.35)

        zero_caught = 0
        try:
            dollars /= 0
        except decimal.DivisionByZero:
            zero_caught = 1
        self.assertTrue(zero_caught)

        dollars = Dollars(amount=123.45)
        self.assertEqual(float(dollars), 123.45)
        return

    def test__moneyfmt(self):
        """
        The moneyfmt code is borrowed. The tests display typical usage and
        ensures it works as expected.
        """

        dollars = Dollars(amount=1234.56)
        self.assertEqual(dollars.moneyfmt(sep=','), '1,234.56')
        self.assertEqual(dollars.moneyfmt(sep='', curr='$'), '$1234.56')
        self.assertEqual(dollars.moneyfmt(), '1,234.56')
        self.assertEqual(dollars.moneyfmt(curr='$'), '$1,234.56')
        dollars = Dollars(amount=-1234.56)
        self.assertEqual(dollars.moneyfmt(sep='', neg='-'), '-1234.56')
        self.assertEqual(dollars.moneyfmt(sep='', neg='(', trailneg=')'
                         ), '(1234.56)')
        self.assertEqual(dollars.moneyfmt(), '-1,234.56')
        self.assertEqual(dollars.moneyfmt(curr='$'), '-$1,234.56')
        return


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()

