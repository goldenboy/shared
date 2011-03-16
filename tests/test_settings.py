#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
test_settings.py

Test suite for shared/modules/settings.py

"""

from applications.shared.modules.local.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.database import Collection
from applications.shared.modules.settings import Setting
from gluon.shell import env
import sys
import unittest

APP_ENV = env(__file__.split('/')[-3], import_models=True)
DB = APP_ENV['db']

# C0111: Missing docstring
# R0904: Too many public methods
# pylint: disable=C0111,R0904


class TestSetting(unittest.TestCase):

    def test____init__(self):
        setting = Setting(DB.setting)
        self.assertTrue(setting)

    def test__get(self):
        name_1 = '_test__get_name_1_'
        value_1 = '_test__get_value_1_'
        name_2 = '_test__get_name_2_'
        value_2 = '_test__get_value_2_'
        count = lambda: len(Setting(DB.setting).set_.get())

        orig_count = count()
        setting_1 = Setting(DB.setting, name=name_1, value=value_1).add()
        setting_2 = Setting(DB.setting, name=name_2, value=value_2).add()
        self.assertEqual(count(), orig_count + 2)
        self.assertEqual(Setting.get(DB, name_1), value_1)
        self.assertEqual(Setting.get(DB, name_2), value_2)

        self.assertRaises(ValueError, Setting.get, DB,
                '__non_existent_setting__')

        # Cleanup
        setting_1.remove()
        setting_2.remove()

    def test__match(self):
        settings = Setting.match(DB, 'cfc_%', as_dict=True)

        name_1 = 'cfc_test__match_name_1_'
        value_1 = '_test__match_value_1_'
        name_2 = '_test__match_name_2_'
        value_2 = '_test__match_value_2_'

        setting_1 = Setting(DB.setting, name=name_1, value=value_1).add()
        setting_2 = Setting(DB.setting, name=name_2, value=value_2).add()

        settings = Setting.match(DB, '%_test__match_%')
        self.assertTrue(isinstance(settings, Collection))
        self.assertEqual(len(settings), 2)
        for s in settings:
            self.assertTrue(isinstance(s, Setting))

        settings = Setting.match(DB, '%_name_2_')
        self.assertEqual(len(settings), 1)

        settings = Setting.match(DB, '%_test__match_%', as_dict=True)
        self.assertTrue(isinstance(settings, dict))
        self.assertEqual(len(settings), 2)
        self.assertTrue(name_1 in settings)
        self.assertEqual(settings[name_1], value_1)
        self.assertTrue(name_2 in settings)
        self.assertEqual(settings[name_2], value_2)

        # Cleanup
        setting_1.remove()
        setting_2.remove()


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
