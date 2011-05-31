#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
stickon/validators.py

Classes extending functionality of gluon/validators.py.

"""
from gluon.validators import IS_DECIMAL_IN_RANGE, is_empty

# C0103: Invalid name
# pylint: disable=C0103


class IS_CURRENCY(IS_DECIMAL_IN_RANGE):
    """Class representing a currency validator."""
    def __init__(self, *a, **b):
        IS_DECIMAL_IN_RANGE.__init__(self, *a, **b)
        if not 'error_message' in b:
            self.error_message = self.error_message.replace(' a number ',
                    ' a dollar amount ')

    def __call__(self, value):
        return IS_DECIMAL_IN_RANGE.__call__(self, value)

    def formatter(self, value):
        try:
            return '{val:.2f}'.format(val=float(value))
        except (ValueError, TypeError):
            return value or ''


class IS_NOT_ALL_EMPTY(object):
    """Class representing a validator requiring at least one non-empty field in
    a set.
    """

    def __init__(self, others,
            error_message='Enter a value in at least one field'):
        self.others = others
        self.error_message = error_message

    def __call__(self, value):
        okay = (value, None)
        error = (value, self.error_message)
        # Return okay either the 'value', or one of self.others is not empty.
        values = []
        values.append(value)
        values.extend(self.others)
        empties = []
        for v in values:
            unused_v, empty = is_empty(v)
            empties.append(empty)
        # Example empties == [True, True, False]
        # If one False exists, it's valid
        if reduce(lambda x, y: x and y, empties):
            return error
        return okay


class BOTH_NOT_EMPTY(object):
    """Validator class for presense of atleast one value."""
    def __init__(self, other_value, error_message='enter a value', strip=True):
        self.other_value = other_value
        self.error_message = error_message
        self.strip = strip

    def __call__(self, value):
        if self.strip:
            self.other_value = self.other_value.strip()
            value = value.strip()
        if not self.other_value and not value:
            return (value, self.error_message)
        else:
            return (value, None)