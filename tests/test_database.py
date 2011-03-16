#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/db/table.py

"""

# The accounting database is use for testing
from applications.shared.modules.local.test_runner import LocalTestSuite, \
    ModuleTestSuite
from gluon.validators import IS_DATE, IS_DATETIME, IS_INT_IN_RANGE, \
    IS_IN_DB, IS_IN_SET, IS_LENGTH, IS_NULL_OR
from applications.shared.modules.database import Collection, DbIOError, \
    DbObject, rows_to_objects
import cStringIO
import copy
import datetime
import decimal
import re
import sys
import time
import unittest

# C0111: *Missing docstring*
# R0904: *Too many public methods (%s/%s)*
# pylint: disable=C0111,R0904

from gluon.shell import env

# The test script requires an existing database to work with. The shared
# database should have tables account and company. The models/db.py should
# define the tables.

APP_ENV = env(__file__.split('/')[-3], import_models=True)
DBH = APP_ENV['db']

D = decimal.Decimal

TEST_DROP_QUERY = """
DROP TABLE IF EXISTS test;
"""

TEST_CREATE_QUERY = \
    """
CREATE TABLE test (
  id int(11) NOT NULL AUTO_INCREMENT,
  company_id int(11) DEFAULT '0',
  number int(11) DEFAULT '0',
  name text COLLATE latin1_general_ci,
  amount decimal(18,2) DEFAULT '0.00',
  start_date date DEFAULT NULL,
  status char(1) DEFAULT 'a',
  creation_date datetime DEFAULT NULL,
  modified_date datetime DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1
"""

TEST_INSERT_COMPANY = """INSERT into company (name) VALUES ('%s');""" \
    % '__test__'
TEST_DELETE_COMPANY = """DELETE FROM company WHERE name = '%s';   """ \
    % '__test__'

# Test data
COMPANY_ID = None
COMPANY_ID_2 = 222
NUMBER = 1000
NUMBER_2 = 2000
NAME = '__test_table_name__'
NAME_2 = '__test_table_name_2__'
AMOUNT = D('123.45')
AMOUNT_2 = D('987.65')
START_DATE = datetime.date(2010, 1, 11)
START_DATE_2 = datetime.date(2010, 2, 22)
STATUS = 'a'
STATUS_2 = 'd'
LIST = ['abc', 'def', 'ghi']


# The Account class is adapted from the accounting class of the same name.
class Account(DbObject):

    """Class representing an account record.

    """

    def __init__(self, tbl_, **kwargs):
        super(Account, self).__init__(tbl_, **kwargs)
        return


# The Company class is adapted from the accounting class of the same name.
class Company(DbObject):

    """Class representing an accounting company record.

    """

    def __init__(self, tbl_, **kwargs):
        super(Company, self).__init__(tbl_, **kwargs)
        return


def suite_setup():

    # Delete test table if it wasn't removed properly

    rows = DBH.executesql("""SHOW TABLES LIKE 'test';""")
    if len(rows) > 0:
        DBH.executesql(TEST_DROP_QUERY)
        DBH.commit()

    # Create a temporary table for testing

    DBH.executesql(TEST_CREATE_QUERY)
    DBH.commit()

    DBH.define_table(
        'test',
        DBH.Field('company_id', 'integer'),
        DBH.Field('number', 'integer', requires=IS_INT_IN_RANGE(1000,
                  10000)),
        DBH.Field('name', requires=IS_NULL_OR(IS_LENGTH(512))),
        DBH.Field('amount', 'decimal(10,2)', default=D('0.00')),
        DBH.Field('start_date', 'date',
                  requires=IS_NULL_OR(IS_DATE(format='%Y-%m-%d'))),
        DBH.Field('status', requires=IS_IN_SET(['a', 'd'])),
        DBH.Field('creation_date', 'datetime',
                  requires=IS_NULL_OR(IS_DATETIME(format='%Y-%m-%d %H:%M:%S'
                  ))),
        DBH.Field('modified_date', 'datetime',
                  requires=IS_NULL_OR(IS_DATETIME(format='%Y-%m-%d %H:%M:%S'
                  ))),
        migrate=False,
        )

    DBH.test.company_id.requires = IS_IN_DB(DBH, DBH.company.id,
            '%(name)s')
    return


def suite_teardown():

    # Remove temporary table

    DBH.executesql(TEST_DROP_QUERY)
    DBH.executesql(TEST_DELETE_COMPANY)
    DBH.commit()
    return


# The db.test table has to be created in order for it to be used in the Test
# class definition.

suite_setup()


class TestCollection(unittest.TestCase):

    i_re = re.compile(r'^\d+$')

    def setUp(self):
        # C0103: *Invalid name "%s" (should match %s)*
        # W0603: *Using the global statement*

        # pylint: disable=C0103,W0603
        DBH.executesql(TEST_DELETE_COMPANY)
        DBH.executesql(TEST_INSERT_COMPANY)
        DBH.commit()
        global COMPANY_ID
        COMPANY_ID = None

        # Get the id of the test company

        rows = \
            DBH.executesql("""
            SELECT id FROM company
            WHERE name = '%s'
            """
                           % '__test__')
        if len(rows) <= 0:
            return
        row = rows[0]
        if len(row) <= 0:
            return
        COMPANY_ID = row[0]

    def tearDown(self):
        # C0103: *Invalid name "%s" (should match %s)*
        # pylint: disable=C0103
        DBH.executesql(TEST_DELETE_COMPANY)
        DBH.commit()

    def _obj(self, number=0):
        if number == 1:
            t = DbObject(DBH.test)
            t.company_id = COMPANY_ID
            t.number = NUMBER
            t.name = NAME
            t.amount = AMOUNT
            t.start_date = START_DATE
            t.status = STATUS
            self.assertTrue(t.add())  # Add test object
            return t
        if number == 2:
            t2 = DbObject(DBH.test)
            t2.company_id = COMPANY_ID
            t2.number = NUMBER_2
            t2.name = NAME_2
            t2.amount = AMOUNT_2
            t2.start_date = START_DATE_2
            t2.status = STATUS_2
            self.assertTrue(t2.add())  # Add test object 2
            return t2

    def test____init__(self):
        c = Collection(DBH.test)
        self.assertTrue(isinstance(c, Collection))  # Object created

        # Ensure object has db_ property
        self.assertTrue(hasattr(c, 'db_'))
        self.assertTrue(hasattr(c, 'objects'))  # Object has objects property
        self.assertEqual(len(c.objects), 0)  # Objects property is empty

        c = Collection(DBH.test, objects=LIST)
        self.assertEqual(c.objects, LIST)  # Objects property set properly

    def test____getitem__(self):
        # Able to get specific list item
        self.assertEqual(Collection(DBH.test, objects=LIST)[0], 'abc')
        # Able to get slice
        self.assertEqual(Collection(DBH.test, objects=LIST)[1:3],
                ['def', 'ghi'])
        return

    def test____iter__(self):
        t = self._obj(number=1)
        t2 = self._obj(number=2)
        # Iterator returns list
        self.assertEqual(list(Collection(DBH.test).get(id=t.id)), [t])
        query = DbObject(DBH.test).tbl_.company_id == COMPANY_ID
        for (x, o) in enumerate(Collection(DBH.test).get(query=query)):
            if x == 0:
                self.assertEqual(o, t)  # Iterates through first object
            if x == 1:
                self.assertEqual(o, t2)  # Iterates through second object
            self.assertTrue(x <= 1)  # Count of objects stays in range
        self.assertTrue(t.remove())  # Remove test object
        self.assertTrue(t2.remove())  # Remove test object
        return

    def test____len__(self):
        t = self._obj(number=1)
        c = Collection(DBH.test)
        self.assertEqual(len(c), 0)  # Initially len is zero
        self.assertTrue(c.get(id=t.id))
        self.assertEqual(len(c), 1)  # After get, len is correct
        self.assertTrue(t.remove())  # Remove test object
        return

    def test____nonzero__(self):
        self.assertFalse(Collection(DBH.test))  # Unpopulated object is false.
        # Populated object is true.
        self.assertTrue(Collection(DBH.test, objects=LIST))
        return

    def test____repr__(self):
        # Uninitialized repr() returns empty string
        self.assertTrue(len(repr(Collection(DBH.test))) == 0)
        t = self._obj(number=1)
        self.assertTrue(len(repr(Collection(DBH.test, objects=[t])))
                        > 0)  # Initialized repr() returns non-empty string

        # Return value is tested in export_as_csv

        self.assertTrue(t.remove())  # Remove test object
        return

    def test____str__(self):
        # Uninitialized str() returns empty string
        self.assertTrue(len(str(Collection(DBH.test))) == 0)
        # Initialized str() returns non-empty string
        t = self._obj(number=1)
        self.assertTrue(len(str(Collection(DBH.test, objects=[t]))) > 0)

        # Return value is tested in export_as_csv

        self.assertTrue(t.remove())  # Remove test object
        return

    def test__as_dict(self):
        # Uninitialized returns empty dict
        self.assertEqual(Collection(DBH.test).as_dict(), {})
        t = self._obj(number=1)
        t2 = self._obj(number=2)
        d = Collection(DBH.test, objects=[t, t2]).as_dict()
        self.assertTrue(d)  # With objects, returns dictionary
        self.assertEqual(d[t.id], t)  # Lookup returns expected object
        self.assertEqual(d[t2.id], t2)  # Lookup returns expected object (2)

        self.assertTrue(t.remove())  # Remove test object
        self.assertTrue(t2.remove())  # Remove test object 2
        return

    def test__export_as_csv(self):
        output = cStringIO.StringIO()
        Collection(DBH.test).export_as_csv(out=output)
        # Uninitialized object returns empty string
        self.assertEqual(output.getvalue(), '')
        output.close()

        t = self._obj(number=1)
        t2 = self._obj(number=2)
        output = cStringIO.StringIO()
        o = Collection(DBH.test, objects=[t, t2])
        o.export_as_csv(out=output)

        # String fields are double quoted.

        self.assertEqual("""%s,%s,%s,"%s",%s,"%s","%s","%s","%s"\r
%s,%s,%s,"%s",%s,"%s","%s","%s","%s"\r
"""
                         % (
            t.id,
            COMPANY_ID,
            NUMBER,
            NAME,
            AMOUNT,
            START_DATE,
            STATUS,
            t.creation_date,
            t.modified_date,
            t2.id,
            COMPANY_ID,
            NUMBER_2,
            NAME_2,
            AMOUNT_2,
            START_DATE_2,
            STATUS_2,
            t2.creation_date,
            t2.modified_date,
            ), output.getvalue())
        output.close()

        # With header

        output = cStringIO.StringIO()
        o = Collection(DBH.test, objects=[t])
        o.export_as_csv(out=output, header=1)

        # String fields are double quoted.

        # C0324: *Comma not followed by a space*
        # pylint: disable=C0324

        self.assertEqual("""\"%s","%s","%s","%s","%s","%s","%s","%s","%s"\r
%s,%s,%s,"%s",%s,"%s","%s","%s","%s"\r
"""
                         % (
            'id',
            'company_id',
            'number',
            'name',
            'amount',
            'start_date',
            'status',
            'creation_date',
            'modified_date',
            t.id,
            COMPANY_ID,
            NUMBER,
            NAME,
            AMOUNT,
            START_DATE,
            STATUS,
            t.creation_date,
            t.modified_date,
            ), output.getvalue())
        output.close()

        self.assertTrue(t.remove())  # Remove test object
        self.assertTrue(t2.remove())  # Remove test object 2
        return

    def test__first(self):
        # Uninitialized first is None
        self.assertEqual(Collection(DBH.test).first(), None)
        # Returns correct first
        self.assertEqual(Collection(DBH.test, objects=LIST).first(),
                         'abc')
        return

    def test__get(self):

        # Test with id

        t = self._obj(number=1)
        t2 = self._obj(number=2)
        self.assertTrue(t.id and t2.id and t.id != t2.id)  # Ids are unique
        c = Collection(DBH.test)
        self.assertTrue(c.get(id=t.id))
        self.assertEqual(len(c.objects), 1)  # Sets correct number of objects
        o = c.objects[0]
        self.assertEqual(o.company_id, COMPANY_ID)  # Correct company_id
        self.assertEqual(o.name, NAME)  # Correct name
        self.assertEqual(o, t)  # Object matches original

        self.assertTrue(c.get(id=t2.id))
        self.assertEqual(len(c.objects), 1)  # Sets correct number of objects
        o = c.objects[0]
        self.assertEqual(o.company_id, COMPANY_ID)  # Correct company_id
        self.assertEqual(o.name, NAME_2)  # Correct name
        self.assertEqual(o, t2)  # Object matches original

        # Id set to zero should try to match on zero and return none.
        self.assertFalse(c.get(id=0))
        self.assertEqual(len(c.objects), 0)  # Sets correct number of objects
        # Id set to None is the same as not setting it, returns all.
        self.assertTrue(c.get(id=None))
        self.assertEqual(len(c.objects), 2)  # Sets correct number of objects

        # Test with query

        self.assertTrue(c.get(query=DbObject(DBH.test).tbl_.name
                        == NAME))
        self.assertEqual(len(c.objects), 1)  # Sets correct number of objects
        self.assertEqual(c.objects[0], t)  # Object matches original

        self.assertTrue(c.get(query=DbObject(DBH.test).tbl_.company_id
                        == COMPANY_ID))
        self.assertEqual(len(c.objects), 2)  # Sets correct number of objects
        self.assertEqual(c.objects[0], t)  # Object matches original
        self.assertEqual(c.objects[1], t2)  # Object matches original

        self.assertFalse(c.get(query=DbObject(DBH.test).tbl_.name
                         == '__fake__'))
        self.assertEqual(len(c.objects), 0)  # Returns expected nothing

        # Empty string query should return no objects
        self.assertFalse(c.get(query=''))
        self.assertEqual(len(c.objects), 0)  # Sets correct number of objects
        # Query set to None is the same as not setting it, returns all.
        self.assertTrue(c.get(query=None))
        self.assertEqual(len(c.objects), 2)  # Sets correct number of objects

        # Test with id and query

        self.assertTrue(c.get(id=t2.id,
                        query=DbObject(DBH.test).tbl_.name == NAME))
        self.assertEqual(len(c.objects), 1)  # Sets correct number of objects
        self.assertEqual(c.objects[0], t2)  # Object matches expected

        # Test with neither id and query

        self.assertTrue(c.get())
        self.assertEqual(len(c.objects), 2)  # Sets correct number of objects
        self.assertEqual(c.objects[0], t)  # Object matches expected
        self.assertEqual(c.objects[1], t2)  # Object matches expected
        # Id and query set to None is the same as not setting them, returns
        # all.
        self.assertTrue(c.get(id=None, query=None))
        self.assertEqual(len(c.objects), 2)  # Sets correct number of objects

        # Test with orderby

        # By number reverse
        self.assertTrue(c.get(orderby=~DbObject(DBH.test).tbl_.number))
        self.assertEqual(len(c.objects), 2)  # Sets correct number of objects
        self.assertEqual(c.objects[0], t2)  # Object matches expected
        self.assertEqual(c.objects[1], t)  # Object matches expected

        # Test with limitby
        self.assertTrue(c.get(limitby=None))
        self.assertEqual(len(c.objects), 2)  # Sets correct number of objects
        self.assertTrue(c.get(limitby=1))
        self.assertEqual(len(c.objects), 1)  # Sets correct number of objects
        self.assertTrue(c.get(limitby=(0, 2)))
        self.assertEqual(len(c.objects), 2)  # Sets correct number of objects
        self.assertTrue(c.get(limitby=(1, 2)))
        self.assertEqual(len(c.objects), 1)  # Sets correct number of objects

        self.assertTrue(t.remove())  # Remove test object
        self.assertTrue(t2.remove())  # Remove test object 2
        return

    def test__last(self):
        # Uninitialized last is None
        self.assertEqual(Collection(DBH.test).last(), None)
        # Returns correct last
        self.assertEqual(Collection(DBH.test, objects=LIST).last(),
                         'ghi')

    def test__only(self):
        # Test with id
        t = self._obj(number=1)
        t2 = self._obj(number=2)
        self.assertTrue(t.id and t2.id and t.id != t2.id)  # Ids are unique
        c = Collection(DBH.test)
        self.assertTrue(c.only(id=t.id))
        self.assertEqual(len(c.objects), 1)  # Sets correct number of objects
        o = c.objects[0]
        self.assertEqual(o.company_id, COMPANY_ID)  # Correct company_id
        self.assertEqual(o.name, NAME)  # Correct name
        self.assertEqual(o, t)  # Object matches original

        # Test with query
        self.assertTrue(c.only(query=(DbObject(DBH.test).tbl_.name == NAME)))
        self.assertEqual(len(c.objects), 1)  # Sets correct number of objects
        self.assertEqual(c.objects[0], t)  # Object matches original

        # Query returning no records should raise exception
        c = Collection(DBH.test)
        self.assertRaises(DbIOError, c.only, 0, None, None)
        try:
            c.only(id=-1)
        except DbIOError, err:
            self.assertTrue(re.compile(r'.*No record found.*').search(
                err.message))

        # Query returning more than one record should raise exception
        query = DbObject(DBH.test).tbl_.company_id == COMPANY_ID
        self.assertRaises(DbIOError, c.only, 0, query, None)
        try:
            c.only(query=query)
        except DbIOError, err:
            self.assertTrue(re.compile(r'.*More than one.*').search(
                err.message))
        self.assertTrue(t.remove())  # Remove test object
        self.assertTrue(t2.remove())  # Remove test object 2
        return


class TestDbIOError(unittest.TestCase):

    def test____init__(self):
        try:
            raise DbIOError('gl_detail', 'id', 12345, 'Unable to read')
        except DbIOError, err:
            self.assertEqual(err.table_name, 'gl_detail')
            self.assertEqual(err.field_name, 'id')
            self.assertEqual(err.field_value, 12345)
            self.assertEqual(err.message, 'Unable to read')
        return

    def test____repr__(self):
        try:
            raise DbIOError('gl_detail', 'id', 12345, 'Unable to read')
        except DbIOError, err:
            self.assertEqual(str(err),
                             'Unable to read, gl_detail, id=12345')
        return


class TestDbObject(unittest.TestCase):

    i_re = re.compile(r'^\d+$')
    COMPANY_ID = None
    COMPANY_ID_2 = 222
    NUMBER = 1000
    NUMBER_2 = 2000
    NAME = '__test_table_name__'
    NAME_2 = '__test_table_name_2__'
    AMOUNT = D('123.45')
    AMOUNT_2 = D('987.65')
    START_DATE = datetime.date(2010, 1, 11)
    START_DATE_2 = datetime.date(2010, 2, 22)
    STATUS = 'a'
    STATUS_2 = 'd'

    def setUp(self):
        # C0103: *Invalid name "%s" (should match %s)*
        # W0603: *Using the global statement*

        # pylint: disable=C0103,W0603
        DBH.executesql(TEST_DELETE_COMPANY)
        DBH.executesql(TEST_INSERT_COMPANY)
        DBH.commit()
        global COMPANY_ID
        COMPANY_ID = None

        # Get the id of the test company

        rows = \
            DBH.executesql("""
            SELECT id FROM company
            WHERE name = '%s'
            """
                           % '__test__')
        if len(rows) <= 0:
            return
        row = rows[0]
        if len(row) <= 0:
            return
        COMPANY_ID = row[0]

    def tearDown(self):
        # C0103: *Invalid name "%s" (should match %s)*
        # pylint: disable=C0103
        DBH.executesql(TEST_DELETE_COMPANY)
        DBH.commit()

    def test____init__(self):
        # R0915: *Too many statements (%s/%s)*
        # pylint: disable=R0915

        t = DbObject(DBH.test)
        DBH.executesql("""DELETE from test;""")
        self.assertTrue(t)  # Object created

        # Ensure object has default properties
        self.assertTrue(hasattr(t, 'db_'))
        self.assertTrue(hasattr(t, 'set_'))
        self.assertTrue(isinstance(t.set_, Collection))

        # Test a few object properties
        self.assertTrue(hasattr(t, 'company_id'))
        self.assertTrue(hasattr(t, 'status'))

        # Test setting and getting field values
        t.company_id = COMPANY_ID
        t.status = 'd'
        self.assertEqual(t.company_id, COMPANY_ID)
        self.assertEqual(t.status, 'd')

        self.assertEqual(t.db_(t.tbl_.id > 0).count(), 0)  # Has no records

        # Raw sql

        t.db_.executesql("""
            INSERT into test
                (company_id, status)
            VALUES
                (%s, '%s');
            """
                         % (COMPANY_ID, STATUS))
        self.assertEqual(t.db_(t.tbl_.id > 0).count(), 1)  # Has one record
        rows = \
            t.db_.executesql("""
            SELECT id, company_id, name, status from test;
            """)
        self.assertTrue(self.i_re.match(str(rows[0][0])))  # Id is integer
        self.assertEqual(rows[0][1], COMPANY_ID)  # company_id matches
        self.assertEqual(rows[0][2], None)  # unset name is None
        self.assertEqual(rows[0][3], STATUS)  # status matches

        t.tbl_.truncate()
        t.db_.commit()
        self.assertEqual(t.db_(t.tbl_.id > 0).count(), 0)  # Has no records

        # Test passing attributes as parameters.

        t = DbObject(DBH.test)
        # No parameters, name is None
        self.assertEqual(t.name, None)
        t = DbObject(DBH.test, name=NAME)
        # Provide name as parameter, gets set.
        self.assertEqual(t.name, NAME)
        t = DbObject(DBH.test, name=NAME, xxxx='__fake__')
        # Provide name as parameter, gets set.
        # No field attribute is not set.
        self.assertEqual(t.name, NAME)
        self.assertFalse(hasattr(t, 'xxxx'))

        # Test set_ property.
        t = DbObject(DBH.test)
        t.tbl_.truncate()
        t.db_.commit()

        t.company_id = COMPANY_ID
        t.name = NAME
        t.number = NUMBER
        t.start_date = START_DATE
        t.status = STATUS
        self.assertTrue(t.add())  # Add succeeds

        t2 = DbObject(DBH.test)
        t2.company_id = COMPANY_ID
        t2.name = NAME_2
        t2.number = NUMBER_2
        t2.start_date = START_DATE_2
        t2.status = STATUS_2
        self.assertTrue(t2.add())  # Add (2) succeeds

        collection = t.set_.get(id=t.id)
        self.assertEqual(collection.objects, [t])
        collection = t.set_.get(id=t2.id)
        self.assertEqual(collection.objects, [t2])
        collection = t.set_.get(query=t.tbl_.name == 'fake')
        self.assertEqual(collection.objects, [])
        collection = t.set_.get(query=t.tbl_.status != '')
        self.assertEqual(collection.objects, [t, t2])

        return

    def test____copy__(self):
        t = DbObject(DBH.test)
        t.company_id = COMPANY_ID
        t.number = NUMBER
        t.name = NAME
        t.amount = AMOUNT
        t.start_date = START_DATE
        t.status = STATUS
        t2 = copy.copy(t)
        self.assertEqual(t, t2)
        return

    def test____deepcopy__(self):
        t = DbObject(DBH.test)
        t.company_id = COMPANY_ID
        t.number = NUMBER
        t.name = NAME
        t.amount = AMOUNT
        t.start_date = START_DATE
        t.status = STATUS
        t2 = copy.deepcopy(t)
        self.assertEqual(t, t2)
        return

    def test____eq__(self):
        t = DbObject(DBH.test)
        t2 = DbObject(DBH.test)
        self.assertEqual(t, t2)  # same objects are equal
        t.company_id = COMPANY_ID
        t2.company_id = COMPANY_ID
        self.assertEqual(t, t2)  # same change, objects still equal
        t2.company_id = COMPANY_ID_2
        self.assertNotEqual(t, t2)  # one changed, objects not equal
        return

    def test____ne__(self):
        t = DbObject(DBH.test)
        t2 = DbObject(DBH.test)
        self.assertFalse(t != t2)  # same objects are not not equal
        t.company_id = COMPANY_ID
        t2.company_id = COMPANY_ID
        self.assertFalse(t != t2)  # same change, objects not not equal
        t2.company_id = COMPANY_ID_2
        self.assertNotEqual(t, t2)  # one changed, objects not equal
        self.assertTrue(t != t2)  # one changed, objects not euqal is true
        return

    def test____repr__(self):
        # repr() returns non-empty string
        self.assertTrue(len(repr(DbObject(DBH.test))) > 0)

        # Return value is tested in export_as_csv

        return

    def test____str__(self):
        # str() returns non-empty string
        self.assertTrue(len(str(DbObject(DBH.test))) > 0)

        # Return value is tested in export_as_csv

        return

    def test__as_dict(self):
        t = DbObject(DBH.test)
        self.assertEqual(t.as_dict(), {
            'id': None,
            'company_id': None,
            'number': None,
            'name': None,
            'amount': D('0.00'),
            'start_date': None,
            'status': None,
            'creation_date': None,
            'modified_date': None,
            })
        t.company_id = COMPANY_ID
        t.number = NUMBER
        t.name = NAME
        t.amount = AMOUNT
        t.start_date = START_DATE
        t.status = STATUS
        self.assertEqual(t.as_dict(), {
            'id': None,
            'company_id': COMPANY_ID,
            'number': NUMBER,
            'name': NAME,
            'amount': AMOUNT,
            'start_date': START_DATE,
            'status': STATUS,
            'creation_date': None,
            'modified_date': None,
            })
        return

    def test__as_list(self):
        t = DbObject(DBH.test)

        # Uninitialized returns list of default values
        self.assertEqual(t.as_list(), [
            None,
            None,
            None,
            None,
            D('0.00'),
            None,
            None,
            None,
            None,
            ])

        t.company_id = COMPANY_ID
        t.number = NUMBER
        t.name = NAME
        t.amount = AMOUNT
        t.start_date = START_DATE
        t.status = STATUS
        # Initialized returns expected list
        self.assertEqual(t.as_list(), [
            None,
            COMPANY_ID,
            NUMBER,
            NAME,
            AMOUNT,
            START_DATE,
            STATUS,
            None,
            None,
            ])
        return

    def test__add(self):

        t = DbObject(DBH.test)
        t.tbl_.truncate()
        t.db_.commit()

        t.company_id = COMPANY_ID
        t.number = NUMBER
        t.name = NAME
        t.amount = AMOUNT
        t.start_date = START_DATE
        t.status = STATUS
        self.assertTrue(t.add())  # Add succeeds
        self.assertTrue(self.i_re.match(str(t.id)))  # Object id field is set
        # Creation and modified dates should be set.
        self.assertTrue(isinstance(t.creation_date, datetime.datetime))
        self.assertTrue(isinstance(t.modified_date, datetime.datetime))

        rows = \
            t.db_.executesql("""
            SELECT
                id,
                company_id,
                number,
                name,
                amount,
                start_date,
                status,
                creation_date,
                modified_date
            FROM test;
            """)
        self.assertEqual(rows[0][0], t.id)  # Id matches
        self.assertEqual(rows[0][1], COMPANY_ID)  # company_id matches
        self.assertEqual(rows[0][2], NUMBER)  # number matches
        self.assertEqual(rows[0][3], NAME)  # name matches
        self.assertEqual(rows[0][4], AMOUNT)  # amount matches
        self.assertEqual(rows[0][5], START_DATE)  # start_date matches
        self.assertEqual(rows[0][6], STATUS)  # status matches
        # Creation and modified dates should be set.
        self.assertTrue(isinstance(rows[0][7], datetime.datetime))
        self.assertTrue(isinstance(rows[0][8], datetime.datetime))

        old_id = t.id
        self.assertTrue(t.add())  # Successive add succeeds
        self.assertTrue(t.id != old_id)  # Object has new id
        self.assertEqual(t.db_(t.tbl_.id > 0).count(), 2)  # Now two records

        t.tbl_.truncate()
        t.db_.commit()

        # Test MySQL column default values.
        t2 = DbObject(DBH.test)
        self.assertEqual(t2.status, None)     # Status initially null.
        t2.add()
        rows = \
            t2.db_.executesql("""
            SELECT
                id,
                company_id,
                number,
                name,
                amount,
                start_date,
                status,
                creation_date,
                modified_date
            FROM test;
            """)
        self.assertEqual(rows[0][0], t2.id)  # Id matches
        self.assertEqual(rows[0][6], 'a')   # status matches default
        self.assertEqual(t2.status, 'a')     # Instance is updated.

        t2.tbl_.truncate()
        t2.db_.commit()
        return

    def test__export_as_csv(self):
        t = DbObject(DBH.test)
        t.tbl_.truncate()
        t.db_.commit()

        t.company_id = COMPANY_ID
        t.name = NAME
        t.number = NUMBER
        t.amount = AMOUNT
        t.start_date = START_DATE
        t.status = STATUS
        self.assertTrue(t.add())  # Add succeeds

        output = cStringIO.StringIO()
        t.export_as_csv(out=output)

        # String fields are double quoted.

        self.assertEqual("""%s,%s,%s,"%s",%s,"%s","%s","%s","%s"\r\n"""
                         % (
            t.id,
            COMPANY_ID,
            NUMBER,
            NAME,
            AMOUNT,
            START_DATE,
            STATUS,
            t.creation_date,
            t.modified_date,
            ), output.getvalue())

        t.tbl_.truncate()
        t.db_.commit()
        return

    def test__modify(self):

        t = DbObject(DBH.test)
        t.tbl_.truncate()
        t.db_.commit()

        t.company_id = COMPANY_ID
        t.name = NAME
        t.number = NUMBER
        t.start_date = START_DATE
        t.status = STATUS
        self.assertTrue(t.add())  # Add succeeds

        original_modified_date = t.modified_date

        t.name = NAME_2
        time.sleep(1)  # Pause one sec so the modified date will change
        self.assertTrue(t.modify())  # Modify succeeds

        rows = \
            t.db_.executesql("""
            SELECT
                id,
                company_id,
                name,
                number,
                start_date,
                status,
                creation_date,
                modified_date
            FROM test;
            """)
        self.assertEqual(rows[0][0], t.id)  # Id matches
        self.assertEqual(rows[0][1], COMPANY_ID)  # company_id matches
        self.assertEqual(rows[0][2], NAME_2)  # name matches
        self.assertEqual(rows[0][3], NUMBER)  # number matches
        self.assertEqual(rows[0][4], START_DATE)  # start_date matches
        self.assertEqual(rows[0][5], STATUS)  # status matches
        # Creation and modified dates should be set.
        self.assertTrue(isinstance(rows[0][6], datetime.datetime))
        self.assertTrue(isinstance(rows[0][7], datetime.datetime))

        # modified date is updated
        self.assertNotEqual(t.modified_date, original_modified_date)

        t.tbl_.truncate()
        t.db_.commit()
        return

    def test__remove(self):

        def names():
            n = []
            rows = t.db_.executesql("""SELECT name FROM test;""")
            if len(rows) > 0:
                for r in rows:
                    if len(r) > 0:
                        n.append(r[0])
            return n

        t = DbObject(DBH.test)
        t.tbl_.truncate()
        t.db_.commit()

        t.company_id = COMPANY_ID
        t.name = NAME
        t.number = NUMBER
        t.start_date = START_DATE
        t.status = STATUS
        self.assertFalse(t.remove())  # Remove fails if record not added

        self.assertTrue(t.add())  # Add succeeds

        t2 = DbObject(DBH.test)
        t2.company_id = COMPANY_ID
        t2.name = NAME_2
        t2.number = NUMBER_2
        t2.start_date = START_DATE_2
        t2.status = STATUS_2
        self.assertTrue(t2.add())  # Add (2) succeeds

        # Table populated as expected
        self.assertEqual(names(), [NAME, NAME_2])

        self.assertTrue(t.remove())  # Remove returns success

        self.assertEqual(names(), [NAME_2])  # Table populated as expected

        self.assertTrue(t.add())  # Object can be re-added.

        self.assertTrue(t2.remove())  # Remove (2) returns success
        self.assertEqual(names(), [NAME])  # Table populated as expected
        self.assertTrue(t.remove())  # Remove returns success
        return

    def test__update(self):

        def initialize():
            t = DbObject(DBH.test)
            t.tbl_.truncate()
            t.db_.commit()

            t.company_id = COMPANY_ID
            t.number = NUMBER
            t.name = NAME
            t.amount = AMOUNT
            t.start_date = START_DATE
            t.status = STATUS
            self.assertTrue(t.add())
            return t

        records = DbObject(DBH.test).set_.get()
        self.assertEqual(len(records), 0)

        t = initialize()
        records = DbObject(DBH.test).set_.get()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], t)

        t2 = DbObject(DBH.test)
        t2.company_id = COMPANY_ID_2
        t2.number = NUMBER_2
        t2.name = NAME_2
        t2.amount = AMOUNT_2
        t2.start_date = START_DATE_2
        t2.status = STATUS_2

        # Record is not in database, should add
        self.assertTrue(t2.update())
        records = DbObject(DBH.test).set_.get()
        self.assertEqual(len(records), 2)
        self.assertNotEqual(t.id, t2.id)

        # Record is in database, should modify
        self.assertTrue(t2.update())
        records = DbObject(DBH.test).set_.get()
        self.assertEqual(len(records), 2)
        self.assertNotEqual(t.id, t2.id)

        # Update record with identical key fields, should modify t
        t = initialize()
        t2 = DbObject(DBH.test)
        t2.company_id = COMPANY_ID
        t2.number = NUMBER_2
        t2.name = NAME
        t2.amount = AMOUNT_2
        t2.start_date = START_DATE_2
        t2.status = STATUS_2

        self.assertTrue(t2.update(key_fields=['company_id', 'name']))

        tests = t.set_.get()
        self.assertEqual(len(tests), 1)
        self.assertEqual(t.id, t2.id)

        # Update record with non-identical key fields but matching id, should
        # modify.
        t = initialize()
        t2 = DbObject(DBH.test)
        t2.id = t.id
        t2.company_id = COMPANY_ID_2
        t2.number = NUMBER_2
        t2.name = NAME_2
        t2.amount = AMOUNT_2
        t2.start_date = START_DATE_2
        t2.status = STATUS_2

        self.assertTrue(t2.update(key_fields=['company_id', 'name']))

        tests = t.set_.get()
        self.assertEqual(len(tests), 1)
        self.assertEqual(t.id, t2.id)
        self.assertEqual(tests[0].company_id, t2.company_id)

        # Update record with non-identical key fields, no id, should add
        t = initialize()
        t2 = DbObject(DBH.test)
        t2.id = None
        t2.company_id = COMPANY_ID_2
        t2.number = NUMBER_2
        t2.name = NAME_2
        t2.amount = AMOUNT_2
        t2.start_date = START_DATE_2
        t2.status = STATUS_2

        self.assertTrue(t2.update(key_fields=['company_id', 'name']))

        tests = t.set_.get()
        self.assertEqual(len(tests), 2)
        self.assertNotEqual(t.id, t2.id)

        # Test with a key field not defined.
        t = initialize()
        t2 = DbObject(DBH.test)
        t2.id = None
        t2.company_id = COMPANY_ID_2

        self.assertTrue(t2.update(key_fields=['company_id', 'name']))

        tests = t.set_.get()
        self.assertEqual(len(tests), 2)
        self.assertNotEqual(t.id, t2.id)

        t3 = DbObject(DBH.test)
        t3.id = None
        t3.company_id = COMPANY_ID_2

        self.assertTrue(t3.update(key_fields=['company_id', 'name']))

        tests = t.set_.get()
        self.assertEqual(len(tests), 2)
        self.assertEqual(t2.id, t3.id)

        # Make sure it distinguishes between NULL and empty string.
        t = initialize()
        t2 = DbObject(DBH.test)
        t2.id = None
        t2.company_id = COMPANY_ID_2
        t2.name = ''

        self.assertTrue(t2.update(key_fields=['company_id', 'name']))

        t3 = DbObject(DBH.test)
        t3.id = None
        t3.company_id = COMPANY_ID_2

        self.assertTrue(t3.update(key_fields=['company_id', 'name']))

        tests = t.set_.get()
        self.assertEqual(len(tests), 3)
        self.assertNotEqual(t2.id, t3.id)

        t.tbl_.truncate()
        t.db_.commit()
        return


class TestFunctions(unittest.TestCase):
    def test__rows_to_objects(self):
        db = DBH
        query = db.account.id > 0

        # Single table
        companies = Company(db.company).set_.get()
        rows = db().select(db.company.ALL)
        objects = {'company': (Company, db.company)}
        instances = rows_to_objects(rows, objects)
        self.assertEqual(len(instances), len(companies))
        for i in instances:
            self.assertEqual(sorted(i.keys()), ['company'])
            company = Company(db.company).set_.get(id=i['company'].id).first()
            self.assertEqual(i['company'], company)

        # Multiple tables
        # Start with just one account
        account = Account(db.account).set_.get(query=query).first()
        company = Company(db.company).set_.get(id=account.company_id).first()

        rows = db(db.account.id == account.id).select(
                db.company.ALL, db.account.ALL,
                left=db.company.on(db.account.company_id == db.company.id))
        objects = {'company': (Company, db.company),
                'account': (Account, db.account)}
        instances = rows_to_objects(rows, objects)
        self.assertEqual(len(instances), 1)
        self.assertEqual(sorted(instances[0].keys()), ['account', 'company'])
        self.assertEqual(instances[0]['account'], account)
        self.assertEqual(instances[0]['company'], company)

        # Now test the whole set
        rows = db().select(
                db.company.ALL, db.account.ALL,
                left=db.company.on(db.account.company_id == db.company.id))
        objects = {'company': (Company, db.company),
                'account': (Account, db.account)}
        instances = rows_to_objects(rows, objects)
        self.assertEqual(len(instances), len(rows))
        for i in instances:
            self.assertEqual(sorted(i.keys()), ['account', 'company'])
            account = Account(db.account).set_.get(id=i['account'].id).first()
            company = Company(db.company).set_.get(id=i['company'].id).first()
            self.assertEqual(i['account'], account)
            self.assertEqual(i['company'], company)


def main():

    # Suite setup will already be called

    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()
    suite_teardown()


if __name__ == '__main__':
    main()
