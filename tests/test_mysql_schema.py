#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/mysql_schema.py

"""

from applications.shared.modules.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.mysql_schema import ColumnLine, \
    CreateLine, MySQLColumn, MySQLTable, SchemaFile, SchemaLine
import os
import sys
import unittest

# R0904: Too many public methods
# pylint: disable=C0111,R0904


class TestColumnLine(unittest.TestCase):

    def test____init__(self):
        column_line = ColumnLine()
        self.assertTrue(column_line)  # Creates object
        return

    def test__parse(self):
        tests = [
            {
                'label': 'empty string',
                'text': '',
                'name': '',
                'type': '',
                'attributes': [],
                },
            {
                'label': 'basic typical',
                'text': '`my_column` text,',
                'name': 'my_column',
                'type': 'text',
                'attributes': [],
                },
            {
                'label': 'basic without ticks',
                'text': 'my_column text,',
                'name': 'my_column',
                'type': 'text',
                'attributes': [],
                },
            {
                'label': 'basic without comma',
                'text': '`my_column` text',
                'name': 'my_column',
                'type': 'text',
                'attributes': [],
                },
            {
                'label': 'basic indented',
                'text': '    `my_column` text,',
                'name': 'my_column',
                'type': 'text',
                'attributes': [],
                },
            {
                'label': 'length',
                'text': '`my_column` varchar(255),',
                'name': 'my_column',
                'type': 'varchar',
                'length': 255,
                'attributes': [],
                },
            {
                'label': 'decimals',
                'text': '`my_decimals` decimal(18,2),',
                'name': 'my_decimals',
                'type': 'decimal',
                'length': 18,
                'decimals': 2,
                'attributes': [],
                },
            {
                'label': 'AUTO_INCREMENT',
                'text': '`my_not_null` integer AUTO_INCREMENT,',
                'name': 'my_not_null',
                'type': 'integer',
                'attributes': ['AUTO_INCREMENT'],
                },
            {
                'label': 'COMMENT',
                'text': \
                    """`my_not_null` integer COMMENT 'this is my comment',""",
                'name': 'my_not_null',
                'type': 'integer',
                'attributes': ['COMMENT'],
                'comment': 'this is my comment',
                },
            {
                'label': 'DEFAULT',
                'text': """`my_not_null` integer DEFAULT '0',""",
                'name': 'my_not_null',
                'type': 'integer',
                'attributes': ['DEFAULT'],
                'default': '0',
                },
            {
                'label': 'NOT NULL',
                'text': '`my_not_null` integer NOT NULL,',
                'name': 'my_not_null',
                'type': 'integer',
                'attributes': ['NOT NULL'],
                },
            {
                'label': 'NULL',
                'text': '`my_not_null` integer NULL,',
                'name': 'my_not_null',
                'type': 'integer',
                'attributes': ['NULL'],
                },
            {
                'label': 'PRIMARY KEY',
                'text': '`my_not_null` integer PRIMARY KEY,',
                'name': 'my_not_null',
                'type': 'integer',
                'attributes': ['PRIMARY KEY'],
                },
            {
                'label': 'PRIMARY',
                'text': '`my_not_null` integer PRIMARY,',
                'name': 'my_not_null',
                'type': 'integer',
                'attributes': ['PRIMARY'],
                },
            {
                'label': 'UNIQUE KEY',
                'text': '`my_not_null` integer UNIQUE KEY,',
                'name': 'my_not_null',
                'type': 'integer',
                'attributes': ['UNIQUE KEY'],
                },
            {
                'label': 'UNIQUE',
                'text': '`my_not_null` integer UNIQUE,',
                'name': 'my_not_null',
                'type': 'integer',
                'attributes': ['UNIQUE'],
                },
            {
                'label': 'typical id',
                'text': '`id` int(11) NOT NULL AUTO_INCREMENT,',
                'name': 'id',
                'type': 'int',
                'length': 11,
                'attributes': ['AUTO_INCREMENT', 'NOT NULL'],
                },
            {
                'label': 'unsigned and zerofill',
                'text': '`my_unsigned` integer UNSIGNED ZEROFILL,',
                'name': 'my_unsigned',
                'type': 'integer',
                'attributes': [],
                },
            ]

        for test in tests:
            cl = ColumnLine(text=test['text'])
            try:
                cl.parse()
            except ValueError, e:
                print '%s: %s' % (test['label'], e)
                continue

            self.assertEqual(cl.name, test['name'])
            self.assertEqual(cl.type, test['type'])
            if 'length' in test:
                self.assertEqual(cl.length, test['length'])
            else:
                self.assertEqual(cl.length, None)
            if 'decimals' in test:
                self.assertEqual(cl.decimals, test['decimals'])
            else:
                self.assertEqual(cl.decimals, None)
            self.assertEqual(cl.attributes, test['attributes'])
            if 'comment' in test:
                self.assertEqual(cl.comment, test['comment'])
            else:
                self.assertEqual(cl.comment, None)
            if 'default' in test:
                self.assertEqual(cl.default, test['default'])
            else:
                self.assertEqual(cl.default, None)

        cl = ColumnLine(text='n@n (parsable colu%mn line')
        self.assertRaises(ValueError, cl.parse)
        return

    def test__filter_attributes(self):
        column_line = ColumnLine()
        column_line.attributes = []
        column_line.filter_attributes('A', 'B')
        self.assertEqual(column_line.attributes, [])

        column_line.attributes = ['A', 'B']
        column_line.filter_attributes('A', 'B')
        self.assertEqual(column_line.attributes, ['A'])
        return


class TestCreateLine(unittest.TestCase):

    def test____init__(self):
        create_line = CreateLine()
        self.assertTrue(create_line)  # Creates object
        return

    def test__parse(self):
        tests = [
                {
                    'label': 'empty string',
                    'text': '',
                    'table_name': ''
                },
                {
                    'label': 'basic typical',
                    'text': 'CREATE TABLE `my_table` (',
                    'table_name': 'my_table'
                }]

        for test in tests:
            cl = CreateLine(text=test['text'])
            try:
                cl.parse()
            except ValueError, e:
                print '%s: %s' % (test['label'], e)
                continue

            self.assertEqual(cl.table_name, test['table_name'])

        cl = CreateLine(text='n@n (parsable crea%e line')
        self.assertRaises(ValueError, cl.parse)
        return


class TestMySQLColumn(unittest.TestCase):

    TBL_NAME = 'my_table_1'
    TBL_NAME_2 = 'my_table_2'
    TBL_NAME_3 = 'my_table_3'
    COL_NAME = 'my_column_1'
    COL_NAME_2 = 'my_column_2'
    REF_TABLE = 'some_table'
    REF_COL = 'some_column'
    DESC_COL = 'name_column'

    def test____init__(self):
        mysql_column = MySQLColumn(name='__test_mysql_column__')
        self.assertTrue(mysql_column)  # Creates object
        return

    def test__documentation(self):
        # W0511 Used when a warning note as FIXME or XXX is detected.
        # pylint: disable=W0511

        tests = [
            {
                'name': 'my_column_name',
                'type': 'text',
                'expect': 'my_column_name       text                 # FIXME'
            },
            {
                #         '1234567890123456789012345678901234567890'
                'name': 'my_column_name',
                'type': 'text',
                'name_width': 16,
                'type_width': 6,
                'expect': 'my_column_name   text   # FIXME',
            },
            {
                #         '1234567890123456789012345678901234567890'
                'name': 'my_column_name',
                'type': 'integer(11)',
                'name_width': 16,
                'type_width': 11,
                'ref_table': 'city',
                'ref_column': 'id',
                'expect': \
                    'my_column_name   integer(11) # FIXME References city.id',
            }]

        for t in tests:
            mysql_column = MySQLColumn(name=t['name'],
                    data_type=t['type'])
            kwargs = {}
            for w in ['name_width', 'type_width']:
                if w in t:
                    kwargs[w] = t[w]
            if 'ref_table' in t:
                ref_table = MySQLTable(name=t['ref_table'])
                ref_column = MySQLColumn(name=t['ref_column'])
                mysql_column.referenced_table = ref_table
                mysql_column.referenced_column = ref_column
            self.assertEqual(mysql_column.documentation(**kwargs),
                             t['expect'])
        return

    def test__requires_statement(self):
        table = MySQLTable(name=self.TBL_NAME)
        ref_table = MySQLTable(name=self.REF_TABLE)
        ref_column = MySQLColumn(name=self.REF_COL)
        desc_column = MySQLColumn(name=self.DESC_COL)
        mysql_column = MySQLColumn(name=self.COL_NAME, table=table,
                                   referenced_table=ref_table,
                                   referenced_column=ref_column,
                                   descriptor_column=desc_column)
        fmt = ' '.join(['db.{tbl}.{col}.requires =',
                       """IS_IN_DB(db, db.{ref_tbl}.{ref_col},'%({desc})s')"""
                       ])
        stmt = mysql_column.requires_statement()
        self.assertEqual(stmt, fmt.format(tbl=self.TBL_NAME,
                         col=self.COL_NAME, ref_tbl=self.REF_TABLE,
                         ref_col=self.REF_COL, desc=self.DESC_COL))

        return

    def test__set_descriptor_column(self):
        table = MySQLTable(name=self.TBL_NAME)
        mysql_column = MySQLColumn(name=self.COL_NAME, table=table)

        mysql_column.set_descriptor_column()
        # no referenced column, descriptor column is None.
        self.assertEqual(mysql_column.descriptor_column, None)

        table_2 = MySQLTable(name='employee')
        mysql_column.referenced_table = table_2

        t2_col_1 = MySQLColumn(name='id', table=table_2)
        t2_col_2 = MySQLColumn(name='group_id', table=table_2)
        table_2.columns.append(t2_col_1)
        table_2.columns.append(t2_col_2)

        mysql_column.referenced_column = t2_col_1
        mysql_column.set_descriptor_column()
        # no referenced table, uses referenced column
        self.assertEqual(mysql_column.descriptor_column, t2_col_1)

        mysql_column.referenced_table = table_2
        mysql_column.referenced_column = t2_col_2
        mysql_column.set_descriptor_column()
        # referenced, no non-id column, uses referenced column
        self.assertEqual(mysql_column.descriptor_column, t2_col_2)

        # For each name in the names list, a column is added to the referenced
        # table with that name. Each subsequent name is higher in the priority
        # for matching the descriptor column, so its column should become the
        # descriptor column.

        names = ['identity', 'given_name', 'title', 'last_name', 'name']
        for name in names:
            new_column = MySQLColumn(name=name, table=table_2)
            table_2.columns.append(new_column)
            mysql_column.set_descriptor_column()
            # referenced, uses new column
            self.assertEqual(mysql_column.descriptor_column, new_column)
        return

    def test__set_referenced_column(self):

        # Test with ????_id style column

        table = MySQLTable(name='session')
        mysql_column = MySQLColumn(name='employee_id', table=table)
        # Control - referenced column initially None
        self.assertEqual(mysql_column.referenced_column, None)

        mysql_column.set_referenced_column()
        # no referenced table, referenced column is None.
        self.assertEqual(mysql_column.referenced_column, None)
        table_2 = MySQLTable(name='employee')
        mysql_column.referenced_table = table_2

        mysql_column.set_referenced_column()
        # referenced table has no columns, referenced column is None.
        self.assertEqual(mysql_column.referenced_column, None)

        t2_col_1 = MySQLColumn(name='id', table=table_2)
        t2_col_2 = MySQLColumn(name='name', table=table_2)
        t2_col_3 = MySQLColumn(name='group_id', table=table_2)
        t2_col_4 = MySQLColumn(name='status_id', table=table_2)
        table_2.columns.append(t2_col_1)
        table_2.columns.append(t2_col_2)
        table_2.columns.append(t2_col_3)
        table_2.columns.append(t2_col_4)

        mysql_column.set_referenced_column()
        # match, referenced column is expected
        self.assertEqual(mysql_column.referenced_column, t2_col_1)

        # Test with non ????_id style column

        table = MySQLTable(name='session')
        mysql_column.name = 'service_username'

        table_3 = MySQLTable(name='service')
        mysql_column.referenced_table = table_3
        mysql_column.referenced_column = None
        # Control - referenced column initially None
        self.assertEqual(mysql_column.referenced_column, None)

        t3_col_1 = MySQLColumn(name='name', table=table_3)
        t3_col_2 = MySQLColumn(name='group_id', table=table_3)
        t3_col_3 = MySQLColumn(name='status_id', table=table_3)
        table_3.columns.append(t3_col_1)
        table_3.columns.append(t3_col_2)
        table_3.columns.append(t3_col_3)

        mysql_column.set_referenced_column()
        # No match, no id, uses first column
        self.assertEqual(mysql_column.referenced_column, t3_col_1)

        mysql_column.referenced_column = None
        # Control - referenced column initially None
        self.assertEqual(mysql_column.referenced_column, None)
        t3_col_4 = MySQLColumn(name='username', table=table_3)
        table_3.columns.append(t3_col_4)
        mysql_column.set_referenced_column()
        # Non-???_id column match, uses expected
        self.assertEqual(mysql_column.referenced_column, t3_col_4)

        mysql_column.referenced_column = None
        # Control - referenced column initially None
        self.assertEqual(mysql_column.referenced_column, None)
        t3_col_4.name = 'id'
        mysql_column.set_referenced_column()
        # No match, uses id field
        self.assertEqual(mysql_column.referenced_column, t3_col_4)
        return

    def test__set_referenced_table(self):
        table = MySQLTable(name='session')
        table.columns.append(MySQLColumn(name='id', table=table))
        table.columns.append(MySQLColumn(name='name', table=table))
        table.columns.append(MySQLColumn(name='group_id', table=table))
        table.columns.append(MySQLColumn(name='status_id', table=table))
        mysql_column = MySQLColumn(name=self.COL_NAME, table=table)
        # Control - referenced table initially None
        self.assertEqual(mysql_column.referenced_table, None)

        tables = []
        mysql_column.set_referenced_table(tables=tables)
        # Table list is empty, referenced table still None
        self.assertEqual(mysql_column.referenced_table, None)

        table_2 = MySQLTable(name='employee')
        table_2.columns.append(MySQLColumn(name='id', table=table_2))
        table_2.columns.append(MySQLColumn(name='name', table=table_2))
        table_2.columns.append(MySQLColumn(name='group_id',
                               table=table_2))
        table_2.columns.append(MySQLColumn(name='status_id',
                               table=table_2))

        table_3 = MySQLTable(name='location')
        table_3.columns.append(MySQLColumn(name='id', table=table_3))
        table_3.columns.append(MySQLColumn(name='name', table=table_3))
        table_3.columns.append(MySQLColumn(name='group_id',
                               table=table_3))
        table_3.columns.append(MySQLColumn(name='status_id',
                               table=table_3))

        tables.append(table)
        tables.append(table_2)
        tables.append(table_3)

        mysql_column.name = 'oneword'
        mysql_column.set_referenced_table(tables=tables)
        # One word column doesn't reference table
        self.assertEqual(mysql_column.referenced_table, None)

        mysql_column.name = 'login_id'
        mysql_column.set_referenced_table(tables=tables)
        # Reference like name doesn't match any references tables
        self.assertEqual(mysql_column.referenced_table, None)

        mysql_column.name = 'location_id'
        mysql_column.set_referenced_table(tables=tables)
        # Match sets expected.
        self.assertEqual(mysql_column.referenced_table, table_3)

        mysql_column.name = 'session_id'
        mysql_column.set_referenced_table(tables=tables)
        # Matches it own table, sets expected.
        self.assertEqual(mysql_column.referenced_table, table)
        return


class TestMySQLTable(unittest.TestCase):

    def test____init__(self):
        table = MySQLTable(name='__test_mysql_table__')
        self.assertTrue(table)  # Creates object
        return

    def test__create_statement(self):
        table = MySQLTable(name='my_table')
        table.columns.append(MySQLColumn(name='id', data_type='integer',
            length=11, attributes=['NOT NULL', 'AUTO_INCREMENT'], table=table))
        table.columns.append(MySQLColumn(name='name', data_type='varchar',
            length=255, attributes=['DEFAULT NULL'], table=table))
        table.columns.append(MySQLColumn(name='description', data_type='blob',
            table=table))
        table.columns.append(MySQLColumn(name='group_id', data_type='integer',
            length=11, table=table))

        expect = """\
