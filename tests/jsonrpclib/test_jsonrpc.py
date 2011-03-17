#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
test_jsonrpc.py

Test suite for shared/modules/jsonrpclib/jsonrpc.py

"""

from applications.shared.modules.local.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.jsonrpclib.jsonrpc import Server
import sys
import unittest

# pylint: disable=C0111,R0904


class TestServer(unittest.TestCase):

    def test____init__(self):
        url = '/'.join([
                'https://input.ellwoodepps-dev.com/',
                'firearms/BasicJSONRPCData/call/jsonrpc',
                ])
        server = Server(url)
        self.assertEqual(server.add(1, 10), 11)


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
