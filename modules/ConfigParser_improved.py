#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ConfigParser_improved.py

ConfigParser with improvements.
"""

from ConfigParser import SafeConfigParser


class ConfigParserImproved(SafeConfigParser):
    """Class representing an improved config parser.

        SafeConfigParser.items() returns all setting values as strings. This
        causes foo for boolean, integer, and float values. This class is much
        like SafeConfigParser except it adds an items_scrubbed method. The
        method takes the results of the items() method and scrubs the data,
        converting values to their expected data type.

            Config setting             items_scrubbed tuple

            setting = True             ('setting', True)
            setting = False            ('setting', False)
            setting = 123              ('setting', 123)
            setting = 123.45           ('setting', 123.45)
            setting = my setting       ('setting', 'my setting')
            setting = 'my setting'     ('setting', "'my setting'")  *
            setting = 'True'           ('setting', 'True')
            setting = '123'            ('setting', '123')
            setting = '123.45'         ('setting', '123.45')

        * Quoted setting values are returned quoted. This is the same behaviour
        as items().
    """

    def items_scrubbed(self, section, raw=False, vars=None):
        """Return items of a section scrubbed.

        Args:
            see ConfigParse.items()
        """
        items = SafeConfigParser.items(self, section, raw, vars)
        scrubbed = []
        for item in items:
            if item[1].strip() == 'False':
                scrubbed.append((item[0], False))
            elif item[1].strip() == 'True':
                scrubbed.append((item[0], True))
            else:
                try:
                    new_item = (item[0], int(item[1]))
                except ValueError:
                    try:
                        new_item = (item[0], float(item[1]))
                    except ValueError:
                        # Strip strings to remove extra quotes.
                        # Only strip it the value in the quotes is a string.
                        stripped = item[1].strip("'")
                        want_stripped = False
                        if stripped == 'True' or stripped == 'False':
                            want_stripped = True
                        else:
                            try:
                                int(stripped)
                                want_stripped = True
                            except ValueError:
                                try:
                                    float(stripped)
                                    want_stripped = True
                                except ValueError:
                                    want_stripped = False
                        if want_stripped:
                            new_item = (item[0], item[1].strip("'"))
                        else:
                            new_item = item
                scrubbed.append(new_item)
        return scrubbed
