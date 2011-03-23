#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
page.py

Classes related to web pages.

"""

from applications.shared.modules.download_agent import DownloadAgent, \
    DynamicMozillaCookieJar
from BeautifulSoup import BeautifulSoup
import HTMLParser
import re
import sys


class DownloadError(Exception):

    """General exception for web page download errors"""

    def __init__(self, messages=None):
        """Constructor.

        Args:
            messages: list, List of error messages.
        """

        super(DownloadError, self).__init__()
        self.messages = messages or []
        return

    def __repr__(self):
        return '\n'.join([x for x in self.messages])

    def __str__(self):
        return repr(self)


class WebPage(object):

    """Class representing a web page."""

    retries = 5  # Number of times to retry downloading
    control_chars = None  # Cache of control chars string
    control_chars_re = None  # Cache of control chars re

    def __init__(self, url, post_data=None):
        """ Constructor.

        Args:
            url: string, eg http://www.example.com
            post_data: dict, POST data parameters.
        """

        self.url = url
        self.post_data = post_data
        self.raw_content = None
        self.content = None

        # Pages may have some foo that BeautifulSoup kaks on.
        # Store a list of markup massages in an object property.

        # Here is the code in BeautifulSoup.py
        # class BeautifulStoneSoup(Tag):
        #   def _feed(self, inDocumentEncoding=None, isHTML=False):
        #        for fix, m in self.markupMassage:
        #            markup = fix.sub(m, markup)
        #

        # Test using python console:
        # >>> s = 'html with foo'
        # >>> fix.sub(lambda_func, s)
        #
        # Example:
        # >>> s = '<TD id="sublistHeaderLine1" width=11%">'
        # >>> re.compile(r'width=([0-9]+)%">').sub(
        #     lambda match: 'width=' + match.group(1) + '%">', s)

        # Code to use to create re and fix
        #
        # tests = ['<OPTION value="455" No.1 MARK VI">',
        #          '<OPTION value="Webley .455" MARK VI">']
        # fix_re = re.compile(r'(<option value=)"([^"]+"[^="]+)">',
        #                     re.IGNORECASE)
        # for t in tests:
        #     print t
        #     match = fix_re.match(t)
        #     if match:
        #         t1 = fix_re.sub(match.group(1) + "'" + match.group(2) + "'>"
        #                         , t)
        #         print t1

        self.bs_massage = []
        # Convert ampersand character from hex to int,
        #    eg, &#x26                  => &#38
        #    eg, &#xB3                  => &#179
        #    eg, &#x30D6                => &#12501
        self.bs_massage.append((re.compile('&#x([A-Z0-9]{2,4})'),
                               lambda match: '&#' \
                               + str(int(match.group(1), 16))))
        # Fix missing quotes.
        #    eg style=display:none;"    => style="display:none;"
        self.bs_massage.append((re.compile('style=display:none;"'),
                               lambda match: 'style="display:none;"'))
        # Fix invalid tags
        #    eg <mhafner@imdb.com>      => mhafner@imdb.com
        self.bs_massage.append((re.compile('<([^<>]+@imdb.com)>'),
                               lambda match: match.group(1)))
        # Fix malformed <br> tag
        #    eg <br</p>                 => <br></p>
        self.bs_massage.append((re.compile('<br<([^<>]+)>'),
                               lambda match: '<br><' + match.group(1) \
                               + '>'))
        # Fix bad end tag
        #    eg u'</%def>'              => </div>
        self.bs_massage.append((re.compile('</\%def>'), lambda match: \
                               '</div>'))
        # Missing space
        #    eg class="script_loader"allowtransparency="true"       =>
        #       class="script_loader" allowtransparency="true"
        bs_re = \
            re.compile('class="script_loader"allowtransparency="true"')
        self.bs_massage.append((bs_re, lambda match: \
                    'class="script_loader" allowtransparency="true"'))
        # Remove troublesome sidebar
        #    eg <div id="tn15lhs">... </div><div id="tn15main">     =>
        #       </div><div id="tn15main">
        bs_re = re.compile('<div id="tn15lhs">.*<div id="tn15main">',
                           re.DOTALL)
        self.bs_massage.append((bs_re, lambda match: \
                               '<div id="tn15main">'))
        # Replace script hack. Idiots.
        #    eg <scr'+'ipt ... </scr'+'ipt>                         =>
        #       <script ... </script>
        self.bs_massage.append((re.compile("""<([/]?)scr'\+'ipt""",
                               re.IGNORECASE), lambda match: '<' \
                               + match.group(1) + 'script'))
        # Missing font attribute quotes
        #   eg <FONT SIZE="1" TYPE=arial, helvetica, sans-serif>
        #      <FONT SIZE="1" TYPE="arial, helvetica, sans-serif">
        bs_re = \
            re.compile(r'(<font.*\s+(?:face|type)\s*=\s*)([^"].*?)(\s*(\w+=.*)?\s*>)'
                       , re.IGNORECASE)
        self.bs_massage.append((bs_re, lambda match: match.group(1) \
                               + '"' + match.group(2) + '"' \
                               + match.group(3)))
        # Missing leading quote on attribute
        #   eg <TD id="sublistHeaderLine1" width=11%">
        #      <TD id="sublistHeaderLine1" width="11%">
        self.bs_massage.append((re.compile(r'width=([0-9]+)%">'),
                               lambda match: 'width="' + match.group(1) \
                               + '%">'))
        # Double quotes within quoted attribute value.
        #   eg. <OPTION value=""22"">&quot;22&quot;</OPTION>
        #       <OPTION value='"22"'>&quot;22&quot;</OPTION>
        #   eg  <OPTION value="Mod. S. 775 "1874 Cavalry" .45/70">Mod</OPTION>
        #       <OPTION value='Mod. S. 775 "1874 Cavalry" .45/70'>Mod</OPTION>
        bs_re = \
            re.compile(r"""
                    (                           # group start
                    <option\svalue=             # option tag with value attr
                    )                           # group close
                    "                           # First quote
                    (                           # group start
                    [0-9a-zA-Z \-\.\/]*         # optional leading text
                    "[0-9a-zA-Z \-\.\/]+"       # text surrounded by quotes
                    [0-9a-zA-Z \-\.\/]*         # optional trailing text
                    )                           # group close
                    ">                          # quote and tag close
                    """
                       , re.IGNORECASE | re.VERBOSE)
        self.bs_massage.append((bs_re, lambda match: match.group(1) \
                               + "'" + match.group(2) + "'>"))
        # Quotes within quoted attribute value. Must follow double quotes
        # within quoted.
        #   eg. <OPTION value="455" No.1 MARK VI">
        #       <OPTION value='455" No.1 MARK VI'>
        bs_re = re.compile(r'(<option value=)"([^"]+"[^="]+)">',
                           re.IGNORECASE)
        self.bs_massage.append((bs_re, lambda match: match.group(1) \
                               + "'" + match.group(2) + "'>"))
        # Extra quote
        #   eg. <table class="footer" id="amazon-affiliates"">
        #       <table class="footer" id="amazon-affiliates">
        #   Regexp explanation: Any string ending in ""> except where proceeded
        #   by an equal sign , eg, this is ok <a href = "">
        self.bs_massage.append((re.compile("""([^= ])\s*"">"""),
                               lambda match: match.group(1) \
                               + """ ">"""))
        # Missing quote in style tag.
        #   eg. <TD style="font-size : 10pt; height="35">
        #       <TD style="font-size : 10pt;" height="35">
        bs_re = re.compile(r'(<td style="[^"]+)\s([A-Za-z_]+="[^"]*")',
                           re.IGNORECASE)
        self.bs_massage.append((bs_re, lambda match: match.group(1) \
                               + '"' + match.group(2)))

        # Rogue perl tag (imdb)  Newer versions of Beautiful Soup handle this
        #   eg. <div class="inputs"></%perl></div>
        #      <div class="inputs"></div>
        bs_re = re.compile(r'</%perl>')
        self.bs_massage.append((bs_re, lambda match: ''))
        return

    def as_soup(self):
        """
        Return the site page contents as a BeautifulSoup object
        """

        try:
            soup = BeautifulSoup(self.content, smartQuotesTo=None,
                                 convertEntities='xml',
                                 markupMassage=self.bs_massage)
        except HTMLParser.HTMLParseError, err:
            print >> sys.stderr, 'ERROR: Not able to parse page %s' \
                % self.url
            print >> sys.stderr, err
            # with open('/root/tmp/raw.htm', 'w') as f_dump:
            #     f_dump.write(self.raw_content + '\n')
            # with open('/root/tmp/content.htm', 'w') as f_dump:
            #     f_dump.write(self.content + '\n')
            return

        return soup

    def get(
        self,
        cookie_jar=None,
        cookie=None,
        cookie_filename=None,
        referrer=None,
        request_headers=None,
        ):
        """Get the content of the webpage.

        Note:
            Content is stored in "content" property.

        Args:
            cookie_jar = cookielib.CookieJar object instance
            cookie: cookielib.Cookie object instance
            referrer: string, Url of referrer.

        Raises:
            DownloadError if web page download is unsuccessful
        """

        if not referrer:
            referrer = self.url

        if not cookie_jar and cookie_filename:
            cookie_jar = DynamicMozillaCookieJar(filename=cookie_filename)
            cookie_jar.create_file()

        agent = DownloadAgent(
            accept_encoding='gzip,deflate',
            cookie_jar=cookie_jar,
            cookie=cookie,
            post_data=self.post_data,
            referrer=referrer,
            request_headers=request_headers,
            retries=self.retries,
            url=self.url,
            )
        agent.download()

        if not agent.content:
            if agent.errors:
                raise DownloadError(messages=agent.errors)
        self.raw_content = agent.content

        # with open('/root/tmp/raw.htm', 'w') as f_dump:
        #    f_dump.write(self.raw_content + '\n')

        self.content = self.scrub_content()
        return

    def scrub_content(self, html=None):
        """Scrub page contents

        Replaces control characters and unicode characters with '?'
        """

        if html is None:
            html = self.raw_content

        # Remove DOS eol characters
        html = html.replace('\r\n', '\n')

        html = html.decode('utf-8', 'ignore').encode('ascii',
                'xmlcharrefreplace')

        if not self.control_chars:

            # Skip chr(9), tab should be fine (don't want it replaced with ?
            # Skip chr(10), newline is needed in json

            self.control_chars = ''.join([unichr(x) for x in range(0,
                    9) + range(11, 32)])
        if not self.control_chars_re:
            self.control_chars_re = re.compile('[%s]'
                    % re.escape(self.control_chars))
        html = self.control_chars_re.sub('?', html)
        return html


