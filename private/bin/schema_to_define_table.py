#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This script converts MySQL schema to define table statements suitable for
web2py db models.

For usage and help:

    schema_to_define_table.py -h    # Brief help displaying options
    schema_to_define_table.py -f    # Full help including examples and
                                    # notes on configuation options.
"""
# W0404: *Reimport %r (imported line %s)*
# pylint: disable=W0404
from applications.shared.modules.mysql_schema import ColumnLine, CreateLine, \
        MySQLColumn, MySQLTable, SchemaFile
from applications.shared.modules.web2py_sql import FieldPropertyDefaultsSet
from optparse import OptionParser
import gluon.main               # Sets up logging
import logging
import sys

LOG = logging.getLogger('app')

VERSION = '0.1'
INDENT = ' ' * 4

# web2py
# allowed field types: string, boolean, integer, double, text, blob, date,
# time, datetime, upload, password
# MySQL datatype: web2py datatype
DATA_TYPES = {
    'bit': 'integer',
    'tinyint': 'boolean',
    'smallint': 'integer',
    'mediumint': 'integer',
    'int': 'integer',
    'integer': 'integer',
    'bigint': 'integer',
    'real': 'double',
    'double': 'double',
    'float': 'double',
    'decimal': 'decimal',
    'numeric': 'decimal',
    'date': 'date',
    'time': 'time',
    'timestamp': 'datetime',
    'datetime': 'datetime',
    'year': 'integer',
    'char': 'boolean',
    'varchar': 'string',
    'binary': 'string',
    'varbinary': 'string',
    'tinyblob': 'blob',
    'blob': 'blob',
    'mediumblob': 'blob',
    'longblob': 'blob',
    'tinytext': 'text',
    'text': 'text',
    'mediumtext': 'text',
    'longtext': 'text',
    }


def define_table_code(table, defaults_set=None):
    """Return text representing the define table statement for the table.

    Args:
        table: MySQLTable object instance.

    Returns:
        string, Text representing the define table statement.

    Example:
        db.define_table('my_collection',
            Field('name',
                requires=IS_NOT_EMPTY()
                ),
            Field('group_id',
                'integer'
                ),
            migrate=False,
            )

    """

    lines = []
    indents = []
    indents.append("db.define_table('%s'" % table.name)
    for c in table.columns:
        indents.extend(define_field_code(c, defaults_set=defaults_set))
    indents.append('migrate=False')
    indents.append(')')
    delimiter = ',\n%s' % INDENT
    lines.append(delimiter.join(indents))
    return '\n'.join(lines)


def define_field_code(column, defaults_set=None):
    """Return text representing the define field statement for the column.

    Args:
        table: MySQLTable object instance.

    Returns:
        string, Text representing the define table statement.

    Example:
        Field('name',
            requires=IS_NOT_EMPTY()
            ),

    """
    lines = []

    if column.data_type in DATA_TYPES:
        column.data_type = DATA_TYPES[column.data_type]

    LOG.debug("column.name: {var}".format(var=column.name))
    # All params will have the format:  key=value
    # There is one exception, the fieldname.
    fieldname = None
    params = {}
    if defaults_set:
        for d in defaults_set.field_property_defaults:
            defaults = d.defaults_for(column)
            LOG.debug("defaults: {var}".format(var=defaults))
            if 'SKIP' in defaults:
                return []
            for defs in defaults:
                # Split parameters on equal sign. Then store in dict.
                # This will remove duplicates.
                if defs.find('=') >= 0:
                    k, v = defs.split('=', 1)
                    params[k] = v
                else:
                    fieldname = defs

    LOG.debug("params: {var}".format(var=params))
    if fieldname:
        lines.append("Field('%s'" % fieldname)
    else:
        lines.append("Field('%s'" % column.name)

    column_type = column.data_type
    if 'type' in params:
        column_type = params['type']

    if column.data_type == 'decimal':
        lines.append("%s'%s(%s,%s)'" % (INDENT, column_type,
                     column.length, column.decimals))
    else:
        lines.append("%s'%s'" % (INDENT, column_type))

    for k, v in params.items():
        if k == 'type':
            continue
        lines.append('%s%s' % (INDENT, '{k}={v}'.format(k=k, v=v)))

    lines.append('%s)' % INDENT)
    return lines


def usage_full():
    """Extended usage."""

    full_usage = """
GENERAL USAGE

    # Dump MySQL schema to a text file, and parse file
    $ mysqldump my_database -d > /path/to/my_database.sql
    $ schema_to_define_table.py /path/to/my_database.sql

    # Same thing in one liner
    mysqldump my_database -d | schema_to_define_table.py -


OVERVIEW

    This script converts MySQL schema into table and field definitions suitable
    for web2py db models.

    The script is not perfect. The output is intended to give the user a base
    to work from. The output is web2py compatible. You should be able to put it
    into the db.py model and your application will run without errors.


