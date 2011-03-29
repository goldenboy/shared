#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/pagination.py

"""

from applications.shared.modules.local.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.pagination import Navigator, PageList, \
        Report, ReportColumnSet
from gluon.globals import Request
from gluon.html import DIV, TD
from BeautifulSoup import BeautifulSoup
import sys
import unittest

ROW_CLASSES = ['row_odd', 'row_even']

# C0111: Missing docstring
# R0904: Too many public methods
# pylint: disable=C0111,R0904


class TestNavigator(unittest.TestCase):

    def test____init__(self):
        nav = Navigator([])
        self.assertFalse(nav)

        pages = ['p1', 'p2', 'p3']
        nav = Navigator(pages)
        self.assertTrue(nav)

        # No page provided, defaults to first.
        self.assertEqual(nav.page, 'p1')

        # Invalid page provided, page gets set to first
        nav = Navigator(pages, 'pX')
        self.assertTrue(nav)
        self.assertEqual(nav.page, 'p1')

        # Valid page provided, page gets set
        nav = Navigator(pages, 'p2')
        self.assertEqual(nav.page, 'p2')

    def test____len__(self):
        nav = Navigator([])
        self.assertEqual(len(nav), 0)

        nav = Navigator(['p1'])
        self.assertEqual(len(nav), 1)

        nav = Navigator(['p1', 'p2'])
        self.assertEqual(len(nav), 2)

    def test_next(self):
        nav = Navigator([])
        self.assertEqual(nav.next(), '')

        pages = ['p1', 'p2', 'p3']
        nav = Navigator(pages)
        nav.page = ''
        self.assertEqual(nav.next(), 'p1')

        nav.page = 'p1'
        self.assertEqual(nav.next(), 'p2')
        nav.page = 'p2'
        self.assertEqual(nav.next(), 'p3')
        nav.page = 'p3'
        self.assertEqual(nav.next(), 'p3')

        nav.page = 'p1'
        self.assertEqual(nav.next(count=2), 'p3')

    def test_prev(self):
        nav = Navigator([])
        self.assertEqual(nav.prev(), '')

        pages = ['p1', 'p2', 'p3']
        nav = Navigator(pages)
        nav.page = ''
        self.assertEqual(nav.prev(), 'p1')

        nav.page = 'p3'
        self.assertEqual(nav.prev(), 'p2')
        nav.page = 'p2'
        self.assertEqual(nav.prev(), 'p1')
        nav.page = 'p1'
        self.assertEqual(nav.prev(), 'p1')

        nav.page = 'p3'
        self.assertEqual(nav.prev(count=2), 'p1')


class TestPageList(unittest.TestCase):

    def test____init__(self):
        page_list = PageList(pages=100, current_page=1)
        self.assertTrue(len(page_list.shown_sections) > 1)

    def test_shown(self):
        pages = 50
        tests = [{'label': 'left edge', 'current': 0, 'expect': [[
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            ], [47, 48, 49]]}, {'label': 'middle', 'current': 25,
                                'expect': [[0, 1, 2], [
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            ], [47, 48, 49]]}, {'label': 'right edge', 'current': 49,
                                'expect': [[0, 1, 2], [
            41,
            42,
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            ]]}]

        for test in tests:
            page_list = PageList(pages, current_page=test['current'])
            self.assertEqual(page_list.shown(), test['expect'])
        return

    def test_is_shown(self):

        # rules:
        # left and right edge have a minimum 3
        # left edge: if current page <= 9, and i <= 9 show
        # right edge: if current page > pages - 9 and i >= pages - 9 show
        # middle: if abs(current page - i ) <= 9/2 show

        # If the number of pages is 9 or less, then all page numbers are shown
        # regardless of the current page

        pages = 9
        expect_true = [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            ]

        for current_page in range(-2, pages + 2):
            page_list = PageList(pages, current_page)
            shown_true = []

            # The range intentionally extends prior and beyond normal page
            # numbers.

            for page in range(-2, pages + 2):
                if page_list.is_shown(page):
                    shown_true.append(page)
            self.assertEqual(expect_true, shown_true)

        # Ensure the left edge is always 3 or more
        # Ensure the right edge is always 3 or more

        pages = 50
        left_edge = [0, 1, 2]
        right_edge = [47, 48, 49]

        for current_page in range(-2, pages + 2):
            page_list = PageList(pages, current_page)
            shown_true = []

            # The range intentionally extends prior and beyond normal page
            # numbers.

            for page in range(-2, pages + 2):
                if page_list.is_shown(page):
                    shown_true.append(page)

            min_len = page_list.min_edge + page_list.surround
            self.assertEqual(left_edge, shown_true[0:3])
            self.assertEqual(right_edge, shown_true[-3:])
            self.assertTrue(len(shown_true) >= min_len)

        # Ensure the surround is always at least 9.

        pages = 50
        for current_page in range(-2, pages + 2):
            page_list = PageList(pages, current_page)
            shown_true = []

            # The range intentionally extends prior and beyond normal page
            # numbers.

            for page in range(-2, pages + 2):
                if page_list.is_shown(page):
                    shown_true.append(page)
            start = current_page - 1 - page_list.surround / 2
            if start < 0:
                start = 0
            end = current_page + page_list.surround / 2
            if end >= pages:
                end = page - 1
            surround_range = range(start, end)
            self.assertTrue(set(surround_range).issubset(set(shown_true)))
        return


class ReportTest(Report):
    """Class sub-classing Report used for testing."""

    def __init__(self, request, report_function, sqldb=None, columns=None,
            row_classes=None):
        Report.__init__(self, request, report_function, sqldb, columns,
                row_classes)

    def rows(self, page, items_per_page, order_by, order_dir):
        order_by = 'id' if not order_by else order_by
        data = sim_data()
        reverse = True if order_dir else False
        ordered = sorted(data, key=lambda x: x[order_by], reverse=reverse)
        start = page * items_per_page
        end = start + items_per_page
        return ordered[start:end]

    def sql_query(self):
        pass


class TestReport(unittest.TestCase):

    def test____init__(self):
        try:
            report = Report()
        except TypeError:
            pass
        else:
            self.fail('No parameters should fail')

        report = ReportTest(sim_request(), 'some_function', None,
                sim_columns())
        self.assertTrue(report)

    def test__format_delimited_list(self):
        report = sim_report()
        row = {'a': 'A', 'b': 'B', 'c': 'C'}

        # (fields, sep, expect)
        tests = [
            (['b'],             None,  'B'),
            (['b', 'c'],        None,  'BC'),
            (['b', 'c', 'a'],   None,  'BCA'),
            (['b'],             ' ',   'B'),
            (['b', 'c'],        ' ',   'B C'),
            (['b', 'c', 'a'],   ' ',   'B C A'),
            (['b'],             ', ',  'B'),
            (['b', 'c'],        ', ',  'B, C'),
            (['b', 'c', 'a'],   ', ',  'B, C, A'),
            (['b'],             ' - ', 'B'),
            (['b', 'c'],        ' - ', 'B - C'),
            (['b', 'c', 'a'],   ' - ', 'B - C - A'),
            ]
        for t in tests:
            if t[1] != None:
                self.assertEqual(report.format_delimited_list(row, t[0], t[1]),
                        t[2])
            else:
                self.assertEqual(report.format_delimited_list(row, t[0]), t[2])

    def test__header_link(self):
        report = sim_report()
        header = report.header_link(report.column_set.report_columns[1],
                'name', 1)
        # Example link:
        # <a class="results_column_header_link"
        # href="/app/cont/some_function?order_by=name&order_dir=0&page=0">Name
        # </a>
        soup = as_soup(header)
        self.assertEqual(soup.find('a').string, 'Name')
        self.assertEqual(soup.find('a')['href'],
                '/app/cont/some_function?order_by=name&order_dir=0&page=0')

    def test__next_page_link(self):
        report = sim_report()
        page = 2
        pages = 10
        next_link = report.next_page_link(page, pages)
        # Example link:
        # <a class="page_link" href="/app/cont/some_function?page=3"> next</a>
        soup = as_soup(next_link)
        self.assertEqual(soup.find('a').string, 'next')
        self.assertEqual(soup.find('a')['href'],
                '/app/cont/some_function?page={pg}'.format(pg=str(page + 1)))

        # Test where page is last page.
        page = pages - 1
        next_link = report.next_page_link(page, pages)
        # Example link:
        # <span>next</span>
        soup = as_soup(next_link)
        self.assertEqual(soup.find('span').string, 'next')

    def test__numeric_page_links(self):
        report = sim_report()
        page = 2
        pages = 5
        links = report.numeric_page_links(page, pages)
        self.assertEqual(len(links), pages)
        for l in links:
            self.assertTrue(isinstance(l, TD))

    def test__page_link(self):
        report = sim_report()
        page_number = 5
        page = 1
        page_link = report.page_link(page_number, page)
        # Example link:
        # <a class="page_link" href="/app/cont/some_function?page=5">6</a>
        soup = as_soup(page_link)
        self.assertEqual(soup.find('a').string, str(page_number + 1))
        self.assertEqual(soup.find('a')['href'],
                '/app/cont/some_function?page={pg}'.format(pg=page_number))

        # Test where the page number is the current page
        page = page_number
        page_link = report.page_link(page_number, page)
        # Example link:
        # <span>6</span>
        soup = as_soup(page_link)
        self.assertEqual(soup.find('span').string, str(page_number + 1))

    def test__prev_page_link(self):
        report = sim_report()
        page = 3
        prev_link = report.prev_page_link(page)
        # Example link:
        # <a class="page_link" href="/app/cont/some_function?page=2"> prev</a>
        soup = as_soup(prev_link)
        self.assertEqual(soup.find('a').string, 'prev')
        self.assertEqual(soup.find('a')['href'],
                '/app/cont/some_function?page={pg}'.format(pg=str(page - 1)))

        # Test where page is first page.
        page = 0
        prev_link = report.prev_page_link(page)
        # Example link:
        # <span>prev</span>
        soup = as_soup(prev_link)
        self.assertEqual(soup.find('span').string, 'prev')

    def test__report(self):
        report = sim_report().report()

        # The report() method is quite complex. Just test that results are
        # returns and are as expected.
        self.assertTrue('page_links' in report and isinstance(
            report['page_links'], DIV))
        self.assertTrue('results' in report and isinstance(
            report['results'], DIV))
        soup = as_soup(report['results'])

        # Verify th headers
        expect_headers = [x[0] for x in sim_columns()]
        got_headers = [x.a.string for x in soup.findAll('th')]
        self.assertEqual(sorted(got_headers), sorted(expect_headers))

        # Verify tr/td data
        data = sim_data()
        got_trs = soup.findAll('tr')[1:]        # Ignore header row
        got_tds = [x.findAll('td') for x in got_trs]
        got_ids = [int(x[0].string) for x in got_tds]
        expect_ids = [x['id'] for x in data]
        self.assertEqual(got_ids, expect_ids)

        got_names = [x[1].string for x in got_tds]
        expect_names = [x['name'] for x in data]
        self.assertEqual(got_names, expect_names)

        # Verify tr classes
        self.assertEqual(got_trs[0]['class'], ROW_CLASSES[0])
        self.assertEqual(got_trs[1]['class'], ROW_CLASSES[1])
        self.assertEqual(got_trs[2]['class'], ROW_CLASSES[0])

        # Verify pages
        self.assertTrue('pages' in report and report['pages'] == 1)

    def test__rows(self):
        report = Report(sim_request(), 'some_function', None,
                sim_columns())
        try:
            report.rows(0, 9999999, '', 0)
        except NotImplementedError:
            pass
        else:
            self.fail('NotImplementedError not raised.')

    def test__sql_query(self):
        report = Report(sim_request(), 'some_function', None,
                sim_columns())
        try:
            report.sql_query()
        except NotImplementedError:
            pass
        else:
            self.fail('NotImplementedError not raised.')


class TestReportColumnSet(unittest.TestCase):

    def test____init__(self):
        column_set = ReportColumnSet()
        # Because ReportColumnSet has a __len__ method, the truth of an
        # instance is determined by the result of that method.
        self.assertFalse(column_set)
        self.assertEqual(column_set.report_columns, [])
        columns = ['a', 'b']
        column_set = ReportColumnSet(columns)
        self.assertEqual(column_set.report_columns, columns)
        self.assertTrue(column_set)

    def test____len__(self):
        column_set = ReportColumnSet()
        self.assertEqual(len(column_set), 0)
        columns = ['a', 'b']
        column_set = ReportColumnSet(columns)
        self.assertEqual(len(column_set), 2)

    def test__add_columns(self):
        column_set = ReportColumnSet()
        self.assertEqual(len(column_set), 0)
        column_set.add_columns(sim_columns())
        self.assertEqual(len(column_set), 2)
        for x in column_set.report_columns:
            self.assertTrue(isinstance(x, dict))
        self.assertEqual(column_set.report_columns[0]['number'], 1)
        self.assertEqual(column_set.report_columns[1]['number'], 2)
        # Additional columns can be added, the number fields should be set
        # properly.
        column_set.add_columns(sim_columns())
        self.assertEqual(len(column_set), 4)
        self.assertEqual(column_set.report_columns[2]['number'], 3)
        self.assertEqual(column_set.report_columns[3]['number'], 4)

    def test__sorted(self):
        column_set = ReportColumnSet()
        self.assertEqual(column_set.sorted(), [])
        column_set.add_columns(sim_columns())
        sorted_set = column_set.sorted()
        self.assertEqual(sorted_set[0]['heading'], 'ID')
        self.assertEqual(sorted_set[1]['heading'], 'Name')
        # Reverse the numbers
        column_set.report_columns[0]['number'] = 2
        column_set.report_columns[1]['number'] = 1
        sorted_set = column_set.sorted()
        self.assertEqual(sorted_set[0]['heading'], 'Name')
        self.assertEqual(sorted_set[1]['heading'], 'ID')


def sim_columns():
    return [
        ('ID',   'id', 'id',     0),
        ('Name', 'name', 'name', 0),
        ]


def sim_columns2():
    return [
        ('ID',   'table1.id', 'table1.id',     0),
        ('Name', 'table2.name', 'table2.name', 0),
        ]


def sim_data():
    """Return test data."""
    data = []
    alpha = 'abcdefghijklmnopqrstuvwxyz'
    for i, x in enumerate(alpha):
        data.append({'id': i,
            'name': ''.join([x for _ in range(0, 6)]).title()})
    return data


def sim_data2():
    """Return test data."""
    data = []
    alpha = 'abcdefghijklmnopqrstuvwxyz'
    for i, x in enumerate(alpha):
        data.append({
           'table1': {'id': i},
           'table2': {'name': ''.join([x for _ in range(0, 6)]).title()},
           })
    return data


def sim_request():
    """Return test request."""
    request = Request()
    request.application = 'app'
    request.controller = 'cont'
    request.function = 'func'
    return request


def sim_report():
    return ReportTest(sim_request(), 'some_function', None, sim_columns(),
            ROW_CLASSES)


def as_soup(html):
    html = """
    <html>
    <body>
    {html}
    </body>
    </html>
    """.format(html=html)
    return BeautifulSoup(html, smartQuotesTo=None, convertEntities='xml')


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
