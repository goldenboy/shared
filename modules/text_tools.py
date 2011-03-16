#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Classes for handling custom text formatting.

"""

import re


class MarkdownText(object):

    """
    This class ensures consistent use of markdown across applications by
    defining the extras and permitted_tags options in the XML call
    """

    def __init__(self, text=''):
        self.text = text

    def text_as_xml(self):
        """
        Convert markdown text to xml
        """

        from gluon.html import XML
        import gluon.contrib.markdown.markdown2

        if not self.text:
            return XML('')

        return XML(gluon.contrib.markdown.markdown2.markdown(self.text,
                   extras=['code-friendly', 'footnotes', 'codecolor',
                   'linkpatterns']), permitted_tags=[
            'a',
            'b',
            'blockquote',
            'br/',
            'cite',
            'code',
            'h1',
            'h2',
            'h3',
            'h4',
            'i',
            'img/',
            'li',
            'ol',
            'p',
            'pre',
            'ul',
            ])


class TruncatableText(object):

    """
    This class permits text to be truncated.

    truncate_length=0 indicates no truncate
    """

    def __init__(self, text=None, truncate_length=0):
        self.text = text
        self.truncate_length = truncate_length
        self.truncated = False

    def truncated_text(self):
        """If self.text is more than self.truncate_length characters long,
        it will be cut at the next word-boundary and '...' will
        be appended.
        To prevent corrupting markdown punctuation syntax, truncate only on
        word-boundary end followed by space followed by word-boundary start.
        """

        if not self.text:
            return ''

        if self.truncate_length == 0:
            return self.text

        if len(self.text) < self.truncate_length:
            return self.text

        pattern = r'^(.{%d,}?\b)\s+\b.*' % (self.truncate_length - 1)
        text_re = re.compile(pattern, re.DOTALL)
        match = text_re.match(self.text)
        if not match:
            return self.text

        self.truncated = True
        return '%s%s' % (match.group(1), '...')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
