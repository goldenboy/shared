#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/download_agent.py

"""

from applications.shared.modules.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.download_agent import DownloadAgent, \
    DynamicMozillaCookieJar, ErrorMessage
from urllib2 import HTTPError, URLError
import os
import re
import shutil
import socket
import sys
import unittest

# C0111: *Missing docstring*
# R0904: *Too many public methods (%s/%s)*
# pylint: disable=C0111,R0904


class TestDownloadAgent(unittest.TestCase):

    def test____init__(self):
        da = DownloadAgent()
        self.assertFalse(not da)
        return

    def test_download(self):
        tests = [
            {
                'label': 'valid url',
                'url': 'http://www.example.com',
                'expect': '<title>IANA &mdash; Example domains</title>',
            },
            {
                 # We're using openDNS that redirects invalid urls to notice
                 # page so it will return content.
                 'label': 'invalid url',
                 'url': 'http://www.xxxxxxxxxxfakeurlxxxxxxxxxxx.com',
                 'expect': None,
             }]

        for test in tests:
            da = DownloadAgent(url=test['url'])
            da.download()
            if test['expect']:
                self.assertTrue(da.content and len(da.content) > 0)
                p_title = re.compile('%s' % test['expect'])
                m = p_title.search(da.content)
                self.assertFalse(not m)
            else:
                self.assertTrue(not da.content)
        return


class TestDynamicMozillaCookieJar(unittest.TestCase):

    def test____init__(self):
        cj = DynamicMozillaCookieJar()
        self.assertTrue(cj is not None)
        self.assertTrue(hasattr(cj, 'extract_cookies'))
        return

    def test__create_file(self):
        # Should gracefully handle no filename.
        cj = DynamicMozillaCookieJar()
        cj.create_file()
        cj = DynamicMozillaCookieJar(filename='')
        cj.create_file()

        # Test non-existant file.
        cj_file = '/tmp/__test_download_agent__.txt'
        if os.path.exists(cj_file):
            os.remove(cj_file)
        cj = DynamicMozillaCookieJar(filename=cj_file)
        self.assertTrue(cj is not None)
        self.assertRaises(IOError, cj.load)
        # Should create cookie file and it should be loadable.
        cj.create_file()
        self.assertTrue(os.path.exists(cj_file))
        try:
            cj.load()
        except IOError:
            self.assertFalse('Unexpected IOError raised')
        if os.path.exists(cj_file):
            os.remove(cj_file)

        # Test file from no-existant path.
        cj_path = '/tmp/__test_download_agent__'
        cj_file = os.path.join(cj_path, '__cookie__.txt')
        if os.path.exists(cj_path):
            shutil.rmtree(cj_path)

        cj = DynamicMozillaCookieJar(filename=cj_file)
        self.assertTrue(cj is not None)
        self.assertRaises(IOError, cj.load)
        # Should create path and cookie file and it should be loadable.
        cj.create_file()
        self.assertTrue(os.path.exists(cj_file))
        try:
            cj.load()
        except IOError:
            self.assertFalse('Unexpected IOError raised')
        if os.path.exists(cj_path):
            shutil.rmtree(cj_path)
        return


class TestErrorMessage(unittest.TestCase):

    def test____init__(self):
        err = ''
        error_msg = ErrorMessage(err)

        self.assertFalse(error_msg.retry)
        self.assertFalse(error_msg.identified)
        return

    def test__identified(self):

        code = 200
        try:
            raise HTTPError('http://www.example.com', code, None, None,
                            None)
        except HTTPError, err:
            error_msg = ErrorMessage(err)
            error_msg.identify()
            self.assertFalse(error_msg.retry)
            self.assertTrue(error_msg.identified)
            self.assertTrue(len(error_msg.messages) > 0)

        code = 503
        try:
            raise HTTPError('http://www.example.com', code, None, None,
                            None)
        except HTTPError, err:
            error_msg = ErrorMessage(err)
            error_msg.identify()
            self.assertTrue(error_msg.retry)
            self.assertTrue(error_msg.identified)
            self.assertTrue(len(error_msg.messages) > 0)

        reason = socket.timeout()
        try:
            raise URLError(reason)
        except URLError, err:
            error_msg = ErrorMessage(err)
            error_msg.identify()
            self.assertTrue(error_msg.retry)
            self.assertTrue(error_msg.identified)
            self.assertTrue(len(error_msg.messages) > 0)

        reason = socket.gaierror()
        try:
            raise URLError(reason)
        except URLError, err:
            error_msg = ErrorMessage(err)
            error_msg.identify()
            self.assertFalse(error_msg.retry)
            self.assertTrue(error_msg.identified)
            self.assertTrue(len(error_msg.messages) > 0)

        reason = 'something timed out or something'
        try:
            raise URLError(reason)
        except URLError, err:
            error_msg = ErrorMessage(err)
            error_msg.identify()
            self.assertTrue(error_msg.retry)
            self.assertTrue(error_msg.identified)
            self.assertTrue(len(error_msg.messages) > 0)

        try:
            raise IOError('first arg', 'second arg')
        except IOError, err:
            error_msg = ErrorMessage(err)
            error_msg.identify()
            self.assertFalse(error_msg.retry)
            self.assertFalse(error_msg.identified)
            self.assertFalse(len(error_msg.messages) > 0)
        return


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
