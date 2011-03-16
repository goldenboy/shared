#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Classes for handling mysql schema.

"""

import re

# attribute name: expects an argument to follow

ATTRIBUTES = {
    'AUTO_INCREMENT': 0,
    'COMMENT': 1,
    'DEFAULT': 1,
    'NOT NULL': 0,
    'NULL': 0,
    'PRIMARY KEY': 0,
    'PRIMARY': 0,
    'UNIQUE KEY': 0,
    'UNIQUE': 0,
    }


class ColumnLine(object):

    """Class representing a MySQL schema column definition line"""

    def __init__(self, text=''):
        """Constructor.

        Args:
            text: string, The text of the line.
        """

        self.text = text
        self.name = ''
        self.type = ''
        self.length = None
        self.decimals = None
        self.attributes = []
        self.default = None
        self.comment = None
        return

    def parse(self):
        """Parse a column line into its components

        Raises:
            ValueError if column text is no parsable.

        """

        if not self.text:
            return

        col_re = \
            re.compile(r"""
            \s*                     # optional leading whitespace
            [`]?                    # optional `
            ([a-zA-Z][\w\s#\-]+)    # column name
            [`]?                    # optional `
            \s+                     # whitespace
            ([a-zA-Z]+)             # column type
            (?:                     # length start
            \(                      # opening parenthesis of length
            ([0-9]+)                # length group
            (?:                     # decimals start
            ,\s*([0-9]+)            # comma and decimals group
            )?                      # decimals end, optional
            \)                      # closing parenthesis of length
            )?                      # length end, optional
            ([^,]*)
            [,]?                    # trailing comma
            $                       # end of line anchor
            """, re.VERBOSE)
        col_match = col_re.match(self.text)
        if not col_match or len(col_match.groups()) < 4:
            raise ValueError('Column line is not parsable: {text}'.format(
                text=self.text))
        self.name = col_match.group(1).strip()
        self.type = col_match.group(2).strip()
        if col_match.group(3):
            self.length = int(col_match.group(3))
        if col_match.group(4):
            self.decimals = int(col_match.group(4))
        column_attributes = ''
        if col_match.group(5):

            # Eg NOT NULL AUTO_INCREMENT

            column_attributes = col_match.group(5).strip()
        if column_attributes:
            for attr in sorted(ATTRIBUTES.keys()):
                if ATTRIBUTES[attr]:
                    attr_re = re.compile(r"""%s '([^']+)'""" % attr)
                else:
                    attr_re = re.compile(r'%s' % attr)
                col_search = attr_re.search(column_attributes)
                if col_search:
                    self.attributes.append(attr)
                    if col_search.groups():
                        if attr == 'COMMENT':
                            self.comment = col_search.group(1)
                        if attr == 'DEFAULT':
                            self.default = col_search.group(1)

        self.filter_attributes('NOT NULL', 'NULL')
        self.filter_attributes('PRIMARY KEY', 'PRIMARY')
        self.filter_attributes('UNIQUE KEY', 'UNIQUE')
        return

    def filter_attributes(self, keep_attr, give_way_attr):
        """Filter mutually exclusive attributes.

        If both the keep and give_way attributes are in the attributes
        list, remove the give_way attribute.

        Args:
            keep_attr: string (optional) The ...
            give_way_attr:

        """

        if keep_attr in self.attributes and give_way_attr \
            in self.attributes:
            self.attributes.remove(give_way_attr)


class CreateLine(object):

    """Class representing a MySQL schema create table line"""

    def __init__(self, text=''):
        """Constructor.

        Args:
            text: string, The text of the line.
        """

        self.text = text
        self.table_name = ''
        return

    def parse(self):
        """Parse the text of a create line and determine its properties.

        Raises:
            ValueError if the create line text is no parsable.

        """

        if not self.text:
            return
        create_re = \
            re.compile(r"""
            CREATE\sTABLE\s+        # CREATE TABLE
            [`]?                    # optional `
            ([a-zA-Z][\w\s#\-]+)    # table name
            [`]?                    # optional `
            \s+\(                   # whitespace and opening parenthesis
            $                       # end of line anchor
            """, re.VERBOSE)
        create_match = create_re.match(self.text)
        if not create_match or len(create_match.groups()) < 1:
            raise ValueError('Create line is not parsable: {text}'.format(
                text=self.text))
        self.table_name = create_match.group(1).strip()
        return


class MySQLColumn(object):

    """Class representing a MySQL table column"""

    def __init__(
        self,
        name='',
        data_type='',
        length=None,
        decimals=None,
        attributes=None,
        table=None,
        referenced_table=None,
        referenced_column=None,
        descriptor_column=None,
        ):
        """Constructor.

        Args:
            name: string, the name of the column
            data_type: string, the data type of the column
            length: integer, length of data type
            decimals: integer, number of decimals in data type
            attributes: list, a list of column attributes,
                Eg ['AUTO_INCREMENT', 'NOT NULL'
            table: MySQLTable object instance, object representing the table
                the column belongs to.
            referenced_table: MySQLTable object instance, object representing
                the table the column references
            referenced_column: MySQLColumn object instance, object
                representing the column this column references
            descriptor_column: MySQLColumn object instance, object
                representing the column in the referenced table containing the
                desciptor of the field and used in drop down lists and printing
                the column.
        """

        self.name = name
        self.data_type = data_type
        self.length = length
        self.decimals = decimals
        self.attributes = []
        if attributes:
            self.attributes = attributes
        self.table = table
        self.referenced_table = referenced_table
        self.referenced_column = referenced_column
        self.descriptor_column = descriptor_column
        return

    def documentation(self, name_width=20, type_width=20):
        """Return text documenting the column

        Args:
            name_width: integer, width of name column
            type_width: integer, width of type column

        Return:
            string, Text documenting column.
        """

        # pylint: disable=W0511
        # FIXME is intentional

        fmt = '%%-%ss %%-%ss # FIXME' % (name_width, type_width)
        args = [self.name, self.data_type]
        if self.referenced_table is not None:
            fmt = fmt + ' References %s.%s'
            args.append(self.referenced_table.name)
            args.append(self.referenced_column.name)
        return fmt % tuple(args)

    def requires_statement(self):
        """Return a string representing a requires statement

        Example: "db.tbl_a.tbl_b_id.requires = \
                    IS_IN_DB(db, db.tbl_b.id,'%(b_name)s')"
            where the object column is in "table_a" and references the "id"
            column in "table_b" and can be described by the column "b_name" in
            "table_b".

        Returns:
            String, requires statement.

        """

        return """db.%s.%s.requires = IS_IN_DB(db, db.%s.%s,'%%(%s)s')""" \
            % (self.table.name, self.name, self.referenced_table.name,
               self.referenced_column.name, self.descriptor_column.name)

    def set_descriptor_column(self):
        """Set the descriptor column property.

        The method uses fuzzy logic to determine the descriptor column. These
        conditions are checked in order on all the columns of the referenced
        table. The first column to match is used.
        * column with name "name"
        * column with name "last_name"
        * column with name "title"
        * column with name "*_name"
        * first column of table whose name does not match "id" or "*_id"
        * the referenced_column itself

        """

        if not self.referenced_table:
            if not self.referenced_column:
                return
            else:
                self.descriptor_column = self.referenced_column
                return

        regexes = [re.compile(r'name'), re.compile(r'last_name'),
                   re.compile(r'title'), re.compile(r'.+_name')]

        for regex in regexes:
            for column in self.referenced_table.columns:
                if regex.match(column.name):
                    self.descriptor_column = column
                    return

        id_re = re.compile(r'(?:.+_)?id$')
        for column in self.referenced_table.columns:
            if id_re.match(column.name):
                continue
            self.descriptor_column = column
            return

        self.descriptor_column = self.referenced_column
        return

    def set_referenced_column(self):
        """Set the referenced_column property.

        The method attempts to determine the referenced column from the column
        name.
        * if the column name is of the format "*_column", the referenced column
          is "column"
        * the first column named 'id'
        * the first column not named 'id'

        Typically the column name is like "my_table_id" and the referenced
        column is "id".

        The referenced column must be a column of the referenced table.
        """

        if not self.referenced_table:
            return

        col_re = re.compile(r'^.+_([^_]+)$')
        col_match = col_re.match(self.name)
        if col_match and col_match.group(1) != None:
            for column in self.referenced_table.columns:
                if column.name == col_match.group(1):
                    self.referenced_column = column
                    return
        for column in self.referenced_table.columns:
            if column.name == 'id':
                self.referenced_column = column
                return
        for column in self.referenced_table.columns:
            if column.name != 'id':
                self.referenced_column = column
                return
        return

    def set_referenced_table(self, tables=None):
        """Set the referenced_table property.

        The method attempts to determine the referenced table from the column
        name.
        * if the column name is of the format "*_id", the referenced table
          is one with a name matching "*"

        Typically the column name is like "my_table_id" and the referenced
        table is "my_table".

        Args:
            tables: list, List of MySQLTable objects.
        """

        # If no table list is provided or list is empty there is no possible
        # table that can be referenced. Exit.

        if not tables:
            return

        # Extract the table name from the column name.

        table_re = re.compile(r'(.*)_id')
        table_match = table_re.match(self.name)
        if not table_match:
            return
        table_name = table_match.group(1)

        # Find the table in the provided list

        for table in tables:
            if table.name == table_name:
                self.referenced_table = table
        return


class MySQLTable(object):

    """Class representing a MySQL table"""

    def __init__(self, name):
        """Constructor.

        Args:
            name: string, The name of the table.
        """

        self.name = name
        self.columns = []
        return

    def create_statement(self, drop=False):
        """Construct a create table statement using the table columns.

        Args:
            drop: If True, prepend DROP TABLE IF EXIST statement.

        Returns:
            String: string representing create statement.
        """
        lines = []
        if drop:
            lines.append('DROP TABLE IF EXISTS `{name}`;'.format(
                name=self.name))

        lines.append('CREATE TABLE `{name}` ('.format(name=self.name))
        for column in self.columns:
            length = '({len})'.format(len=column.length) \
                    if column.length else ''
            attributes = ' ' + ' '.join(column.attributes) \
                    if len(column.attributes) > 0 else ''
            lines.append('  `{name}` {type}{len}{attr},'.format(
                name=column.name, type=column.data_type, len=length,
                attr=attributes))

        lines.append('  PRIMARY KEY (`id`)')
        lines.append(') ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;')
        return "\n".join(lines)

    def documentation(self):
        """Return text documenting the table

        Example:
            \"""
            db_database

            ms_access_name      varchar     Name in MS Access.
            mysql_name          varchar     Name in MySQL.
            creation_date       datetime    Record creation timestamp.
            modified_date       datetime    Record last modified timestamp.
            \"""

        Return:
            string, Text documenting table.
        """

        # Set the column widths based on the length of the values in those
        # columns.

        lines = []

        min_width = 10
        name_width = min_width
        type_width = min_width
        if self.columns:
            name_width = max([max(min_width, len(x.name)) for x in
                             self.columns]) + 1
            type_width = max([max(min_width, len(x.data_type)) for x in
                             self.columns]) + 1

        lines.append(r'%s' % self.name)
        lines.append('')
        for column in self.columns:
            if column.name != 'id':
                lines.append(column.documentation(name_width=name_width,
                             type_width=type_width))
        return '\n'.join(lines)

    def insert_statement(self, data, lock=False):
        """Construct a create table statement using the table columns.

        Args:
            data: list of tuples, data to be inserted.
            lock: If True, includes LOCK TABLE and UNLOCK TABLE statements

        Returns:
            String: string representing insert statement.
        """
        lines = []
        if lock:
            lines.append('LOCK TABLE `{name}` WRITE;'.format(
                name=self.name))
        lines.append('INSERT INTO `{name}` VALUES'.format(
                name=self.name))
        none_re = re.compile(r'([(,])None([, ])')
        line = ",\n".join([str(x) for x in data])
        # Replace None with NULL
        line = re.sub(r'([(,])None([, ])',
                lambda match: match.group(1) + 'NULL' + match.group(2), line)
        lines.append(line)
        lines.append(';')
        if lock:
            lines.append('UNLOCK TABLES;')
        return "\n".join(lines)


class SchemaFile(object):

    """Class representing a MySQL schema file"""

    def __init__(self, file_object=None):
        """Constructor.

        Args:
            file: file-like object, the file containing schema data.
        """

        self.file_object = file_object
        self.lines = []
        return

    def filter(self, types):
        """Filter lines from the schema lines that match the types provided.

        Args:
            types: list, List of schema line types, eg ['create', 'column']

        """

        lines = []
        for line in self.lines:
            if line.type in types:
                lines.append(line)
        return lines

    def parse(self):
        """Parse the lines of a schema file."""

        for line in self.file_object.readlines():
            schema_line = SchemaLine(text=line.rstrip())
            schema_line.type = schema_line.get_type()
            self.lines.append(schema_line)
        return


class SchemaLine(object):

    """Class representing a line of a MySQL schema file"""

    def __init__(self, text=''):
        """Constructor.

        Args:
            text: string, The text of the line.
        """

        self.text = text
        self.type = None
        return

    def get_type(self):
        """Determine the line type

        Returns:
            string, type indicator
        """

        types = [
            {'id': 'drop', 're': re.compile(r'^DROP .*')},
            {'id': 'create', 're': re.compile(r'^CREATE TABLE .*')},
            {'id': 'create_close', 're': re.compile(r'^\) ENGINE=.*;$')},
            {'id': 'column', 're':
                re.compile(r'^\s*`[a-zA-Z][\w#\-]+`\s+\w+')},
            {'id': 'comment', 're': re.compile(r'^--')},
            {'id': 'blank', 're': re.compile(r'^\s*$')},
            ]

        for line_type in types:
            if line_type['re'].match(self.text):
                return line_type['id']
        return 'other'