CREATE TABLE `my_table` (
  `id` integer(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `description` blob,
  `group_id` integer(11),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;"""

        expect_drop = """\
DROP TABLE IF EXISTS `my_table`;
CREATE TABLE `my_table` (
  `id` integer(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `description` blob,
  `group_id` integer(11),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;"""
        self.assertEqual(table.create_statement(), expect)
        self.assertEqual(table.create_statement(drop=True), expect_drop)

    def test__documentation(self):
        # W0511 Used when a warning note as FIXME or XXX is detected.
        # pylint: disable=W0511

        table = MySQLTable(name='my_table')
        expect = """my_table
"""
        self.assertEqual(table.documentation(), expect)

        table.columns.append(MySQLColumn(name='id', data_type='integer',
            table=table))
        table.columns.append(MySQLColumn(name='name', data_type='varchar(255)',
            table=table))
        table.columns.append(MySQLColumn(name='description', data_type='blob',
            table=table))
        table.columns.append(MySQLColumn(name='group_id', data_type='integer',
            table=table))
        expect = \
            """my_table

name         varchar(255)  # FIXME
description  blob          # FIXME
group_id     integer       # FIXME"""

# 234567890123456789012345678901234567890

        self.assertEqual(table.documentation(), expect)
        return

    def test__insert_statement(self):
        table = MySQLTable(name='my_table')
        data = [
                (None, 1, 'a'),
                (None, 2, 'b'),
                (None, 3, 'c'),
                ]

        expect = """\
INSERT INTO `my_table` VALUES
(NULL, 1, 'a'),
(NULL, 2, 'b'),
(NULL, 3, 'c')
;"""

        expect_lock = """\
LOCK TABLE `my_table` WRITE;
INSERT INTO `my_table` VALUES
(NULL, 1, 'a'),
(NULL, 2, 'b'),
(NULL, 3, 'c')
;
UNLOCK TABLES;"""

        self.assertEqual(table.insert_statement(data), expect)
        self.assertEqual(table.insert_statement(data, lock=True), expect_lock)
        return


class TestSchemaFile(unittest.TestCase):

    def _config_file_from_text(self, filename, text):

        # R0201: *Method could be a function*
        # pylint: disable=R0201

        f = open(filename, 'w')
        f.write(text)
        f.close()
        return

    def test____init__(self):
        schema_file = SchemaFile()
        self.assertTrue(schema_file)  # Creates object
        return

    def test__filter(self):
        schema_file = SchemaFile()
        self.assertEqual(schema_file.lines, [])  # Control - no lines
        # filter returns expected
        self.assertEqual(schema_file.filter(['a', 'c']), [])

        schema_line1 = SchemaLine()
        schema_line2 = SchemaLine()
        schema_line3 = SchemaLine()
        schema_line1.type = 'a'
        schema_line2.type = 'b'
        schema_line3.type = 'c'
        schema_file.lines.append(schema_line1)
        schema_file.lines.append(schema_line2)
        schema_file.lines.append(schema_line3)
        self.assertEqual(schema_file.filter(['a', 'c']), [schema_line1,
                         schema_line3])  # filter returns expected
        return

    def test__parse(self):
        tests = [
                {
                    'label': 'empty file',
                    'expect': 0,
                    'text': ''
                },
                {
                    'label': 'basic file',
                    'expect': 3,
                    'text': """CREATE TABLE my_table (
    id integer,
)
"""},
                 {
                    'label': 'typical file',
                    'expect': 55,
                    'text': """
-- MySQL dump 10.13  Distrib 5.1.47, for pc-linux-gnu (i686)
--
-- Host: localhost    Database: accounting
-- ------------------------------------------------------
-- Server version    5.1.47-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `company`
--

DROP TABLE IF EXISTS `company`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `company` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text COLLATE latin1_general_ci,
  `bank_account_id` int(11) DEFAULT '0',
  `hst_account_id` int(11) DEFAULT '0',
  `pst_account_id` int(11) DEFAULT '0',
  `transfer_account_id` int(11) DEFAULT '0',
  `unsorted_account_id` int(11) DEFAULT '0',
  `earnings_account_id` int(11) DEFAULT '0',
  `opening_account_id` int(11) DEFAULT '0',
  `dfa_account_id` int(11) DEFAULT '0',
  `colour` text COLLATE latin1_general_ci,
  `fiscal_month` int(11) DEFAULT '0',
  `freeze_date` date DEFAULT NULL,
  `creation_date` datetime DEFAULT NULL,
  `modified_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=305 DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2010-07-01 11:40:10
"""}]

        f_text = '/tmp/test_mysql_schema.txt'
        for t in tests:
            self._config_file_from_text(f_text, t['text'])
            f = open(f_text)
            schema_file = SchemaFile(file_object=f)
            schema_file.parse()
            f.close()
            self.assertEqual(len(schema_file.lines), t['expect'])
        os.unlink(f_text)
        return


class TestSchemaLine(unittest.TestCase):

    def test____init__(self):
        schema_line = SchemaLine()
        self.assertTrue(schema_line)  # Creates object
        return

    def test__get_type(self):
        tests = [
            {
                'label': 'empty string',
                'text': '',
                'expect': 'blank'},
            {
                'label': 'drop',
                'text': 'DROP TABLE IF EXISTS `my_table`',
                'expect': 'drop'},
            {
                'label': 'create',
                'text': 'CREATE TABLE `my_table` (',
                'expect': 'create'},
            {
                'label': 'create close',
                'text': \
                ') ENGINE=InnoDB AUTO_INCREMENT=305 DEFAULT CHARSET=latin1;',
                'expect': 'create_close'},
            {
                'label': 'column',
                'text': '`id` int(11) NOT NULL AUTO_INCREMENT,',
                'expect': 'column'
            },
            {
                'label': 'comment',
                'text': '-- Table structure for table `company`',
                'expect': 'comment'
            },
            {
                'label': 'other',
                'text': '/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;',
                'expect': 'other'
            },
            ]

        for test in tests:
            sl = SchemaLine(text=test['text'])
            self.assertEqual(sl.get_type(), test['expect'])
        return


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
