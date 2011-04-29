#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/text_tools.py

"""

from applications.shared.modules.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.text_tools import MarkdownText, \
    TruncatableText
import sys
import textwrap
import unittest

# pylint: disable=C0111


class TestMarkdownText(unittest.TestCase):

    def test_text_as_xml(self):

        tests = [{'label': 'None', 'text': None, 'expect': ''}, {'label'
                 : 'empty string', 'text': '', 'expect': ''}, {'label'
                 : 'plain text', 'text': 'hello world', 'expect'
                 : '<p>hello world</p>\n'}, {'label': 'emphasis', 'text'
                 : '*hello world*', 'expect'
                 : '<p><em>hello world</em></p>\n'}, {'label'
                 : 'unordered list', 'text'
                 : """
                        * jays
                        * yankees
                        * bosox
                        """,
                 'expect'
                 : '''<ul>
<li>jays</li>
<li>yankees</li>
<li>bosox</li>
</ul>
'''}]

        for test in tests:
            text = None
            if test['text']:
                text = textwrap.dedent(test['text'])
            mkd_text = MarkdownText(text=text)
            xml = mkd_text.text_as_xml()
            self.assertEqual(xml.xml(), test['expect'])


class TestTruncatableText(unittest.TestCase):

    def test_truncated_text(self):

        tests = [{
            'label': 'None',
            'text': None,
            'length': 0,
            'expect': '',
            }, {
            'label': 'empty string',
            'text': '',
            'length': 0,
            'expect': '',
            }, {
            'label': 'plain text, no truncate',
            'text': 'hello world',
            'length': 0,
            'expect': 'hello world',
            }, {
            'label': 'plain text, truncate',
            'text': 'hello world',
            'length': 5,
            'expect': 'hello...',
            }, {
            'label': 'plain text, truncate on whitespace',
            'text'
                : """
                        This is a line of text
                        Another line.
                        And a third
                        """,
            'length': 30,
            'expect': '''
This is a line of text
Another...''',
            }]

        for test in tests:
            text = None
            if test['text']:
                text = textwrap.dedent(test['text'])
            trunc_text = TruncatableText(text=text,
                    truncate_length=test['length'])
            self.assertEqual(trunc_text.truncated_text(), test['expect'
                             ])


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()

