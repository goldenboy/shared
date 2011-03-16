#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Classes for handling pagination

"""
from gluon.html import A, DIV, HR, SPAN, TABLE, TD, TH, TR, URL, XML
import copy

# R0921: Abstract clas not referenced.
# pylint: disable=R0921


class Navigator(object):
    """Represents a page navigator."""

    def __init__(self, pages, page=None):
        """Constructor.

        Args:
            pages: list, list of page names in order.
            page: string, name of current page.
        """
        self.pages = pages
        self.page = page
        if not page or page not in self.pages:
            if len(self.pages) > 0:
                self.page = self.pages[0]

    def __len__(self):
        return len(self.pages)

    def next(self, count=1):
        """Return the next page.

        Args:
            count: integer, the number of pages to move forward.
        Returns:
            string, name of next page.
        """
        if len(self.pages) == 0:
            return ''
        if not self.page:
            return self.pages[0]

        if self.page not in self.pages:
            return self.page
        i = self.pages.index(self.page) + count
        i = i if i > 0 else 0
        i = i if i < len(self.pages) else len(self.pages) - 1
        return self.pages[i]

    def prev(self, count=1):
        """Return the prev page.

        Args:
            count: integer, the number of pages to move back.
        Returns:
            string, name of prev page.
        """
        if len(self.pages) == 0:
            return ''
        if not self.page:
            return self.pages[0]

        if self.page not in self.pages:
            return self.page
        i = self.pages.index(self.page) - count
        i = i if i > 0 else 0
        i = i if i < len(self.pages) else len(self.pages) - 1
        return self.pages[i]


class PageList(object):

    """
    The PageList class represents a list of page numbers for a report.

    It include methods for determining which page numbers should be displayed
    for page links given the total number of pages and the current page of the
    report being displayed.

    """

    def __init__(
        self,
        pages,
        current_page,
        min_edge=3,
        surround=9,
        ):
        """
        pages    = the total number of pages in list
        current_page = the number of the current page, pages start at 0 and run
            through pages-1
        min_edge = the minimum number of page numbers at the left and right
            ends
        surround = the minimum number of page numbers surrounding the current
            page
        """

        self.pages = pages
        self.current_page = current_page
        self.min_edge = min_edge
        self.surround = surround
        self.shown_sections = self.shown()

    def shown(self):
        """
        Return a list of lists of page numbers to be shown
        eg: [ [1,2,3], [49,50] ]
        """

        prev = -1
        sections = []
        current_list = []
        for i in [x for x in range(0, self.pages) if self.is_shown(x)]:
            if i == prev + 1:
                current_list.append(i)
            else:
                sections.append(current_list)
                current_list = [i]
            prev = i
        sections.append(current_list)
        return sections

    def is_shown(self, value):
        """Determine whether a page number is shown or not"""

        # R0911: Too many return statements
        # pylint: disable=R0911

        if value < 0 or value >= self.pages:
            return False

        # rules:
        # left and right edge have a minimum 3
        # left edge: if current page <= 9, and i <= 9 show
        # right edge: if current page > pages - 9 and i >= pages - 9 show
        # middle: if abs(current page - i ) <= 9/2 show

        if value < self.min_edge:
            return True
        if self.pages - 1 - value < self.min_edge:
            return True
        if self.current_page <= self.surround and value \
            <= self.surround:
            return True
        if self.current_page >= self.pages - self.surround and value \
            >= self.pages - self.surround:
            return True
        if value >= self.current_page - 1 - self.surround / 2:
            if value <= self.current_page + self.surround / 2:
                return True
        return False

    def __repr__(self):
        parts = []
        for sections in self.shown_sections:
            value = ''
            for page in sections:
                if page == self.current_page:
                    page_no = '**'
                else:
                    page_no = '%02d' % page
                value = value + ' ' + ' '.join((page_no, ))
            parts.append(value)
        return ' ...'.join(parts)

    def __str__(self):
        return self.__repr__()


class Report(object):
    """Class representing a paginated report."""

    def __init__(
        self,
        request,
        report_function,
        sqldb=None,
        columns=None
        ):
        """Constructor.

        Args:
            request: gluon.globals.Request object instance
            report_function: string, name of the report controller function
            sqldb: gluon.sql.SQLDB object instance
        """

        self.request = request
        self.report_function = report_function
        self.sqldb = sqldb
        self.columns = columns
        self.column_set = ReportColumnSet()
        try:
            self.column_set.add_columns(self.columns)
        except NotImplementedError:
            pass
        return

    def __len__(self):
        """Return the number of rows."""
        if self.sqldb:
            try:
                # This returns the same as len(self.rows()) but has better
                # performance.

                count = self.sqldb(self.sql_query()).count()
            except NotImplementedError:
                count = 0
        else:
            try:
                count = len(self.rows(0, 9999999, '', 0))
            except NotImplementedError:
                count = 0
        return count

    def format_delimited_list(self, row, fields, sep=''):
        """Format a list of field values.

        Args:
            row: Storage or dict, Data set.
            fields: list, List of field names.
                Names are expected to be keys of row.
            sep: string, separator.

        Returns:
            String, formatted string

        Example
            row = {'first': 'Aaaa', 'second': 'Bbbb', 'third': 'Cccc'}.
            fields = ['third', 'first']
            sep = ', '

            returns: 'Cccc, Aaaa'
        """
        # R0201: *Method could be a function*
        # pylint: disable=R0201

        values = []
        for field in fields:
            value = row[field] if field in row and row[field] else ''
            values.append(value)
        return sep.join(values).strip(sep)

    def header_link(
        self,
        report_column,
        order_by,
        order_dir,
        ):
        """Return an HTML anchor representing a column header link.

        Args:
            report_column: dict (see ReportColumnSet)
            order_by: Current report order by
            order_dir: Current report order_dir

        Returns:
            string, HTML anchor

        """

        # Intentionally not using "if not report_column['order_dir']:" as
        # report_column['order_dir'] can take on values "None" and "0" (zero)
        # and they need to be distinguished.

        if report_column['order_dir'] == None:
            return SPAN(report_column['heading'])

        new_order_by = report_column['order_by']
        if order_by == report_column['order_by']:
            new_order_dir = int(not bool(int(order_dir)))
        else:
            new_order_dir = report_column['order_dir']

        request_vars = dict(self.request.vars)
        request_vars.update({'order_dir': new_order_dir,
            'order_by': new_order_by, 'page': 0})
        return A(report_column['heading'],
                 _class='results_column_header_link',
                 _href=URL(r=self.request, f=self.report_function,
                 args=self.request.args, vars=request_vars))

    def next_page_link(self, page, pages):
        """Return an HTML anchor representing a next page link.

        Args:
            page: integer, current page number
            pages: integer, total number of pages in report

        Returns:
            string, HTML anchor
        """

        if page >= pages - 1:
            return SPAN('next')
        else:
            request_vars = dict(self.request.vars)
            request_vars.update({'page': page + 1})
            return A('next', _class='page_link',
                     _href=URL(r=self.request, f=self.report_function,
                     args=self.request.args, vars=request_vars))

    def numeric_page_links(self, page, pages):
        """Return a list of HTML TD tags representing page links.

        Args:
            page: integer, current page number
            pages: integer, total number of pages in report

        Returns:
            list, List of HTML TD tags
        """

        links = []
        pagelists = PageList(pages, page)
        for page_list in pagelists.shown_sections:
            if len(links) > 0:
                links.append(TD(SPAN('...')))
            links = links + [TD(self.page_link(p, page)) for p in
                             page_list]
        return links

    def page_link(self, page_number, current_page):
        """Return an HTML anchor representing a page number link.

        Args:
            page_number: integer, link page number
            current_page: integer, current page number

        Returns:
            string, HTML anchor
        """

        if page_number == current_page:
            return SPAN(page_number + 1)
        else:
            request_vars = dict(self.request.vars)
            request_vars.update({'page': page_number})
            return A(page_number + 1, _class='page_link',
                     _href=URL(r=self.request, f=self.report_function,
                     args=self.request.args, vars=request_vars))

    def prev_page_link(self, page):
        """Return an HTML anchor representing a prev page link.

        Args:
            page: integer, current page number

        Returns:
            string, HTML anchor
        """

        if page == 0:
            return SPAN('prev')
        else:
            request_vars = dict(self.request.vars)
            request_vars.update({'page': page - 1})
            return A('prev', _class='page_link',
                     _href=URL(r=self.request, f=self.report_function,
                     args=self.request.args, vars=request_vars))

    def report(self, page_parameters=None):
        """Create report.

        Args:
            page_parameters: dict, Defines any of these page parameters
                { 'items_per_page': 30,
                  'order_by': 'id',
                  'order_dir': 0,
                  'page': 0,
                }

        Returns:
            dict, dictionary suitable for view template
        """

        # C0103: Invalid name "v"
        # R0912: Too many branches
        # R0914: Too many local variables
        # R0915: Too many statements
        # pylintx: disable=C0103,R0912,R0914,R0915

        results = ''
        page_links = ''
        pages = 0

        items_per_page_range = range(10, 110)

        # Page parameters come from three sources in order of precedence.
        # 1. request.vars, provided in url,
        #    eg table_list?order_by=town&order_dir=1
        # 2. page_parmeters, argument of this method
        # 3. defaults, hard coded below

        page_parameter_defaults = dict(items_per_page=30, order_by='id',
                order_dir=0, page=0)

        defaults = page_parameter_defaults
        if page_parameters:
            defaults.update(page_parameters)

        v = copy.copy(defaults)

        # Sanitize variables. Options from request.vars need sanitizing.
        # request vars are strings, convert to integer where possible.

        for (key, val) in self.request.vars.iteritems():

            if val.isdigit():
                v[key] = int(val)
            else:
                v[key] = val
        digits = ['items_per_page', 'page', 'order_dir']
        for key in digits:
            if not str(v[key]).isdigit():
                v[key] = defaults[key]
        if not v['items_per_page'] in items_per_page_range:
            v['items_per_page'] = defaults['items_per_page']
        if not v['order_by'] in [x['order_by'] for x in
                                 self.column_set.report_columns]:
            v['order_by'] = defaults['order_by']
        if v['order_dir'] != 0:
            v['order_dir'] = 1

        records = self.__len__()

        items_per_page = int(v['items_per_page'])

        # if records/items_per_page produces a fraction, add another page
        pages = int(records / items_per_page) + (records
                % items_per_page != 0) * 1

        v['page'] = 0 if v['page'] > pages else v['page']

        rows = self.rows(v['page'], items_per_page, v['order_by'],
                v['order_dir'])

        tr_rows = []
        ths = [TH(self.header_link(report_column, v['order_by'],
               v['order_dir']), _class='results_column_header')
               for report_column in self.column_set.sorted()]

        tr_rows.append(TR(ths))  # Header row

        if records > 0:
            for row in rows:
                tds = []
                for column in self.column_set.sorted():
                    formatted = ''
                    if callable(column['callback']):
                        formatted = column['callback'](row)
                    else:
                        # The next few lines get the value of the cell,
                        # ie. row/column. Examples:
                        # column.name           r
                        # 'client_id'           row['client_id']
                        # 'client.province'     row['client']['provnce']
                        # 'x.y.z'               row['x']['y']['z']
                        r = row
                        try:
                            for f in column['callback'].split('.'):
                                r = r[f]
                        except KeyError:
                            r = 'n/a'
                        formatted = r
                    if not str(formatted) or formatted == None:
                        formatted = column['empty'] or XML('&nbsp;')
                    column_class = 'results_table_cell col_{name}'.format(
                            name=column['order_by'].replace('.', '_'))
                    tds.append(TD(formatted,
                               _class=column_class,
                               ))
                tr_rows.append(TR(tds))
        else:
            tr_rows.append(TR([TD(SPAN('No records found.'),
                _colspan=len(self.column_set))]))

        results = DIV(TABLE(tr_rows, _class='results_table',
                      _id='results_table', _border='1'))

        page_links = DIV(HR(), TABLE(TR(TD(self.prev_page_link(v['page'
                         ])), self.numeric_page_links(v['page'],
                         pages), TD(self.next_page_link(v['page'],
                         pages))), _class='page_links_table'), HR())

        return dict(results=results, page_links=page_links, pages=pages)

    def rows(self, page, items_per_page, order_by, order_dir):
        """SQL rows for report.

        Args:
            page: integer, the number of the page whose rows are retrieved
            items_per_page: integer
            order_by: string, name of field to sort by
            order_dir: string, order direction

        Returns:
            gluon.sql.Rows instance
        """
        raise NotImplementedError

    def sql_query(self):
        """SQL query used to return results for report.

        Returns:
            gluon.sql.Query instance
        """
        raise NotImplementedError


class ReportColumnSet(object):
    """Class representing a set of ReportColumn objects, columns in a
    report.

    """
    def __init__(self, report_columns=None):
        """Constructor

        Args:
            report_columns: list, List of dicts representing report columns.
                [{'number': 1, ...},{'number': 2, ...},...]

            Example report_column
                report_column = {
                    'number': 1,
                    'heading': 'Clients',
                    'callback': self._format_id,
                    'order_by': 'client.last_name',
                    'order_dir': 0,
                    'empty': 'n/a',
                    }

            number: integer, column number used to determine location in table
                report. Columns count up left to right.
            heading: string, text to display as column heading

            callback: function to call to format value
            order_by: str, indicate the table.field to sort by if column header
                 is clicked eg 'table.field', if empty string, not a sortable
                 column.
            order_dir: 0, 1 or None, default sort direction,
                        0 => ascending
                        1 => descending
                        None => Not a sortable column
            empty: string, string to display if table cell is empty
                    Note: this element is optional.
        """

        self.report_columns = []
        if report_columns:
            self.report_columns = report_columns
        return

    def __len__(self):
        return len(self.report_columns)

    def add_columns(self, columns):
        """Add columns to the set

        Args:
            columns: list, List of tuples. Tuples are:
                ('heading', callback, order_by, order_dir)

        Notes:
            Column numbers are incremented.
            Columns are added in order.

        """
        # Get the current maximum column number.
        number = max([x['number'] for x in self.report_columns]) \
                if self.report_columns else 0

        for col in columns:
            number = number + 1
            report_column = {
                    'number': number,
                    'heading': col[0],
                    'callback': col[1],
                    'order_by': col[2],
                    'order_dir': col[3],
                    }
            report_column['empty'] = ''
            if len(col) == 6:
                report_column['empty'] = col[4]
            self.report_columns.append(report_column)

    def sorted(self):
        """Return the object's report_columns sorted.

        Returns:
            List, list of dicts

        """
        return sorted(self.report_columns, key=lambda column: \
                      column['number'])
