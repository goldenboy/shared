#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
tokens.py

Classes related to hash tokens.

"""

from applications.shared.modules.mysql import LocalMySQL
from applications.shared.modules.stickon.tools import SettingsLoader
from gluon.storage import Settings
from gluon.tools import Auth, Crud, Mail, Service
import os
import hashlib

# C0103: *Invalid name "%s" (should match %s)*
# Some variable names are adapted from web2py.
# pylint: disable=C0103


class WordsRequired(Exception):
    pass

class HashToken(object):

    """Class representing a hash token"""

    def __init__(self, words=None, require_words=True):
        """Constructor.

        Args:
            words: list, list of words used in hash construction.
            require_words: If True, an exception is raised if the words list
                is not provided or is empty.
        """
        self.words = []
        if words:
            self.words = words
        self.require_words = require_words
        self.token = self.generate()
        return

    def generate(self):
        """Generate the hash token.

        Raises: WordsRequired if require_words is True and words list is empty.
        """

        if self.require_words and not self.words:
            raise WordsRequired('Hash token generation fail. Words required.')

        return hashlib.md5('!'.join(self.words)).hexdigest()
