#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
test_magento_api.py

Test suite for shared/modules/magento_api.py

"""

from applications.shared.modules.local.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.magento_api import API
import sys
import unittest
from gluon.shell import env

# pylint: disable=C0111,R0904

# The tests require the local settings for the api user and password. Use
# the firearms application.

APPLICATION = 'firearms'

APP_ENV = env(APPLICATION, import_models=True)
LOCAL_SETTINGS = APP_ENV['local_settings']

URL = "http://www.magento-dev.com"
API_USER = LOCAL_SETTINGS.magento_api_username
API_PASSWORD = LOCAL_SETTINGS.magento_api_password


class TestAPI(unittest.TestCase):

    def test____init__(self):
        api = API(url=URL, api_user=API_USER, api_password=API_PASSWORD)
        self.assertTrue(api)

    def test__api_for_class(self):
        """
        As opposed to testing every decorated property, just test a few
        typical ones.
        """
        api = API(url=URL, api_user=API_USER, api_password=API_PASSWORD)
        root_category = api.category.info(1)
        self.assertEqual(root_category['name'], 'Root Catalog')

        indexer_statuses = api.indexer.status()
        self.assertTrue(len(indexer_statuses) >= 9)
        typical_index = 'catalog_product_attribute'
        typical_statuses = ['pending', 'require_reindex']
        found = True
        for s in indexer_statuses:
            if s.keys()[0] == typical_index:
                found = True
                self.assertTrue(s[typical_index] in typical_statuses)
        self.assertTrue(found)

        # Test merged classes
        pa_set = api.product_attribute_set.list()
        self.assertTrue(len(pa_set) >= 3)
        set_id = 0
        for s in pa_set:
            if s['name'] == 'Firearms':
                set_id = s['set_id']
        self.assertTrue(set_id)

        attributes = api.product_attribute.list(set_id)
        self.assertTrue(len(attributes) > 60)
        found = False
        for attr in attributes:
            if attr['code'] == 'firearm_action':
                found = True
        self.assertTrue(found)


class TestProductAttribute(unittest.TestCase):
    def test__(self):
        api = API(url=URL, api_user=API_USER, api_password=API_PASSWORD)

        # Test a merged class
        self.assertTrue(api.product_attribute)

        # Test availability of magento.catalog methods
        for method in ['currentStore', 'list', 'options']:
            self.assertTrue(method in  dir(api.product_attribute))
        # Test availability of magento_custom.catalog methods
        for method in ['create', 'update', 'delete']:
            self.assertTrue(method in  dir(api.product_attribute))


class TestProductAttributeSet(unittest.TestCase):
    def test__(self):
        api = API(url=URL, api_user=API_USER, api_password=API_PASSWORD)

        # Test a merged class
        self.assertTrue(api.product_attribute_set)

        # Test availability of magento.catalog methods
        for method in ['list']:
            self.assertTrue(method in  dir(api.product_attribute_set))
        # Test availability of magento_custom.catalog methods
        for method in ['insert', 'remove']:
            self.assertTrue(method in  dir(api.product_attribute_set))


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
