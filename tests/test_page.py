#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
page.py

Test suite for shared/modules/page.py

"""

from BeautifulSoup import BeautifulSoup
from applications.shared.modules.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.page import WebPage
import sys
import unittest

# C0111: *Missing docstring*
# R0904: *Too many public methods (%s/%s)*
# pylint: disable=C0111,R0904


class TestWebPage(unittest.TestCase):

    def test____init__(self):

        page = WebPage('http://www.example.com')
        self.assertEqual(page.url, 'http://www.example.com')

    def test_get(self):

        page = WebPage('http://www.example.com')
        self.assertEqual(page.content, None)

        page.get()

        soup = BeautifulSoup(page.content, smartQuotesTo=None,
                             convertEntities='xml')

        title = soup.find('title')
        self.assertEqual(title.string, 'IANA &mdash; Example domains')


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
