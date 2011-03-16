#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/models.py

"""

from applications.shared.modules.local.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.tokens import HashToken, WordsRequired
import sys
import unittest

# pylint: disable=C0111

TOKEN_LEN = 32

class TestHashToken(unittest.TestCase):

    def test____init__(self):
        self.assertRaises(WordsRequired, HashToken)
        token = HashToken(require_words=False)
        self.assertTrue(len(token.token) >= TOKEN_LEN)

    def test__generate(self):
        token = HashToken(require_words=False)
        token.words = []
        self.assertTrue(len(token.generate()) >= TOKEN_LEN)

        token.require_words = True
        self.assertRaises(WordsRequired, token.generate)
        token.words = ['_fake_', '_token_', '_words_']
        first_token = token.generate()
        self.assertTrue(len(first_token) >= TOKEN_LEN)
        # Generating a token a second time using the same words should return
        # the same token.
        second_token = token.generate()
        self.assertTrue(len(second_token) >= TOKEN_LEN)
        self.assertEqual(second_token, first_token)

def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()

