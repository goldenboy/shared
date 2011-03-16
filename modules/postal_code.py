#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
postal_code.py

Classes related to postal codes.

"""

import re


class PostalCode(object):
    """Class representing a postal code."""
    def __init__(self, value):
        """Constructor.

        Args:
            value: str, postal code value. eg 'A1B 2C3'
        """
        self.value = value

    def __repr__(self):
        return self.format_display()

    def __str__(self):
        return self.__repr__()

    def format_display(self):
        """Format the postal code suitable for display.

        Notes: ...
            This method should be overridden by country specific subclasses.
            For the base class no changes are made.

        Returns:
            string, formatted postal code
        """
        return self.value

    def format_storage(self):
        """Format the postal code suitable for storage.

        Notes:
            Storage format means:
                * Convert to uppercase.
                * Remove all non-alphanumeric chars.

        Returns:
            String, eg 'A1B2C3'
        """
        return re.sub(r'[^0-9A-Z]', '', self.value.upper())


class CanadianPostalCode(PostalCode):
    """Class representing a Canadian postal code."""
    def __init__(self, value):
        """Constructor.

        Args:
            value: str, postal code value. eg 'A1B 2C3'
        """
        self.value = value
        PostalCode.__init__(self, value)

    def format_display(self):
        """Format the postal code suitable for display.

        Notes:
            Formatting rules.
            * Format for storage
            * Add a space after the third character

        Returns:
            string, formatted postal code
        """
        s = self.format_storage()
        return '{p1} {p2}'.format(p1=s[:3], p2=s[3:])


class USAZipCode(PostalCode):
    """Class representing an American zip code."""
    def __init__(self, value):
        """Constructor.

        Args:
            value: str, zip code value. eg '1234567890'
        """
        self.value = value
        PostalCode.__init__(self, value)

    def format_display(self):
        """Format the postal code suitable for display.

        Notes:
            Formatting rules.
            * Format for storage
            * If length > 5, add a hyphen after the fifth character.

        Returns:
            string, formatted postal code
        """
        s = self.format_storage()
        if len(s) <= 5:
            return s
        else:
            return '{p1}-{p2}'.format(p1=s[:5], p2=s[5:])


def best_guess_code(value):
    """Return the appropriate PostalCode object for the given code.

    Notes:
        Strategy:
        With non-alphanumeric characters removed
        * All numbers, length 5 or 9  => USAZipCode
        * A1A1A1 => CanadianPostalCode
        * everything else => PostalCode
    """
    for_testing = re.sub(r'[^0-9A-Z]', '', value.upper())

    if re.compile(r'\d{5}').match(for_testing) or \
            re.compile(r'\d{9}').match(for_testing):
            return USAZipCode(value)
    if re.compile(r'[A-Z][0-9][A-Z][0-9][A-Z][0-9]'):
            return CanadianPostalCode(value)
    return PostalCode(value)
