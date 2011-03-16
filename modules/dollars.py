#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
dollars.py

Classes related to representing values as dollars.

"""

import decimal

decimal.getcontext().rounding = decimal.ROUND_HALF_UP
D = decimal.Decimal
TWOPLACES = D(10) ** -2


class Dollars(object):

    """Class representing a dollar value.

    Object instances maintain two decimal points when printed or used in
    basic arithmetic.

    """

    def __init__(self, amount=0):
        """Constructor.

        Args:
            amount - the value of the dollar number.

        """

        if not amount:
            amount = 0
        self.amount = D(str(amount)).quantize(TWOPLACES)
        return

    def __repr__(self):
        return '%.2f' % self.amount

    def __eq__(self, other):
        return str(self) == str(other_as_decimal(other))

    def __ne__(self, other):
        return str(self) != str(other_as_decimal(other))

    def __ge__(self, other):
        return str(self) >= str(other_as_decimal(other))

    def __gt__(self, other):
        return str(self) > str(other_as_decimal(other))

    def __le__(self, other):
        return str(self) <= str(other_as_decimal(other))

    def __lt__(self, other):
        return str(self) < str(other_as_decimal(other))

    def __pos__(self):
        return Dollars(amount=self.amount)

    def __neg__(self):
        return Dollars(amount=D(str(self.amount
                       * -1)).quantize(TWOPLACES))

    def __add__(self, other):
        if isinstance(other, Dollars):
            amount = self.amount + other.amount
        else:
            amount = self.amount + D(str(other)).quantize(TWOPLACES)
        return Dollars(amount=amount)

    def __sub__(self, other):
        if isinstance(other, Dollars):
            amount = self.amount - other.amount
        else:
            amount = self.amount - D(str(other)).quantize(TWOPLACES)
        return Dollars(amount=amount)

    def __mul__(self, other):
        if isinstance(other, Dollars):
            amount = D(str(self.amount
                       * other.amount)).quantize(TWOPLACES)
        else:
            amount = D(str(self.amount
                       * D(str(other)))).quantize(TWOPLACES)
        return Dollars(amount=amount)

    def __div__(self, other):
        if isinstance(other, Dollars):
            amount = D(str(self.amount
                       / other.amount)).quantize(TWOPLACES)
        else:
            amount = D(str(self.amount
                       / D(str(other)))).quantize(TWOPLACES)
        return Dollars(amount=amount)

    def __iadd__(self, other):
        if isinstance(other, Dollars):
            self.amount = D(str(self.amount
                            + other.amount)).quantize(TWOPLACES)
        else:
            self.amount = D(str(self.amount
                            + D(str(other)))).quantize(TWOPLACES)
        return self

    def __isub__(self, other):
        if isinstance(other, Dollars):
            self.amount = D(str(self.amount
                            - other.amount)).quantize(TWOPLACES)
        else:
            self.amount = D(str(self.amount
                            - D(str(other)))).quantize(TWOPLACES)
        return self

    def __imul__(self, other):
        if isinstance(other, Dollars):
            self.amount = D(str(self.amount
                            * other.amount)).quantize(TWOPLACES)
        else:
            self.amount = D(str(self.amount
                            * D(str(other)))).quantize(TWOPLACES)
        return self

    def __idiv__(self, other):
        if isinstance(other, Dollars):
            self.amount = D(str(self.amount
                            / other.amount)).quantize(TWOPLACES)
        else:
            self.amount = D(str(self.amount
                            / D(str(other)))).quantize(TWOPLACES)
        return self

    def __float__(self):
        """
        Convert to float.
        This is required for saving values to a database "double" type field.
        """

        return float('%.2f' % self.amount)

    def moneyfmt(
        self,
        places=2,
        curr='',
        sep=',',
        decpt='.',
        pos='',
        neg='-',
        trailneg='',
        ):
        """Convert D (decimal.Decimal) to a money formatted string.
        Adapted from: http://docs.python.org/library/decimal.html#recipes

        Args:
            places:     integer    Number of places after the decimal point
            curr:       string     Currency symbol before the sign (may be blank)
            sep:        string     Grouping separator (comma, period, space, or blank)
            decpt:      string     Decimal point indicator (comma or period)
                                        only specify as blank when places is zero
            pos:        string     Sign for positive numbers: '+', space or blank
            neg:        string     Sign for negative numbers: '-', '(', space or blank
            trailneg:   string     Trailing minus indicator:  '-', ')', space or blank

        Examples:
        >>> d = D('-1234567.8901')
        >>> moneyfmt(d, curr='$')
        '-$1,234,567.89'
        >>> moneyfmt(d, places=0, sep='.', decpt='', neg='', trailneg='-')
        '1.234.568-'
        >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
        '($1,234,567.89)'
        >>> moneyfmt(D(123456789), sep=' ')
        '123 456 789.00'
        >>> moneyfmt(D('-0.02'), neg='<', trailneg='>')
        '<0.02>'

        """

        exponent = D(10) ** -places  # 2 places --> '0.01'
        (sign, digits, unused_exp) = \
            self.amount.quantize(exponent).as_tuple()
        result = []
        digits = [str(x) for x in digits]
        (build, next_func) = (result.append, digits.pop)
        if sign:
            build(trailneg)
        for i in range(places):
            build((next_func() if digits else '0'))
        build(decpt)
        if not digits:
            build('0')
        i = 0
        while digits:
            build(next_func())
            i += 1
            if i == 3 and digits:
                i = 0
                build(sep)
        build(curr)
        build((neg if sign else pos))
        return ''.join(reversed(result))


def other_as_decimal(other):
    """Convert other to decimal.Decimal"""

    if isinstance(other, Dollars):
        other_as_d = other
    else:
        if other == None or other == '':
            return False
        other_as_d = D(str(other)).quantize(TWOPLACES)
    return other_as_d


