#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Classes for handling table CRUD html.

Provides quick list, edit and update pages.

"""

from applications.shared.modules.pagination import Report
from gluon.html import A, URL
from gluon.sqlhtml import SQLFORM


class TableCRUD(Report):
    """Class representing CRUD functionality for a table."""

    def __init__(
        self,
        sqldb,
        request,
        response,
        session,
        table_name,
        report_function='table_list',
        update_function='table_update',
        ):
        """Constructor.

        Args:
            sqldb: SQLDB object instance
            request: gluon.globals.Request object instance
            response: gluon.globals.Response object instance
            session: gluon.globals.Session object instance
            table_name: string, name of the table
            report_function: string, name of the report controller function
            update_function: string, name of the table update function
        """

        self.sqldb = sqldb
        self.request = request
        self.response = response
        self.session = session
        self.table_name = table_name
        self.report_function = report_function
        self.update_function = update_function
        self.sqldb_table = self.sqldb[self.table_name]  # SQLDB Table
        cols = []
        for field in self.sqldb_table.fields[0:5]:
            cols.append((field.title(), field, field, 0))
        cols.append(('Edit', self._format_edit, '', None))
        self.columns = cols
        Report.__init__(self, self.request, self.report_function,
                self.sqldb, self.columns)

    def _format_edit(self, row):
        """Return an HTML anchor representing a edit record link.

        Column format function.

        Args:
            row: Storage or list, table record

        Returns:
            string, HTML anchor
        """
        return A('edit', _href=URL(r=self.request, f=self.update_function,
            args=[row['id']], vars=self.request.vars))

    def rows(self, page, items_per_page, order_by, order_dir):
        """Retrieve rows for a page.

        Args:
            page: integer, the number of the page whose rows are retrieved
            items_per_page: integer
            order_by: string, name of field to sort by
            order_dir: string, order direction

        Returns:
            Storage: row data.

        """

        order_l = [self.sqldb_table[order_by]]
        if bool(int(order_dir)):
            order_l = [~x for x in order_l]

        offset = page * items_per_page
        limit = (page + 1) * items_per_page
        limitby = (offset, limit)
        rows = self.sqldb(self.sql_query()).select(self.sqldb_table.ALL,
                                   orderby=order_l, limitby=limitby)
        return rows

    def sql_query(self):
        return self.sqldb_table.id > 0

    def update(self):
        """Generic table update.

        Returns:
            dict, dictionary suitable for html template
        """
        if len(self.request.args) > 0:
            row = self.sqldb(self.sqldb_table.id
                             == self.request.args[0]).select()[0]
            form = SQLFORM(self.sqldb_table, row, deletable=True)
            action = 'Update'
        else:
            form = SQLFORM(self.sqldb_table)
            action = 'Add'
        if form.accepts(self.request.vars, self.session,
                        keepvalues=True):
            self.response.flash = 'record updated'
        elif form.errors:
            self.response.flash = 'Form could not be submitted.' + \
                'Please make corrections.'
        elif not self.response.flash:
            self.response.flash = "Fill out the form and submit."
        return dict(form=form, action=action, table=self.table_name)
