#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/mysql_schema.py

"""

from applications.shared.modules.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.web2py_sql import FieldPropertyDefaults, \
    FieldPropertyDefaultsByName, FieldPropertyDefaultsByType, \
    FieldPropertyDefaultsSet
from applications.shared.modules.mysql_schema import MySQLColumn
import os
import sys
import unittest

# pylint: disable=C0111


class TestFieldPropertyDefaultsSet(unittest.TestCase):

    def _config_file_from_text(self, filename, text):

        # R0201: *Method could be a function*
        # pylint: disable=R0201

        f = open(filename, 'w')
        f.write(text)
        f.close()
        return

    def test____init__(self):
        default_set = FieldPropertyDefaultsSet()
        self.assertTrue(default_set)  # Creates object
        return

    def test__load(self):
        default_set = FieldPropertyDefaultsSet()

        tests = [{
            'label': 'empty file',
            'expect': 0,
            'by_name': {},
            'by_type': {},
            'text': '',
            }, {
            'label': 'fake section',
            'expect': 0,
            'by_name': {},
            'by_type': {},
            'text': """
[fake_section]
setting = value
""",
            }, {
            'label': 'by_name section',
            'expect': 7,
            'by_name': {'id': ['SKIP'], 'creation_date'
                        : ['writable=False'], 'modified_date'
                        : ['writable=False', 'update=request.now']},
            'by_type': {
                'string': ['requires=IS_NOT_EMPTY()'],
                'boolean': ['requires=IS_IN_SET[0,1]'],
                'date': ['IS_DATE()'],
                'time': ['IS_DATE()'],
                },
            'text'
                : """
[by_name]
id = SKIP
creation_date = writable=False
modified_date = writable=False
                update=request.now

[by_type]
string = requires=IS_NOT_EMPTY()
boolean = requires=IS_IN_SET[0,1]
date = IS_DATE()
time = IS_DATE()
""",
            }]

        f_text = '/tmp/web2py_sql_fieldpropertydefaults.txt'
        for t in tests:
            self._config_file_from_text(f_text, t['text'])
            default_set.load(f_text)
            self.assertEqual(len(default_set.field_property_defaults),
                             t['expect'])
            by_name = {}
            by_type = {}
            for fpd in default_set.field_property_defaults:
                if hasattr(fpd, 'column_name'):
                    by_name[fpd.column_name] = fpd.defaults
                if hasattr(fpd, 'column_type'):
                    by_type[fpd.column_type] = fpd.defaults
            if 'by_name' in t:
                self.assertEqual(by_name, t['by_name'])
            if 'by_type' in t:
                self.assertEqual(by_type, t['by_type'])
        os.unlink(f_text)
        return


class TestFieldPropertyDefaults(unittest.TestCase):

    def test____init__(self):
        defaults = FieldPropertyDefaults()
        self.assertTrue(defaults)  # Creates object
        return


class TestFieldPropertyDefaultsByName(unittest.TestCase):

    def test____init__(self):
        defaults = FieldPropertyDefaultsByName(column_name='__by_name__'
                )
        self.assertTrue(defaults)  # Creates object
        return

    def test__defaults_for(self):
        defaults = ['writeable=False', 'IS_NOT_EMPTY()']
        by_name = FieldPropertyDefaultsByName()
        self.assertTrue(by_name)  # Creates object

        # No column provided, returns empty list
        self.assertEqual(by_name.defaults_for(), [])
        column = MySQLColumn()
        # column_name not set, returns empty list
        self.assertEqual(by_name.defaults_for(column=column), [])
        by_name.column_name = 'test_id'
        # column.name not set, returns empty list
        self.assertEqual(by_name.defaults_for(column=column), [])
        column.name = 'fake_id'
        # column.name != column_name, returns empty list
        self.assertEqual(by_name.defaults_for(column=column), [])

        column.name = 'test_id'
        # defaults not set, returns empty list
        self.assertEqual(by_name.defaults_for(column=column), [])

        by_name.defaults = defaults
        # column.name == column_name, returns expected
        self.assertEqual(by_name.defaults_for(column=column), defaults)


        class FakeClass(object):

            """Fake class with no name attribute"""

            def __init__(self):
                return


        column = FakeClass()
        # column has no 'name' attribute, raises exception
        self.assertRaises(AttributeError, by_name.defaults_for,
                          column=column)
        return


class TestFieldPropertyDefaultsByType(unittest.TestCase):

    def test____init__(self):
        defaults = FieldPropertyDefaultsByType(column_type='__by_type__'
                )
        self.assertTrue(defaults)  # Creates object
        return

    def test__defaults_for(self):
        defaults = ['writeable=False', 'IS_NOT_EMPTY()']
        by_type = FieldPropertyDefaultsByType()
        self.assertTrue(by_type)  # Creates object

        # No column provided, returns empty list
        self.assertEqual(by_type.defaults_for(), [])
        column = MySQLColumn()
        # column_type not set, returns empty list
        self.assertEqual(by_type.defaults_for(column=column), [])
        by_type.column_type = 'string'
        # column.data_type not set, returns empty list
        self.assertEqual(by_type.defaults_for(column=column), [])
        column.data_type = 'integer'
        # column.data_type != column_type, returns empty list
        self.assertEqual(by_type.defaults_for(column=column), [])

        column.data_type = 'string'
        # defaults not set, returns empty list
        self.assertEqual(by_type.defaults_for(column=column), [])

        by_type.defaults = defaults
        # column.data_type == column_type, returns expected
        self.assertEqual(by_type.defaults_for(column=column), defaults)


        class FakeClass(object):

            """Fake class with no type attribute"""

            def __init__(self):
                return


        column = FakeClass()
        # column has no 'type' attribute, raises exception
        self.assertRaises(AttributeError, by_type.defaults_for,
                          column=column)
        return


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()