TABLE REFERENCES

    Web2py tables use the 'id' column as the primary key. A column in one table
    can reference a column in another by storing id's of the that table in it's
    column.

    For example

        table: artist
        fields
            id integer
            name varchar(255)

        table: album
        fields:
            id integer
            name varchar(255)
            artist_id integer

    The album field "artist_id" references the "id" field of the artist table.
    Web2py uses the IS_IN_DB() validator to ensure values in the column
    exist in the referenced table.

    The script will attempt to create an IS_IN_DB() validator on any column
    with a name like "<table>_id" where <table> is the name of another table.
    (Technically, <table> can be the column's own table as well.)

    For example, the artist/album tables would produce this validator:

        db.album.artist_id.requires = IS_IN_DB(db, db.artist.id,'%(name)s')


CONFIGURATION

    A configuration file can be use to store field property defaults, so the
    defaults can be used on subsequent uses.

    When defining fields in web2py, often there are patterns and repitition.
    For example, datetime fields frequently have the property
    "requires=IS_DATETIME()". A "creation_date" field used to record the
    timestamp a record was created might almost always have the
    "writable=False" property. By prescibing defaults in a configuration file,
    the user has a flexible way to indicate the defaults they'd like.


    Configuration File Option

    The --config-file, -c option is used to indicate the configuration file.

        $ schema_to_define_table.py /path/to/my_database.sql \
            -c /path/to/config_file.conf


    Configuration File Syntax

    The configuration file should be formated as per python's ConfigParser
    using sections of "name = value" pairs to indicate defaults.


    Example:

        [by_name]
        creation_date = writable=False

        [by_type]
        datetime = requires=IS_DATETIME()

    All defaults must be under two sections: by_name and by_type. Defaults in
    the "by_name" section are matched by field names. If a table field has the
    same name as the default name, the indicated property will be added to the
    field definition. Defaults in the "by_type" section are matched on field
    types. If a table field has the same type as the default type, the
    indicated property will be added to the field definition.

    Only one default setting is permitted per field name. Only one default
    setting is permitted per field type. However, defaults can include multiple
    properties. Use one line per property and indent subsequent lines.

    Using the following default, a field named 'creation_date' will have both
    the "writable=False" and the "update=request.now" properties.

        [by_name]
        creation_date = writable=False
            update=request.now

    A field may use defaults from both the "by_name" section and the "by_type"
    section if applicable.

    SKIP property

    The user can flag a field name or type to be skipped by using the keyword
    SKIP as the value. Any field matching the name or type will flagged as
    skipped will not be printed in the output. This setting is ideal for fields
    named 'id' as they are not included in the web2py tables definitions.

        [by_name]
        id = SKIP
        creation_date = writable=False
            update=request.now


    Syntax Details

    These two syntaxes are acceptable

        name = value
        name: value

    Everything after the first delimiter (= or :) is used for the property
    default except leading or trailing whitespace. (The newline character is
    whitespace.)

    Do not quote the value unless you want the quotes in the property default.

    Each property default must be on a separate line. If a name has several
    values, indent all but the first.

        name = value1
            value2
            value3

    Do not use comma delimiters to separate multiple values for a name unless
    you want the commas is part of the property default.
"""
    return full_usage


def main():
    """ Main routine. """

    usage = '%prog [options] schema_file' + '\nVersion: %s' % VERSION
    parser = OptionParser(usage=usage)

    parser.add_option('-c', '--config-file',
                    dest='config_file',
                    help='Name of configuration file.')
    parser.add_option('-f', '--full-help',
                    action='store_true',
                    dest='full_help',
                    help=' '.join(['Print full help and exit.',
                        'Full help includes examples and notes.']),
                    )
    parser.add_option('-i', '--include-headers', action='store_true',
                    dest='headers',
                    help='Print table documentation headers.')
    parser.add_option('-v', '--verbose', action='store_true',
                    dest='verbose',
                    help='Print messages to stdout',
                    )

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

    f = None
    if args[0] == '-':
        f = sys.stdin
    else:
        f = open(args[0], 'r')

    schema_file = SchemaFile(file_object=f)
    schema_file.parse()
    tables = []
    for line in schema_file.filter(['create', 'create_close', 'column']):
        LOG.debug('line: %s' % line.text)
        if line.type == 'create':
            create_line = CreateLine(text=line.text)
            create_line.parse()
            LOG.debug('create_line.table_name: %s'
                      % create_line.table_name)
            if create_line.table_name:
                table = MySQLTable(name=create_line.table_name)
                tables.append(table)
        if line.type == 'create_close':
            pass
        if line.type == 'column':
            if not len(tables) > 0:
                raise ValueError('Column without table: {text}'.format(
                        text=line.text))
            column_line = ColumnLine(text=line.text)
            column_line.parse()
            column = MySQLColumn(
                name=column_line.name,
                data_type=column_line.type,
                length=column_line.length,
                decimals=column_line.decimals,
                table=tables[-1],
                attributes=column_line.attributes,
                )
            tables[-1].columns.append(column)
    f.close()

    # Set tables references
    # This step must be done after all MySQLTable objects are defined and
    # added to tables list since so the tables are available for columns that
    # reference it.
    for t in tables:
        for c in t.columns:
            c.set_referenced_table(tables=tables)
            if c.referenced_table:
                c.set_referenced_column()
                c.set_descriptor_column()

    defaults_set = None
    if options.config_file:
        defaults_set = FieldPropertyDefaultsSet()
        defaults_set.load(options.config_file)

    for t in tables:
        print ''
        if options.headers:
            print '"""'
            print t.documentation()
            print '"""'
        print define_table_code(t, defaults_set=defaults_set)

    first = True
    for t in sorted(tables, cmp=lambda x, y: cmp(x.name, y.name)):
        for c in sorted(t.columns, cmp=lambda x, y: cmp(x.name,
                        y.name)):
            if c.referenced_table:
                if first:
                    print ''
                first = False
                print c.requires_statement()


if __name__ == '__main__':
    main()
