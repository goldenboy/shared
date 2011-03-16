#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Classes for handling database tables.

"""

import cStringIO
import csv
import datetime
import sys

# C0103 Invalid name "id" (should match [a-z_][a-z0-9_]{2,30}$)
# E0203 Access to member 'creation_date' before its definition line 318
# E1101 Instance of 'Collection' has no '_table_class' member
# W0142 Used * or ** magic
# W0201 Attribute 'creation_date' defined outside __init__
# W0622 Redefining built-in 'id'

# pylint: disable=C0103,E0203,E1101,W0142,W0201,W0622


class Collection(object):

    """Class representing a collection of Table object instances.

    """

    def __init__(
        self,
        tbl_,
        db_=None,
        class_=None,
        objects=None,
        ):
        """Constructor

        Args:
            tbl_: gluon/sql.py SQLTable object instance
            db_: gluon/sql.py SQLDB object instance
                Optional. If not provided, tbl_['_db'] is used.
            class_: the class the objects will be created as
            objects: list of DbObject object instances
        """

        self.tbl_ = tbl_
        if db_:
            self.db_ = db_
        else:
            self.db_ = self.tbl_['_db']
        if class_:
            self.class_ = class_
        else:
            self.class_ = DbObject
        self.objects = objects or []
        return

    def __getitem__(self, i):
        """Permits access of objects using self[key] where key is integer or
        slice.
        """

        return self.objects[i]

    def __iter__(self):
        """Permits the object to be used as an iterator."""

        for obj in self.objects:
            yield obj

    def __len__(self):
        """Return length of object."""

        return len(self.objects)

    def __nonzero__(self):
        """Return truth value of object."""

        if len(self.objects):
            return 1
        return 0

    def __repr__(self):
        output = cStringIO.StringIO()
        self.export_as_csv(out=output)
        return output.getvalue()

    def __str__(self):
        return self.__repr__()

    def as_dict(self):
        """Return object as a dict

        The dict has the form { id: Object, id2, Object3, ...}
        The dict can be used as a lookup table.
        """

        if not self.objects:
            return {}
        obj_dict = {}
        for obj in self.objects:
            obj_dict[obj.id] = obj
        return obj_dict

    def export_as_csv(self, out=None, header=0):
        """Write object in csv format.

        Args:
            out     File like object that has write method.
                    Defaults sys.stdout.
            header  Boolean, If True, print a header of field names.

        Raises:
            SyntaxError, if record is not in database.

        """

        if not out:
            out = sys.stdout
        csv_writer = csv.writer(out, quoting=csv.QUOTE_NONNUMERIC)
        if header:
            csv_writer.writerow(self.tbl_.fields)
        for obj in self.objects:
            csv_writer.writerow(obj.as_list())
        return

    def first(self):
        """Return first object"""

        if not self.objects:
            return None
        return self[0]

    def get(
        self,
        id=None,
        query=None,
        orderby=None,
        limitby=None,
        ):
        """Get the collection of DbObject object instances.

        Args:
            id: integer, id of record to get
            query: SQLQuery representing an SQL where clause, for
                   example: db.person.name=='John'
                   defaults None, ie gets all records
            orderby: list, tuple or string, cmp orderby attribute as per
                    gluon.sql.SQLSet._select()
                    Example: db.person.name
                    Defaults: self.tbl_.id, ie by id
            limitby: integer or tuple. Tuple is format (start, stop). If
                    integer converted to tuple (0, integer)
                    Examples:
                        limitby=None        return all records
                        limitby=100         return first 100 records
                        limitby=(0, 100)    return first 100 records
                        limitby=(100, 199)  return 99 records starting at
                                                number 100

        Returns:
            self    The object itself is returned. A successful get populates
                    the "objects" property.

        Raises:
            SyntaxError, if record is not in database.

        Notes:
            if the id parameter is provided, the query, orderby and limitby
                parameters are ignored.
            If both id and query parameters are None, objects for all records
            in the table are returned. Id set to zero will produce a differnt
            result than id set to None. Likewise query set to empty string is
            not the same as query set to None.

            id      query      result
            0       -       0   records (SQL is made, should not match any)
            1       -       1   record
            None    ''      0   records (SQL call is not made)
            None    query   x   records
            None    None    all records
        """

        self.objects = []

        if not hasattr(self, 'db_') or not hasattr(self, 'tbl_'):
            return self

        if not orderby:
            orderby = self.tbl_.id

        if not limitby:
            limitby = None
        elif not hasattr(limitby, '__len__'):
            # Convert integer to tuple
            limitby = (0, int(limitby))

        rows = None
        if id != None:
            rows = self.db_(self.tbl_.id == id).select()
        else:
            if query != None:
                if query:
                    rows = self.db_(query).select(orderby=orderby,
                            limitby=limitby)
            else:
                rows = self.db_().select(self.tbl_.ALL, orderby=orderby,
                        limitby=limitby)

        if not rows:
            return self

        for row in rows:
            db_obj = self.class_(self.tbl_)
            for field in db_obj.tbl_.fields:
                if hasattr(row, field):
                    setattr(db_obj, field, row[field])
            self.objects.append(db_obj)
        return self

    def last(self):
        """Return last object"""

        if not self.objects:
            return None
        return self[-1]

    def only(
        self,
        id=None,
        query=None,
        orderby=None,
        ):
        """Get the collection of DbObject object instances.

        Notes:
            Equivalent to get() but raises an error if the number of records
            found is not one.

        Args:
            see get()

        """

        self.get(id=id, query=query, orderby=orderby)
        if len(self.objects) == 0:
            raise DbIOError('', '', '', 'Expected one. No record found.')
        if len(self.objects) > 1:
            raise DbIOError('', '', '',
                    'Expected one. More than one record found.')
        return self


class DbIOError(Exception):

    """General exception for database IO errors"""

    def __init__(
        self,
        table_name,
        field_name,
        field_value,
        message,
        ):
        """Constructor.

        Args:
            table_name: string, name of database table
            field_name: string, name of the table field
            field_value: string, value of the table field
            message: string, error message

        Example:
            try:
                raise DbIOError('gl_detail', 'id', 12345, 'Unable to read')
            except DbIOError, e:
                print e

        """

        super(DbIOError, self).__init__()
        self.table_name = table_name
        self.field_name = field_name
        self.field_value = field_value
        self.message = message
        return

    def __repr__(self):
        return '{msg}, {table}, {field}={value}'.format(msg=self.message,
                table=self.table_name, field=self.field_name,
                value=self.field_value)

    def __str__(self):
        return repr(self)


class DbObject(object):

    """Class representing an object associated with database table record.

    """

    def __init__(self, tbl_, **kwargs):
        """Constructor

        Args:
            tbl_: gluon/sql.py SQLTable object instance
            kwargs: any number of database table field/value pairs.

        Notes:
            Trailing underscores are used in property names to ensure argument
            won't conflict with a database table field name.
        """

        self.tbl_ = tbl_
        for field in self.tbl_.fields:
            self.__dict__[field] = self.tbl_[field].default
        for key in kwargs.keys():
            if key in self.tbl_.fields:
                self.__dict__[key] = kwargs[key]
            elif key == 'db_':
                self.db_ = kwargs[key]
        if not hasattr(self, 'db_'):
            self.db_ = self.tbl_['_db']
        self.set_ = Collection(tbl_=self.tbl_, db_=self.db_,
                               class_=self.__class__)
        return

    def __copy__(self):
        table = self.__class__(self.tbl_)
        for field in self.tbl_.fields:
            table.__dict__[field] = self.__dict__[field]
        return table

    def __deepcopy__(self, unused_memo):
        # There is no deepness to copy, so just return __copy__()
        return self.__copy__()

    def __eq__(self, other):
        for field in self.tbl_.fields:
            if self.__dict__[field] != other.__dict__[field]:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        output = cStringIO.StringIO()
        self.export_as_csv(out=output)
        return output.getvalue()

    def __str__(self):
        return self.__repr__()

    def add(self):
        """Add a record to the database.

        Returns:
            The object itself if add succeeds, nothing otherwise.

        """

        now = None
        if hasattr(self, 'creation_date') and not self.creation_date:
            if not now:
                now = datetime_now()
            self.creation_date = now
        if hasattr(self, 'created_on') and not self.created_on:
            if not now:
                now = datetime_now()
            self.created_on = now
        if hasattr(self, 'modified_date') and not self.modified_date:
            if not now:
                now = datetime_now()
            self.modified_date = now
        if hasattr(self, 'modified_on') and not self.modified_on:
            if not now:
                now = datetime_now()
            self.modified_on = now
        if hasattr(self, 'updated_on') and not self.updated_on:
            if not now:
                now = datetime_now()
            self.updated_on = now

        args = {}
        for field in self.tbl_.fields:

            # Ignore the id field, it will get set

            if field == 'id':
                continue
            if hasattr(self, field):
                value = getattr(self, field)

                # Do not set if value is None so the defaults defined in
                # the db.table definition will be used

                if value != None:
                    args[field] = value

        id = self.tbl_.insert(**args)
        self.id = id
        self.db_.commit()

        # The database may have changed some field values with its column
        # DEFAULT definitions. Re-read the object to ensure they are in synch.
        try:
            row = self.db_(self.tbl_.id == id).select()[0]
        except IndexError:
            return self

        for field in self.tbl_.fields:
            if hasattr(row, field):
                setattr(self, field, row[field])
        return self

    def as_dict(self):
        """Return a dict representation of the object.

        The dict is of the format  { field1: value1, field2: value2... }.

        NOTE: self.__dict__ returns a dict representation of the object that
        contains elements other than the field/value pairs, eg db_.

        Returns:
            dict Dictionary of object field/value pairs.

        """

        obj_dict = {}
        for field in self.tbl_.fields:
            if hasattr(self, field):
                obj_dict[field] = getattr(self, field)
        return obj_dict

    def as_list(self):
        """Return a list representation of the object.

        The list of values are in the order the fields are defined, ie as
        returned by db.table.fields.

        Returns:
            list List of object field values.

        """

        obj_list = []
        for field in self.tbl_.fields:
            if hasattr(self, field):
                obj_list.append(getattr(self, field))
        return obj_list

    def export_as_csv(self, out=None):
        """Write object in csv format.

        Args:
            out, File like object that has write method.
                    Defaults sys.stdout.

        Raises:
            SyntaxError, if record is not in database.

        """

        if not out:
            out = sys.stdout
        csv_writer = csv.writer(out, quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(self.as_list())
        return

    def modify(self):
        """Modify in the database the record associated with the object.

        Returns:
            The object itself if modify succeeds, nothing otherwise.

        Raises:
            SyntaxError, if record is not in database.

        """

        # An id is necessary in order to know which record to pdate

        if not self.id:
            return

        rows = self.db_(self.tbl_.id == self.id).select()
        if not rows:
            raise SyntaxError('No such record, id = {id}'.format(id=self.id))
        row = rows[0]

        if hasattr(self, 'modified_date'):
            self.modified_date = datetime_now()
        if hasattr(self, 'modified_on'):
            self.modified_on = datetime_now()
        if hasattr(self, 'updated_on'):
            self.updated_on = datetime_now()

        args = {}
        for field in self.tbl_.fields:

            # Ignore the id field, it will have been set

            if field == 'id':
                continue
            if hasattr(self, field):
                args[field] = getattr(self, field)

        row.update_record(**args)
        self.db_.commit()
        return self

    def remove(self):
        """Delete from the database the record associated with the object.

        Returns:
            True if the delete succeeds, False otherwise.

        Raises:
            SyntaxError, if record is not in database.

        """

        # An id is necessary in order to know which record to delete

        if not self.id:
            return

        try:
            self.db_(self.tbl_.id == self.id).delete()
        except:
            raise SyntaxError('Unable to delete record, id = {id}'.format(
                id=self.id))
        self.db_.commit()
        return 1

    def update(self, key_fields=None):
        """Update in the database records with matching field values.

        !!! DEPECATED this method is not recommended. Unless all table fields
        are defined in the object instance, the record may not be updated as
        expected  !!!

        Notes:
            If the object 'id' property is defined, the record is assumed to
                exist and update calls modify() method.
            If the object 'id' property is not defined, and the only key field
                is 'id', the record is assumed to not exist and update calls
                add() method.
            If no records exist with matching field values, update calls the
                add() method.
            If one or more records exist with matching field values, each is
                updated with the values of the object.

        Args:
            update_fields: list, Only fields in this list are updated. If None,
                all fields are updated. Note: the creation_date and created_on
                field values of an existing database record are not modified
                unless explicitly indicated.
            key_fields: list, List of fields used to determine if a record
                exists, similary to a database foreign key. Defaults to ['id']

        Returns:
            The object itself if modify succeeds, nothing otherwise.
        """

        if not key_fields:
            key_fields = ['id']

        # If the record has an id, then assume it exists, call modify()
        if self.id:
            return self.modify()

        # If the record has no id, and the only key field is 'id', then call
        # add().
        if len(key_fields) == 1 and key_fields[0] == 'id':
            if not 'id' in self.__dict__ or self.__dict__['id'] is None:
                return self.add()

        # Build a query of key_fields
        query = None
        for field in key_fields:
            if not query:
                query = self.tbl_[field] == self.__dict__[field]
            else:
                query = query & (self.tbl_[field]
                                 == self.__dict__[field])

        records = self.set_.get(query=query)
        if len(records) == 0:
            self.add()
        else:
            for record in records:
                self.id = record.id
                # Only modify if there is a difference
                if self != record:
                    for field in self.tbl_.fields:
                        # Don't destroy the original creation date
                        if field not in ['creation_date', 'created_on']:
                            if hasattr(self, field):
                                record.__dict__[field] = \
                                    self.__dict__[field]
                    record.modify()
        return self


def datetime_now():
    """Now with microseconds removed"""

    now = datetime.datetime.now()
    return datetime.datetime(
        now.year,
        now.month,
        now.day,
        now.hour,
        now.minute,
        now.second,
        0,
        )


def rows_to_objects(rows, objects):
    """Convert rows to object instances.

    This is useful for returning objects with queries with left joins. Optimal
    performance is maintained.

    Args:
        rows: gluon.dal.Rows instance, as returned by db().select()
        objects: dict, defines the objects row data will be converted to.
            Format: { 'name1': (class1, db.table1),
                        'name2': (class2, db.table2), ...}
            db.table1 is a gluon.dal.Table class
            There should be one element for each table represented in the
            row data.
    Returns:
        list, a list of dicts.
            [{'name1': object1, 'name2': object2}, {...}]
            Each dictionary has an element for each table. The key is the table
            name. The value is a object instance of that table.

    Usage:
        rows = db().select(db.table1.ALL, db.table2.ALL,
            left=db.table2.on(db.table1.field==db.table2.field2))
        objects = { 'table1': (Table1, db.table1),
                    'table2': (Table2, db.table2) }
        instance_rows = rows_to_objects(rows, objects)
        print instance_rows[0]['table1'].name         # Access table1 property
        print instance_rows[0]['table2'].id           # Access table2 property
        print instance_rows[0]['table1'].fullname()   # Call table1 method
        for i in instance_rows:
            print i['table1'].name, i['table2'].description

    Notes:
        Web2py returns a different datatype for a single table.

        Single table:

          rows = db().select(db.company.ALL)
          rows is an array of Row objecst (like dictionaries)
              { 'id': 1, 'name': 'My Company', ... }

        Multiple tables:

          rows = db(db.account.number == '1010').select(
                  db.account.ALL,
                  db.company.ALL,
                  left=db.company.on(db.account.company_id==db.company.id))
          rows is an array of Row of Rows
              { 'account': {'id': 111, ...}, 'company': {'id': 1, ...} }

         With multiple tables, rows are keyed by the table name. With a single
         table, rows are not keyed.
    """
    if len(rows) == 0:
        return
    if len(objects.keys()) == 0:
        return

    instances = []
    for r in rows:
        d = {}
        # See Notes regarding handling single tables differently from multiple
        # tables.
        if len(objects.keys()) == 1:
            for k in objects.keys():
                obj_class, obj_dal = objects[k]
                d[k] = obj_class(obj_dal, **r)
        else:
            for k in objects.keys():
                obj_class, obj_dal = objects[k]
                d[k] = obj_class(obj_dal, **r[k])
        instances.append(d)
    return instances
