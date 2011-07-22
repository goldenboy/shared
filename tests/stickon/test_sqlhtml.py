#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/stickon/validators.py

"""

from applications.shared.modules.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.stickon.sqlhtml import AutoCompleteWidget, \
        InputWidget, SelectWidget
from BeautifulSoup import BeautifulSoup
from gluon.shell import env
import sys
import unittest

# C0103: Invalid name
# C0111: Missing docstring
# R0904: Too many public methods
# pylint: disable=C0103,C0111,R0904

# The test script requires an existing database to work with. The
# shared database should have tables account and company. The models/db.py
# should define the tables.
# Note: When run with python web2py.py, the __file__ value is not what you
# might expect.  __file__ = applications/shared/models/db.py
APP_ENV = env(__file__.split('/')[-3], import_models=True)
DBH = APP_ENV['db']


class TestAutoCompleteWidget(unittest.TestCase):

    def test____init__(self):
        acw = AutoCompleteWidget()
        self.assertTrue(acw)


class TestInputWidget(unittest.TestCase):

    def test____init__(self):
        iw = InputWidget()
        self.assertTrue(iw)

    def test__widget(self):
        field = DBH.account.number
        value = '_some_fake_value__'

        iw = InputWidget()
        soup = as_soup(str(iw.widget(field, value)))
        w_input = soup.find('input')
        if not w_input:
            self.fail('Input tag not returned')
        # Example:
        # <input class="integer" id="account_number" name="number" type="text"
        # value="_some_fake_value__" />
        self.assertEqual(w_input['class'], 'integer')
        self.assertEqual(w_input['id'],    'account_number')
        self.assertEqual(w_input['name'],  'number')
        self.assertEqual(w_input['type'],  'text')
        self.assertEqual(w_input['value'], value)

        iw = InputWidget(attributes=dict(_type='hidden', _id='my_fake_id'),
                class_extra='id_widget')
        soup = as_soup(str(iw.widget(field, value)))
        w_input = soup.find('input')
        if not w_input:
            self.fail('Input tag not returned')
        self.assertEqual(w_input['class'], 'integer id_widget')
        self.assertEqual(w_input['id'],    'my_fake_id')
        self.assertEqual(w_input['name'],  'number')
        self.assertEqual(w_input['type'],  'hidden')
        self.assertEqual(w_input['value'], value)

        iw = InputWidget(attributes=dict(_type='submit'))
        soup = as_soup(str(iw.widget(field, value)))
        w_input = soup.find('input')
        if not w_input:
            self.fail('Input tag not returned')
        self.assertEqual(w_input['class'], 'integer')
        self.assertEqual(w_input['id'],    'account_number')
        self.assertEqual(w_input['name'],  'number')
        self.assertEqual(w_input['type'],  'submit')
        self.assertEqual(w_input['value'], value)


class TestSelectWidget(unittest.TestCase):

    def test____init__(self):
        sw = SelectWidget()
        self.assertTrue(sw)

    def test__widget(self):
        field = DBH.account.status
        value = '_some_fake_value__'

        sw = SelectWidget()
        try:
            sw.widget(DBH.account.number, value)
        except SyntaxError:
            self.fail('SyntaxError raised for field without options.')

        soup = as_soup(str(sw.widget(field, value)))
        select = soup.find('select')
        if not select:
            self.fail('Select tag not returned')
        # Example:
        # <select class="string" id="account_status" name="status">
        #   <option value=""></option>
        #   <option value="a">a</option>
        #   <option value="d">d</option>
        # </select>
        self.assertEqual(select['class'], 'string')
        self.assertEqual(select['id'],    'account_status')
        self.assertEqual(select['name'],  'status')
        options = select.findAll('option')
        self.assertEqual(len(options), 3)

        sw = SelectWidget(attributes=dict(_id='my_fake_id',
            _name='my_fake_name'), class_extra='select_widget')

        soup = as_soup(str(sw.widget(field, value)))
        select = soup.find('select')
        if not select:
            self.fail('Select tag not returned')
        self.assertEqual(select['class'], 'string select_widget')
        self.assertEqual(select['id'],    'my_fake_id')
        self.assertEqual(select['name'],  'my_fake_name')
        options = select.findAll('option')
        self.assertEqual(len(options), 3)


def as_soup(html):
    return BeautifulSoup(html, smartQuotesTo=None, convertEntities='xml')


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
