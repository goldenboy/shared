#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
test_phone.py

Test suite for shared/modules/phone.py

"""

from applications.shared.modules.local.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.ConfigParser_improved import \
        ConfigParserImproved
import os
import sys
import unittest

# pylint: disable=C0111,R0904


class TestConfigParserImproved(unittest.TestCase):

    def test__items_scrubbed(self):
        text = \
            """
[section]
s01_true = True
s02_false = False
s03_int = 123
s04_float = 123.45
s05_str1 = my setting value
s06_str2 = 'This is my setting value'
s07_str_true = 'True'
s08_str_int = '123'
s09_str_float = '123.45'

[strings]
str1 = my setting value
str2 = 'This is my setting value'

"""
        f_text = '/tmp/TestConfigParserImproved.txt'
        _config_file_from_text(f_text, text)
        config = ConfigParserImproved()
        config.read(f_text)
        # items() and items_scrubbed() should return strings identically
        self.assertEqual(config.items('strings'),
                config.items_scrubbed('strings'))

        self.assertEqual(sorted(config.items_scrubbed('section')),
            [
                ('s01_true', True),
                ('s02_false', False),
                ('s03_int', 123),
                ('s04_float', 123.45),
                ('s05_str1', 'my setting value'),
                ('s06_str2', "'This is my setting value'"),
                ('s07_str_true', 'True'),
                ('s08_str_int', '123'),
                ('s09_str_float', '123.45'),
                ])

        os.unlink(f_text)


def _config_file_from_text(filename, text):

    # R0201: *Method could be a function*
    # pylint: disable=R0201

    f = open(filename, 'w')
    f.write(text)
    f.close()
    return


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
