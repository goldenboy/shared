#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
test_settings.py

Test suite for shared/modules/settings.py

"""

from applications.shared.modules.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.database import Collection
from applications.shared.modules.settings import Setting
from gluon.shell import env
import gluon.main
import sys
import unittest


APP_ENV = env(__file__.split('/')[-3], import_models=True)
DB = APP_ENV['db']

# C0111: Missing docstring
# R0904: Too many public methods
# pylint: disable=C0111,R0904


class TestSetting(unittest.TestCase):

    _objects = []

    # C0103: *Invalid name "%s" (should match %s)*
    # pylint: disable=C0103
    @classmethod
    def tearDownClass(cls):
        for obj in cls._objects:
            obj.remove()

    def test____init__(self):
        setting = Setting(DB.setting)
        self.assertTrue(setting)

    def test__formatted(self):
        tests = [
            #(name, value, type, expect)
            ('_test__formatted_1', 'my string', 'string', 'my string'),
            ('_test__formatted_2', 'True',      'string', 'True'),
            ('_test__formatted_3', 'True',      'boolean', True),
            ('_test__formatted_4', 'False',     'boolean', False),
            ('_test__formatted_5', '',          'boolean', False),
            ('_test__formatted_6', '123',       'integer', 123),
            ]
        for t in tests:
            kwargs = dict(name=t[0], value=t[1], type=t[2])
            setting = Setting(DB.setting, **kwargs)
            self.assertEqual(setting.formatted_value(), t[3])

    def test__get(self):
        tests = [
            #(name, value, type, expect)
            ('_test__get_1', '_test_get_value_1', 'string', '_test_get_value_1'),
            ('_test__get_2', '_test_get_value_2', 'string', '_test_get_value_2'),
            ('_test__get_3', 'True',              'string', 'True'),
            ('_test__get_4', 'True',              'boolean', True),
            ('_test__get_5', 'False',             'boolean', False),
            ('_test__get_6', '',                  'boolean', False),
            ('_test__get_7', '123',               'integer', 123),
            ]

        for t in tests:
            kwargs = dict(name=t[0], value=t[1], type=t[2])
            setting = Setting(DB.setting, **kwargs).add()
            self._objects.append(setting)

        for t in tests:
            self.assertEqual(Setting.get(DB, t[0]), t[3])

        self.assertRaises(ValueError, Setting.get, DB,
                '__non_existent_setting__')

    def test__match(self):
        name_1 = '_test__match_name_1_'
        value_1 = '_test__match_value_1_'
        name_2 = '_test__match_name_2_'
        value_2 = '_test__match_value_2_'

        setting_1 = Setting(DB.setting, name=name_1, value=value_1).add()
        self._objects.append(setting_1)
        setting_2 = Setting(DB.setting, name=name_2, value=value_2).add()
        self._objects.append(setting_2)

        settings = Setting.match(DB, '%_test__match_%')
        self.assertTrue(isinstance(settings, Collection))
        self.assertEqual(len(settings), 2)
        for s in settings:
            self.assertTrue(isinstance(s, Setting))

        settings = Setting.match(DB, '%match_name_2_')
        self.assertEqual(len(settings), 1)

        settings = Setting.match(DB, '%_test__match_%', as_dict=True)
        self.assertTrue(isinstance(settings, dict))
        self.assertEqual(len(settings), 2)
        self.assertTrue(name_1 in settings)
        self.assertEqual(settings[name_1], value_1)
        self.assertTrue(name_2 in settings)
        self.assertEqual(settings[name_2], value_2)


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
