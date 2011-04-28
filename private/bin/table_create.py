#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This script prints basic mysql table create commands from text.

For usage and help:

    table_create.py -h    # Brief help displaying options.
    table_create.py -f    # Full help including examples.
"""
# W0404: *Reimport %r (imported line %s)*
# pylint: disable=W0404
from applications.shared.modules.mysql_schema import MySQLColumn, MySQLTable
from optparse import OptionParser
import gluon.main               # Sets up logging
import logging
import sys

VERSION = '0.1'

OPTIONS = ['description', 'sequence']

LOG = logging.getLogger('app')


class CreateTable(MySQLTable):
    """Class representing a MySQL Table with benefits."""

    def __init__(self, name, column_names, data):
        """Constructor

        """
        self.name = name
        self.column_names = column_names
        self.data = data
        self.columns = []
        MySQLTable.__init__(self, name)

    def set_columns(self):
        """Set the column values based on column names."""
        for col_name in self.column_names:
            if col_name == 'id':
                self.columns.append(MySQLColumn(name=col_name,
                    data_type='integer', length=11,
                    attributes=['NOT NULL', 'AUTO_INCREMENT'], table=self))
            if col_name == 'name':
                self.columns.append(MySQLColumn(name=col_name,
                    data_type='varchar', length=255,
                    attributes=['DEFAULT NULL'], table=self))
            if col_name == 'description':
                self.columns.append(MySQLColumn(name=col_name,
                    data_type='varchar', length=512,
                    attributes=['DEFAULT NULL'], table=self))
            if col_name == 'sequence':
                self.columns.append(MySQLColumn(name=col_name,
                    data_type='integer', length=11,
                    attributes=['DEFAULT 0'], table=self))


def created_tables(lines):
    """Create table objects from lines of text.

    Args:
        lines: list, lines of text.

    Return:
        list, list of CreateTable instances
    """
    if not lines:
        return []

    tables = []
    current_table = ''
    columns = []
    rows = []
    sequence = 0
    for line in lines:
        if not line.strip():
            continue
        if not line[0].isspace():
            if current_table:
                tables.append(CreateTable(current_table, columns, rows))
            words = line.strip().split()
            if len(words) > 0:
                current_table = words[0]
                columns = ['id', 'name']
            if len(words) > 1:
                for word in words[1:]:
                    if word not in OPTIONS:
                        LOG.error('Invalid option: {opt}'.format(opt=word))
                columns.extend(words[1:])
            rows = []
            sequence = 0
        else:
            l = []
            for column in columns:
                if column == 'id':
                    l.append(None)
                if column == 'name':
                    l.append(line.strip())
                if column == 'description':
                    l.append('')
                if column == 'sequence':
                    sequence += 1
                    l.append(sequence)
            rows.append(tuple(l))
    if current_table:
        tables.append(CreateTable(current_table, columns, rows))
    return tables


def usage_full():
    """Extended usage."""

    full_usage = """
OVERVIEW

    The script prints the CREATE TABLE and INSERT INTO table commands from
    text.

EXAMPLES

    $ cat ~/tmp/my_condition.txt
    my_condition description sequence
        excellent
        good
        fair

    table_create.py ~/tmp/my_condition.txt

        DROP TABLE IF EXISTS `my_condition`;
        CREATE TABLE `my_condition` (
          `id` integer(11) NOT NULL AUTO_INCREMENT,
          `name` varchar(255) DEFAULT NULL,
          `description` varchar(512) DEFAULT NULL,
          `sequence` integer(11) DEFAULT 0,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

        LOCK TABLE `my_condition` WRITE;
        INSERT INTO `my_condition` VALUES
        (NULL, 'Excellent', '', 1),
        (NULL, 'Good', '', 2),
        (NULL, 'Fair', '', 3)
        ;
        UNLOCK TABLES;


TEXT FORMAT

    table_name [option option ...]
        name_1
        name_2
        ...
        name_n


OPTIONS
    description:
        Append a description field. The value of the field in all records is
        set to empty string.

    sequence:
        Append a sequence field. A sequence field is used to prescribe an
        order to the database records. The value of the field starts at 1 and
        is incremented for each record.

NOTES

    The order of the options determines the order the fields are appended to
    the table definition.
"""
    return full_usage


def main():
    """ Main routine. """

    usage = '%prog [options] /path/to/file' + '\nVersion: %s' % VERSION
    parser = OptionParser(usage=usage)

    parser.add_option('-f', '--full-help', action='store_true',
                      dest='full_help',
                      help=' '.join(['Print full help and exit.',
                          'Full help includes examples and notes.']),
                      )
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

    lines = []
    f = None
    if args[0] == '-':
        f = sys.stdin
    else:
        f = open(args[0], 'r')

    for line in f.readlines():
        lines.append(line)

    for table in created_tables(lines):
        table.set_columns()
        print table.create_statement(drop=True)
        print table.insert_statement(table.data, lock=True)

if __name__ == '__main__':
    main()
