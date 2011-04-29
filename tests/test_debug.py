#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
test_debug.py

Test suite for shared/modules/debug.py

"""

from applications.shared.modules.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.debug import LocalEnvironment
from gluon.shell import env
import sys
import unittest

# pylint: disable=C0111,R0904

APP_ENV = env(__file__.split('/')[-3], import_models=True)


class TestLocalEnvironment(unittest.TestCase):

    def test____init__(self):
        # These variables are similar to how they appear in a controller
        request = APP_ENV['request']
        db = APP_ENV['db']
        session = APP_ENV['session']
        auth = APP_ENV['auth']
        BEAUTIFY = APP_ENV['BEAUTIFY']
        local_env = LocalEnvironment(request=request, session=session,
            auth=auth, beauty=BEAUTIFY, db=db)

    def test____repr__(self):
        request = APP_ENV['request']
        db = APP_ENV['db']
        session = APP_ENV['session']
        auth = APP_ENV['auth']
        BEAUTIFY = APP_ENV['BEAUTIFY']
        local_env = LocalEnvironment(request=request, session=session,
            auth=auth, beauty=BEAUTIFY, db=db)
        self.assertTrue(str(local_env))


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
