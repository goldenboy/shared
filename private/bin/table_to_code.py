#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This script creates a shell module and test script for a database table.

For usage and help:

    table_to_code.py -h    # Brief help displaying options.
    table_to_code.py -f    # Full help including examples.
"""
# W0404: *Reimport %r (imported line %s)*
# pylint: disable=W0404
from optparse import OptionParser
import logging
import logging.config
import re
import sys

VERSION = '0.1'

logging.config.fileConfig('/srv/http/igeejo/web2py/logging.conf')
LOG = logging.getLogger('app')


def class_code(database, table):
    """Return the class definition code.

    Args:
        database: string, The name of the database.
        table: string, The name of the database table.

    Returns:
        string, the class definition code.
    """

    # The class name is the database table name in title format with
    # underscores removed.
    class_name = re.sub('_', '', table.title())

    return """
class {class_name}(DbObject):
    \"""Class representing a record of the {database} {table} table. \"""

    def __init__(self, tbl_, **kwargs):
        super({class_name}, self).__init__(tbl_, **kwargs)
        return""".format(class_name=class_name, database=database, table=table)


def module_code(database, table):
    """Return the class definition code.

    Args:
        database: string, The name of the database.
        table: string, The name of the database table.

    Returns:
        string, the class definition code.
    """

    cls_code = class_code(database, table)

    return """#!/usr/bin/python

\"""
{table}.py

Classes related to {table}.

\"""

from applications.shared.modules.database import DbObject

{cls_code}""".format(cls_code=cls_code, table=table)


def test_class_code(table):
    """Return the test class definition code.

    Args:
        application: string, The name of the web2py application.
        table: string, The name of the database table.

    Returns:
        string, the class definition code.
    """

    # The class name is the database table name in title format with
    # underscores removed.
    class_name = re.sub('_', '', table.title())
    return """
class Test{class_name}(unittest.TestCase):

    \"""Test class for {class_name}.\"""

    def test____init__(self):
        self.assertTrue({class_name}())
        self.assertTrue(hasattr({class_name}(), '_log'))
        return""".format(class_name=class_name)


def test_script_code(application, table):
    """Return the class definition code.

    Args:
        application: string, The name of the web2py application.
        table: string, The name of the database table.

    Returns:
        string, the class definition code.
    """

    test_cls_code = test_class_code(table)
    class_name = re.sub('_', '', table.title())

    return """#!/usr/bin/python

\"""
test_{table}.py

Test suite for {application}/modules/{table}.py

\"""
from applications.shared.modules.local.test_runner import LocalTestSuite, \\
    ModuleTestSuite
from applications.{application}.modules.{table} import {class_name}
import sys
import unittest

# pylint: disable=C0111


{test_cls_code}


def main():
    \"""Run all tests in this module\"""
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()""".format(application=application, class_name=class_name,
            table=table, test_cls_code=test_cls_code)


def usage_full():
    """Extended usage."""

    full_usage = """
EXAMPLES

    # Print the class definition code for a database table.
    $ table_to_code.py my_database.my_table

    # Print the test class definition code for a database table.
    $ table_to_code.py -c my_database.my_table

    # Create a package module for a database table.
    $ table_to_code.py -m my_database.my_table > mytable.py

    # Create a test script for a database table.
    $ table_to_code.py -t my_database.my_table > test_mytable.py
"""
    return full_usage


def main():
    """ Main routine. """

    usage = '%prog [options] database.table' + '\nVersion: %s' % VERSION
    parser = OptionParser(usage=usage)

    parser.add_option('-a', '--application', dest='application',
                      help='Web2py application name.')
    parser.add_option('-c', '--test-class', action='store_true',
                      dest='test_class', help='Print the test class.')
    parser.add_option('-f', '--full-help', action='store_true',
                      dest='full_help',
                      help=' '.join(['Print full help and exit.',
                          'Full help includes examples and notes.']),
                      )
    parser.add_option('-m', '--module', action='store_true',
                      dest='module', help='Print the module.')
    parser.add_option('-t', '--test-script', action='store_true',
                      dest='test_script', help='Print the test script.')
    parser.add_option('-v', '--verbose', action='store_true',
                      dest='verbose', help='Print messages to stdout')

    (options, args) = parser.parse_args()

    if options.verbose:
        # Add a stream handler to print messages to stderr.
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        LOG.addHandler(ch)

    if options.full_help:
        parser.print_help()
        print
        print usage_full()
        return

    if len(args) == 0:
        parser.print_help()
        exit(1)

    try:
        (database, table) = args[0].split('.')
    except ValueError:
        print >> sys.stderr, \
            'Invalid database or table. Use format database.table'
        parser.print_help()
        exit(1)

    application = options.application or database

    if options.test_class:
        LOG.debug("printing test class")
        print test_class_code(table)
    elif options.module:
        LOG.debug("printing module")
        print module_code(database, table)
    elif options.test_script:
        LOG.debug("printing test script")
        print test_script_code(application, table)
    else:
        LOG.debug("printing class")
        print class_code(database, table)


if __name__ == '__main__':
    main()
