#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/db_sequence_field.py

"""

from applications.shared.modules.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.db_sequence_field import DbSequenceField
from gluon.sql import SQLDB, Field
import re
import sys
import unittest

# pylint: disable=C0111


class TestDbSequenceField(unittest.TestCase):

    def setUp(self):

        # C0103: *Invalid name "%s" (should match %s)*
        # pylint: disable=C0103

        db_file_name = 'test.db'
        migrate_file_name = 'test_testy.table'
        uri = 'sqlite://%s' % db_file_name
        folder = '/tmp'
        m = re.compile(r'applications\.(?P<app>.*)\.modules'
                       ).match(__file__)
        if m:
            folder = 'applications/%s/databases' % m.group('app')
        self.db_ = SQLDB(uri=uri, folder=folder)
        try:
            self.db_.testy.drop()
        except KeyError:
            pass

        # Create table and some data

        self.db_.define_table('testy', Field('sequence', 'integer'),
                              migrate=migrate_file_name)

        self.db_(self.db_.testy.id > 0).delete()
        self.db_.commit()

        self.db_.testy.insert(sequence=None)
        self.db_.testy.insert(sequence=None)
        self.db_.testy.insert(sequence=None)
        self.db_.testy.insert(sequence=None)
        self.db_.commit()
        self.records = 4

        rows = self.db_().select(self.db_.testy.ALL)
        self.assertEqual(len(rows), self.records)

    def id_list(self):
        """
        This is a controller function used by other test functions.
        """

        rows = self.db_().select(self.db_.testy.ALL,
                                 orderby=self.db_.testy.sequence
                                 | self.db_.testy.id)
        ids = []
        for row in rows:
            ids.append(row['id'])

        return ids

    def reset_list(self, ids=None, sequences=None):
        """
        This is a controller function used by other test functions.
        """

        if not ids:
            ids = range(1, self.records + 1)
        if not sequences:
            sequences = range(1, self.records + 1)

        rows = self.db_().select(self.db_.testy.ALL)
        i = 0
        for row in rows:

            self.db_(self.db_.testy.id == row['id'
                     ]).update(sequence=sequences[i], id=ids[i])
            i += 1
        self.db_.commit()

        return

    def test____init__(self):
        # W0212: *Access to a protected member %s of a client class*
        # pylint: disable=W0212

        seq = DbSequenceField(field=self.db_.testy.sequence)
        self.assertEqual(seq.db_._dbname, 'sqlite')
        self.assertEqual(seq.table._tablename, 'testy')
        self.assertEqual(seq.field.name, 'sequence')

    def test_move(self):

        # Control - test that a reset returns expected

        self.reset_list()
        expect = [1, 2, 3, 4]
        got = self.id_list()
        self.assertEqual(got, expect)

        seq = DbSequenceField(field=self.db_.testy.sequence)

        # move with no position provided

        self.reset_list()
        seq.move(2)
        expect = [1, 3, 4, 2]  # 2 is moved to end
        got = self.id_list()
        self.assertEqual(got, expect)

        # move to new position upward

        self.reset_list()
        seq.move(4, 2)
        expect = [1, 4, 2, 3]
        got = self.id_list()
        self.assertEqual(got, expect)

        # move to new position downward

        self.reset_list()
        seq.move(1, 3)
        expect = [2, 3, 1, 4]
        got = self.id_list()
        self.assertEqual(got, expect)

        # move to same position

        self.reset_list()
        seq.move(2, 2)
        expect = [1, 2, 3, 4]
        got = self.id_list()
        self.assertEqual(got, expect)

        # move to 'start'

        self.reset_list()
        seq.move(3, 'start')
        expect = [3, 1, 2, 4]
        got = self.id_list()
        self.assertEqual(got, expect)

        # move to 'end'

        self.reset_list()
        seq.move(1, 'end')
        expect = [2, 3, 4, 1]
        got = self.id_list()
        self.assertEqual(got, expect)

        # move 'up'

        self.reset_list()
        seq.move(3, 'up')
        expect = [1, 3, 2, 4]
        got = self.id_list()
        self.assertEqual(got, expect)

        # move 'down'

        self.reset_list()
        seq.move(2, 'down')
        expect = [1, 3, 2, 4]
        got = self.id_list()
        self.assertEqual(got, expect)

        # Secessive moves
        # move 'up'

        self.reset_list()
        seq.move(2, 'up')
        expect = [2, 1, 3, 4]
        got = self.id_list()
        self.assertEqual(got, expect)

        seq.move(2, 'down')
        expect = [1, 2, 3, 4]
        got = self.id_list()
        self.assertEqual(got, expect)

        # Boundary tests
        # move first to 'start'

        self.reset_list()
        seq.move(1, 'start')
        expect = [1, 2, 3, 4]
        got = self.id_list()
        self.assertEqual(got, expect)

        # move last to 'end'

        self.reset_list()
        seq.move(4, 'end')
        expect = [1, 2, 3, 4]
        got = self.id_list()
        self.assertEqual(got, expect)

        # move first 'up'

        self.reset_list()
        seq.move(1, 'up')
        expect = [1, 2, 3, 4]
        got = self.id_list()
        self.assertEqual(got, expect)

        # move last 'down'

        self.reset_list()
        seq.move(4, 'down')
        expect = [1, 2, 3, 4]
        got = self.id_list()
        self.assertEqual(got, expect)

        # move to position outside of range

        self.reset_list()
        seq.move(2, 9999)
        expect = [1, 3, 4, 2]
        got = self.id_list()
        self.assertEqual(got, expect)

        # move to position outside of range

        self.reset_list()
        seq.move(3, -1)
        expect = [3, 1, 2, 4]
        got = self.id_list()
        self.assertEqual(got, expect)

        # invalid position

        self.reset_list()
        seq.move(1, '__invalid__')
        expect = [1, 2, 3, 4]
        got = self.id_list()
        self.assertEqual(got, expect)

    def test_tidy(self):

        # if sequence = NULL, tidy sets sequences

        count = self.db_(self.db_.testy.sequence == None).count()
        self.assertEqual(count, self.records)
        seq = DbSequenceField(field=self.db_.testy.sequence)
        seq.tidy()
        count = self.db_(self.db_.testy.sequence == None).count()
        self.assertEqual(count, 0)

        # Sequence values start at 1 and are sequential

        rows = self.db_().select(self.db_.testy.ALL)
        seqs = []
        for row in rows:
            seqs.append(int(row.sequence))
        self.assertEqual(range(1, self.records + 1), seqs)

        # if multiple records have same sequence value, tidy sets them unique

        self.db_(self.db_.testy.id > 0).update(sequence=1)
        self.db_.commit()
        count = self.db_(self.db_.testy.sequence == 1).count()
        self.assertEqual(count, self.records)
        seq = DbSequenceField(field=self.db_.testy.sequence)
        seq.tidy()
        count = self.db_(self.db_.testy.sequence == 1).count()
        self.assertEqual(count, 1)

        # Doesn't kak on an empty table

        self.db_(self.db_.testy.id > 0).delete()
        self.db_.commit()
        seq = DbSequenceField(field=self.db_.testy.sequence)
        seq.tidy()


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
