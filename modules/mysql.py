#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Classes for handling mysql.

"""

import os


class LocalMySQL(object):

    """Class representing the local MySQL connection parameters."""

    def __init__(
        self,
        request=None,
        database=None,
        user=None,
        password=None,
        hostname='127.0.0.1',
        port=None,
        charset='utf8',
        sqldb=None,
        ):
        """Constructor."""

        self.request = request
        self.database = database
        self.user = user
        self.password = password
        self.hostname = hostname
        self.port = port
        self.charset = charset
        self.sqldb = sqldb

        if not self.port:
            self.set_port()
        if not self.sqldb:
            self.set_sqldb()
        return

    def set_port(self):
        """Set the MySQL port
        The port is set to the first value found in:
        1. request.env.web2py_mysql_tcp_port (set in httpd.conf)
        2. MYSQL_TCP_PORT env variable
        """

        port = None
        if self.request:
            port = self.request.env.web2py_mysql_tcp_port
        if not port:
            port = os.environ.get('MYSQL_TCP_PORT', None)
        self.port = port

    def set_sqldb(self):
        """Set the sqldb property."""

        self.sqldb = '%s://%s:%s@%s:%s/%s?set_encoding=%s' % (
            'mysql',
            self.user,
            self.password,
            self.hostname,
            self.port,
            self.database,
            self.charset,
            )

    def __repr__(self):
        return str(self.__dict__)


