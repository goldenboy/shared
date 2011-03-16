#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
url.py

Test suite for shared/modules/url.py

"""

from applications.shared.modules.local.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.url import UniformResourceLocator
import sys
import unittest

# pylint: disable=C0111,R0904


class TestUniformResourceLocator(unittest.TestCase):

    def test____init__(self):
        try:
            UniformResourceLocator()
        except TypeError:
            # Expect this.
            pass
        else:
            self.fail('No value provided should raise exception.')

        try:
            UniformResourceLocator('http://www.example.com')
        except TypeError:
            self.fail('Value provided should not raise exception.')

    def test__update_query(self):
        scheme_host = 'http://www.example.com'
        query = '?aaa=111'
        test_url = ''.join([scheme_host, query])

        # Test where params is an empty dict.
        params = {}
        url = UniformResourceLocator(scheme_host)
        url.update_query(params)
        self.assertEqual(url.value, scheme_host)
        url = UniformResourceLocator(test_url)
        url.update_query(params)
        self.assertEqual(url.value, test_url)

        # Test adding one parameter
        params = dict(bbb=222)
        url = UniformResourceLocator(scheme_host)
        url.update_query(params)
        expect = scheme_host + '?bbb=222'
        self.assertEqual(url.value, expect)
        url = UniformResourceLocator(test_url)
        url.update_query(params)
        expect = test_url + '&bbb=222'
        self.assertEqual(url.value, expect)

        # Test adding multiple parameters
        params = dict(ccc=333, ddd=444)
        url = UniformResourceLocator(scheme_host)
        url.update_query(params)
        expect = scheme_host + '?ccc=333&ddd=444'
        self.assertEqual(url.value, expect)
        url = UniformResourceLocator(test_url)
        url.update_query(params)
        expect = test_url + '&ccc=333&ddd=444'
        self.assertEqual(url.value, expect)


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
