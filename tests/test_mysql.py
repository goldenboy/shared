#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/mysql.py

"""

from applications.shared.modules.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.mysql import LocalMySQL
from gluon.storage import Storage
import os
import sys
import unittest

# pylint: disable=C0111


class TestLocalMySQL(unittest.TestCase):

    def test____init__(self):
        local_mysql = LocalMySQL()
        self.assertTrue(local_mysql)  # Creates object
        self.assertTrue(local_mysql.port)  # Sets port
        self.assertTrue(local_mysql.sqldb)  # Sets sqldb
        return

    def test__set_port(self):
        port_1 = '1111'
        port_2 = '2222'
        port_3 = '3333'
        local_mysql = LocalMySQL(port=port_1)
        self.assertTrue(local_mysql.port, port_1)  # Provided port is used

        save_env_port = os.environ.get('MYSQL_TCP_PORT')

        del os.environ['MYSQL_TCP_PORT']
        local_mysql = LocalMySQL()
        # No port, no http env var, no uses env var, not set
        self.assertFalse(local_mysql.port)

        os.environ['MYSQL_TCP_PORT'] = port_2
        local_mysql = LocalMySQL()
        # No port, no http env var, uses env var
        self.assertTrue(local_mysql.port, port_2)

        request = Storage()
        request.env = Storage()
        request.env.web2py_mysql_tcp_port = port_3

        local_mysql = LocalMySQL()
        self.assertTrue(local_mysql.port, port_3)  # No port, uses http env var

        os.environ['MYSQL_TCP_PORT'] = save_env_port
        return

    def test__set_sqldb(self):
        sqldb_1 = '__test_sqldb_1__'
        local_mysql = LocalMySQL(sqldb=sqldb_1)
        self.assertEqual(local_mysql.sqldb, sqldb_1)  # Uses provided

        local_mysql.database = 'DB'
        local_mysql.user = 'USER'
        local_mysql.password = 'PWD'
        local_mysql.hostname = 'HOSTNAME'
        local_mysql.port = 'PORT'
        local_mysql.charset = 'CHARS'
        local_mysql.set_sqldb()
        self.assertEqual(local_mysql.sqldb,
                         'mysql://USER:PWD@HOSTNAME:PORT/DB?set_encoding=CHARS'
                         )
        return


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()

