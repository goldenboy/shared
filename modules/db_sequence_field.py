#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Classes for handling database sequence fields.

"""


class DbSequenceField(object):

    """Class representing a mysql database table sequence field.

    A sequence field is one that contains a number representing a sequence
    order. The class provides simple methods for changing a record's sequence
    and ensuring all records' sequences are consistent, eg no two records have
    the same sequence value.
    """

    def __init__(self, field=None):

        # pylint: disable=W0212,C0103

        self.field = field
        self.db_ = self.field._db
        self.table = self.field._db[self.field._tablename]

    def move(self, record_id, position='end'):
        """
        Move a record within the sequence to the indicated position.
        record_id - id of record
        position - new sequence position
                   can be an integer or a key word
                   'start' - move to start of sequence
                   'end'   - move to end of sequence
        """

        if not record_id:
            return

        # Determine the current position

        rows = self.db_(self.table.id == record_id).select()

        if not len(rows) > 0:
            return
        current_pos = rows[0][self.field.name]

        if isinstance(position, str):
            if position == 'start':
                position = 1
            elif position == 'end':
                position = self.tidy() + 1
            elif position == 'up':
                position = current_pos - 1
            elif position == 'down':
                position = current_pos + 1
            else:
                return

        if position == current_pos:
            return   # nothing to do

        # Increment(decrement) the value of the sequence field for all records
        # where the current value is between the position and the current
        # position inclusive.

        query = self.field != None
        delta = 1
        if position < current_pos:
            query = query & (self.field >= position)
            query = query & (self.field <= current_pos)
        else:
            query = query & (self.field <= position)
            query = query & (self.field >= current_pos)
            delta = -1

        self.db_(query).update(**dict([[self.field.name, self.field
                               + delta * 1]]))
        self.db_.commit()

        # Update the moved record

        self.db_(self.table.id
                 == record_id).update(**dict([[self.field.name,
                position]]))
        self.db_.commit()

        # Tidy up

        self.tidy()
        return

    def tidy(self):
        """
        Tidy up values in sequence field.
        * Make sure every record has a value.
        * Make sure there are no duplicates
        * Make sure the sequence values are sequential.

        Any records wwhere sequence is NULL are given sequence values at the
        end.

        If two records have the same sequence value, the one with the lower id
        is given a lower sequence value.

        Returns the number of records in the sequence.
        """

        # Update records with non-NULL sequence values first, then NULL ones

        count = 1
        queries = [self.field != None, self.field == None]
        for query in queries:
            rows = self.db_(query).select(self.table.ALL,
                    orderby=self.field)
            for row in rows:
                if row[self.field.name] != count:
                    row.update_record(**dict([[self.field.name,
                            count]]))
                count += 1
        self.db_.commit()
        return count

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return self.__repr__()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
