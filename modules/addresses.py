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
        return self.value or ''

    def format_storage(self):
        """Format the postal code suitable for storage.

        Notes:
            Storage format means:
                * Convert to uppercase.
                * Remove all non-alphanumeric chars.

        Returns:
            String, eg 'A1B2C3'
        """
        if not self.value:
            return ''
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
        if not s:
            return ''
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
        if not s:
            return ''
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
    if not value:
        return PostalCode(value)

    for_testing = re.sub(r'[^0-9A-Z]', '', value.upper())

    if re.compile(r'^\d{5}$').match(for_testing) or \
            re.compile(r'^\d{9}$').match(for_testing):
            return USAZipCode(value)
    if re.compile(r'^[A-Z][0-9][A-Z][0-9][A-Z][0-9]$').match(for_testing):
            return CanadianPostalCode(value)
    return PostalCode(value)


def best_guess_address(db, city, province, postal_code):
    """Given some address values, return formalized address values.

    Given postal_code    determine city, province, country if possible
    Given city           determine province, postal_code, country if possible
    Given city, province determine province, postal_code, country
    Given province       determine country

    Args:
        db: gluon.dal.DAL instance
        city: string, city name
        province: string, province value, eg 'ON', 'Ontario', optional
        postal_code: string, unformatted postal code, optional

    Returns:
        dict: {
            'city': 'formal city',
            'province': 'formal province',
            'country': 'formal country',
            'postal_code': 'formal postal_code',
            }
    """
    address = {
            'city': '',
            'province': '',
            'country': '',
            'postal_code': '',
            }

    def db_address(address, query):
        rows = db(query).select(
                db.postal_code.name,
                db.city.name,
                db.province.name,
                db.country.name,
                left=[db.city.on(db.postal_code.city_id == db.city.id),
                    db.province.on(db.city.province_id == db.province.id),
                    db.country.on(db.province.country_id == db.country.id)]
                )
        address_lists = {
            'city': [],
            'province': [],
            'country': [],
            'postal_code': [],
            }
        for r in rows:
            for k in address_lists.keys():
                if r[k]['name'] not in address_lists[k]:
                    address_lists[k].append(r[k]['name'])
        for k in address_lists.keys():
            if len(address_lists[k]) == 1:
                    address[k] = address_lists[k][0]
        return address

    if postal_code:
        pc = best_guess_code(postal_code).format_display()
        codes = db(db.postal_code.name == pc).select()
        if len(codes) == 1:
            address = db_address(address, db.postal_code.id == codes[0].id)

    if city:
        cities = db(db.city.name == city).select()
        if len(cities) == 1:
            address = db_address(address, db.city.id == cities[0].id)

    address['postal_code'] = best_guess_code(
            address['postal_code'] or postal_code).format_display()
    address['city'] = address['city'] or city
    if province:
        query = (db.province.name == province) | \
                (db.province.code == province)
        provinces = db(query).select()
        if len(provinces) == 1:
            address['province'] = provinces[0].name
            try:
                q = db.country.id == provinces[0].country_id
                address['country'] = db(q).select()[0].name
            except:
                pass

    address['province'] = address['province'] or province
    return address
