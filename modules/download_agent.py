#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Classes for handling url downloads.

"""

import StringIO
import cookielib
import gzip
import httplib
import os
import pwd
import socket
import time
import urllib
import urllib2

# Verbose levels

ERROR = 0
WARN = 0
INFO = 1
DEBUG = 2


class DownloadAgent(object):

    """
    Class similar to urllib/urllib2 used to handle downloading.
    """

    def __init__(
        self,
        accept_encoding=None,
        cookie=None,
        cookie_jar=None,
        post_data=None,
        referrer=None,
        request_headers=None,
        retries=0,
        url=None,
        ):
        """Constructor.

        Args:
            accept_encoding: string, A comma-seperated list of encoding types.
            cookie: cookielib.Cookie instance
            cookie_jar: cookielib.CookieJar instance
            post_data: dict, POST parameters.
            referrer: string, Referrer url.
            retries: integer, Number of times to retry incase of failure.
            url: string, Url to download
        """

        self.accept_encoding = accept_encoding
        self.cookie = cookie
        if cookie_jar != None:
            self.cookie_jar = cookie_jar
        else:
            self.cookie_jar = cookielib.CookieJar()
        self.post_data = post_data
        self.referrer = referrer
        self.request_headers = {}
        if request_headers:
            self.request_headers = request_headers
        self.retries = retries
        self.url = url
        self.urllib_quote_safe = """:/?&="+-"""
        self.response = None
        self.content = None
        self.errors = []
        return

    def download(self):
        """Download url and store content."""

        if not self.url:
            return

        if self.cookie:
            self.cookie_jar.set_cookie(self.cookie)
        cookie_filename = None
        try:
            cookie_filename = self.cookie_jar.filename
        except AttributeError:
            pass

        if cookie_filename:
            if os.access(cookie_filename, os.F_OK):
                self.cookie_jar.load(ignore_discard=True, ignore_expires=True)

        cookie_handler = urllib2.HTTPCookieProcessor(self.cookie_jar)
        opener = urllib2.build_opener(cookie_handler)
        urllib2.install_opener(opener)

        scrubbed_url = urllib.quote(self.url,
                                    safe=self.urllib_quote_safe)
        req = self.request(scrubbed_url)

        tries = 1 + self.retries
        while tries:
            try:
                self.response = urllib2.urlopen(req, timeout=10)
                tries = 0
            except IOError, err:
                error_msg = ErrorMessage(err)
                error_msg.identify()
                if error_msg.retry:
                    tries -= 1
                else:
                    tries = 0
                if error_msg.messages:
                    self.errors.extend(error_msg.messages)
                if not error_msg.identified:
                    raise
            except httplib.BadStatusLine:

                # PB reports this from time to time

                tries = 0
            if tries > 0:
                time.sleep(1)

        if not self.response:
            self.errors.append('ERROR: No response from %s.' % self.url)
            return

        #import sys      # FIXME
        #print >> sys.stderr, "FIXME self.url: {var}".format(var=self.url)
        #for i in req.header_items():
        #    print >> sys.stderr, "{k}: {v}".format(k=i[0], v=i[1])
        #print >> sys.stderr, ''
        #print >> sys.stderr, 'self.response.info(): {var}'.format(var=self.response.info())
        #print >> sys.stderr, ''
        if cookie_filename:
            self.cookie_jar.save(ignore_discard=True, ignore_expires=True)

        info = self.response.info()
        encoding = ''
        if 'Content-Encoding' in info:
            encoding = info['Content-Encoding']
        content_fh = self.response

        # with open('/root/tmp/jimk.txt', 'w') as f_dump:
        #    f_dump.write(content_fh.read() + "\n")

        if encoding == 'gzip':
            compressedstream = StringIO.StringIO(self.response.read())
            content_fh = gzip.GzipFile(fileobj=compressedstream)

        self.content = content_fh.read()
        self.response.close()
        return

    def request(self, url):
        """Create urllib2.Request for the download.

        Args:
            url: string, the url for download.
        """

        data = None
        if self.post_data:
            data = urllib.urlencode(self.post_data)
        req = urllib2.Request(url, data)
        # Add default request headers
        user_agent = ' '.join(('Mozilla/5.0',
                              '(X11; U; Linux i686; en-US; rv:1.9.2.10)',
                              'Gecko/20100928', 'Firefox/3.5.7'))
        req.add_header('User-Agent', user_agent)
        # Add customer request headers
        for k,v in self.request_headers.items():
            req.add_header(k,v)
        if self.accept_encoding:
            req.add_header('Accept-encoding', self.accept_encoding)
        if self.referrer:
            req.add_header('Referer', urllib.quote(self.referrer,
                           safe=self.urllib_quote_safe))
        return req


class DynamicMozillaCookieJar(cookielib.MozillaCookieJar):
    """This is a subclass of MozillaCookieJar adding methods for creating the
    cookie file.
    """

    def __init__(self, filename=None):
        cookielib.MozillaCookieJar.__init__(self, filename=filename)

    def create_file(self):
        """Create a cookie file. ...
        """
        cookie_filename = None
        try:
            cookie_filename = self.filename
        except AttributeError:
            return

        if not cookie_filename:
            return

        # Create the path to the cookie file if it does not exist.
        dir_name = os.path.dirname(cookie_filename)
        user = 'http'
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            # Change ownership on the session cookie file so http can access it.
            os.chown(dir_name,
                    pwd.getpwnam(user).pw_uid,
                    pwd.getpwnam(user).pw_gid)

        # Create empty cookie file if not exists
        if not os.path.exists(cookie_filename):
            self.save()
            # Change ownership on the session cookie file so http can access it.
            os.chown(cookie_filename,
                    pwd.getpwnam(user).pw_uid,
                    pwd.getpwnam(user).pw_gid)
        return


class ErrorMessage(object):

    """Class to represent download agent error messages"""

    def __init__(self, err):
        """Constructor.

        Args:
            err: IOError exception message
        """

        self.err = err
        self.retry = False
        self.messages = []
        self.identified = False

    def identify(self):
        """Identify the error based on it's message

        urllib2.urlopen produces two types of errors, HTTPError and
        URLError. Trap for each.

        NOTE: The retry and identified attributes are set as
        appropriate.
        """

        # HTTPError

        if hasattr(self.err, 'code'):
            msg = 'HTTP error code: {code}'.format(code=self.err.code)
            self.messages.append(msg)
            if self.err.code == 503:
                self.retry = True
            self.identified = True
            return

        # URLError

        if hasattr(self.err, 'reason'):
            msg = \
                "Can't connect, {reason}".format(reason=self.err.reason)
            self.messages.append(msg)
            self.identified = True
            if isinstance(self.err.reason, socket.timeout):
                self.messages.append('Timeout error')
                self.retry = True
            elif isinstance(self.err.reason, socket.gaierror):
                msg = 'Get address info error. Likely invalid url.'
                self.messages.append(msg)
            elif hasattr(self.err.reason, 'find') \
                and self.err.reason.find('timed out') > -1:
                self.messages.append('Timeout error')
                self.retry = True
        return


