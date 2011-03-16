#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
url.py

Classes related to urls of IMDb pages.

"""

import urllib
import urlparse


class UniformResourceLocator(object):
    """Class representing a url"""
    def __init__(self, value):
        """Constructor.

        Args:
            value: str, Url value. eg 'http://www.example.com?abc=123'
        """
        self.value = value

    def update_query(self, query_pairs):
        """Add parameters to the url value.

        Args:
            query_pairs: dict, Dictionary of name-value pairs to be updated in
                the url query string.

        Example:
            self.value = 'http://www.example.com?abc=123'
            self.update_query({'def': 456})

            Then:
            self.value = 'http://www.example.com?abc=123&def=456'
        """
        if not query_pairs:
            return
        scheme, netloc, url, params, query, fragment = urlparse.urlparse(
                self.value)
        query_d = dict(urlparse.parse_qsl(query))
        query_d.update(query_pairs)
        self.value = urlparse.urlunparse(
            (scheme, netloc, url, params, urllib.urlencode(query_d), fragment))
        return
