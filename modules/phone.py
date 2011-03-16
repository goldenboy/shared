#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
phone.py

Classes related to phone numbers.

"""

import re


class PhoneNumber(object):
    """Class representing a phone number."""
    def __init__(self, value):
        """Constructor.

        Args:
            value: str, phone number value. eg '519 291 5554'
                The format of the value can vary. Punctation is ignored.
        """
        self.value = value
        self.npa = ''           # area_code
        self.nxx = ''           # exchange
        self.xxxx = ''          # station
        self.ext = ''           # extension
        if self.value:
            self.parse()

    def __repr__(self):
        return self.format_display()

    def __str__(self):
        return self.__repr__()

    def area_code(self):
        """Return the phone number's area code.

        Returns:
            string, the phone's area code, ie npa.
        """
        return self.npa

    def exchange(self):
        """Return the phone number's exchange.

        Returns:
            string, the phone's exchange, ie nxx.
        """
        return self.nxx

    def extension(self):
        """Return the phone number's extension.

        Returns:
            string, the phone's extension, ie ext.
        """
        return self.ext

    def format_display(self):
        """Format the phone number suitable for display.

        NOTE: ...

        Returns:
            String, eg '(519) 291-5554 x123'
        """
        # If the nxx or xxxx are not defined, the phone number is atypical.
        # Return the value as is.
        if not self.nxx or not self.xxxx:
            return self.value

        # The npa and ext are optional. Only format if they exist.
        npa_str = '({npa})'.format(npa=self.npa) if self.npa else ''
        ext_str = 'x{ext}'.format(ext=self.ext) if self.ext else ''

        return '{npa} {nxx}-{xxxx} {ext}'.format(npa=npa_str, nxx=self.nxx,
                xxxx=self.xxxx, ext=ext_str).strip()

    def format_storage(self):
        """Format the phone number suitable for storage.

        NOTE: ...

        Returns:
            String, eg '5192915554123'
        """
        # If the npa, nxx or xxxx are not defined, the phone number is
        # atypical. Return the value as is.
        if not self.npa or not self.nxx or not self.xxxx:
            return self.value.strip()

        return '{npa:3s}{nxx:3s}{xxxx:4s}{ext}'.format(npa=self.npa,
                nxx=self.nxx, xxxx=self.xxxx, ext=self.ext).strip()

    def parse(self):
        """Parse the phone number into its components.

        Strategy
            1) Remove all non digits from string.
            2) Remove any leading digit one (1).
            3) Parse number based on number of digits sent. See table below.

         Typical phone number format: (aaa) bbb-cccc xdddd
         Digits    Format          Example          npa   nxx   xxxx  ext
         10        aaabbbcccc      '5192912540'    '519' '291' '2540' ''
         >=11      aaabbbccccdddd  '519291254012'  '519' '291' '2540' '12'
         others    <invalid>       'Not Available' ''    ''    ''     ''
        """

        self.npa = ''
        self.nxx = ''
        self.xxxx = ''
        self.ext = ''
        if not self.value:
            return

        v = self.value
        # Remove non-digits
        v = re.compile(r'[^0-9]').sub('', v)
        # Remove leading digit one.
        v = re.compile(r'^1').sub('', v)
        if len(v) == 10:
            self.npa = v[0:3]
            self.nxx = v[3:6]
            self.xxxx = v[6:]
        elif len(v) > 10:
            self.npa = v[0:3]
            self.nxx = v[3:6]
            self.xxxx = v[6:10]
            self.ext = v[10:]
        return

    def station(self):
        """Return the phone number's station.

        Returns:
            string, the phone's station, ie xxxx.
        """
        return self.xxxx
