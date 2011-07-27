#!/usr/bin/python

"""
test_runner.py

Classes for local python test_suite scripts.

"""
from optparse import OptionParser
import datetime
import inspect
import os
import re
import subprocess
import sys
import time
import unittest

from applications.shared.modules.testing import FileSet


# Decorator
def count_diff(func):
    """Decorator used to display the effect of a function on mysql record
    counts.

    """
    def wrapper(*arg):
        """Decorator wrapper function

        Args:
            arg: args passed to decorated function.
        """

        tmp_dir = '/tmp/mysql_count'
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        bef = open(os.path.join(tmp_dir, 'before.txt'), "w")
        aft = open(os.path.join(tmp_dir, 'after.txt'), "w")
        subprocess.call(["/root/bin/mysql_record_count.sh"], stdout=bef,
                shell=True)
        func(*arg)
        subprocess.call(["/root/bin/mysql_record_count.sh"], stdout=aft,
                shell=True)
        subprocess.call(["diff", "/tmp/mysql_count/before.txt",
                "/tmp/mysql_count/after.txt"])
        return
    return wrapper


class _MyTextTestResult(unittest._TextTestResult):
    """A test result class that can print formatted text results to streams.
    Differs from unittest._TextTestResult
    * use distinct streams for errors and general output
    * Replace the "dots" mode with a showErr mode, prints only errors

    Used by TextTestRunner.
    """

    # Many varibles are copied as is from unittest code.
    # pylint: disable=C0103
    # pylint: disable=W0212
    # pylint: disable=W0231
    # pylint: disable=W0233

    separator1 = '=' * 70
    separator2 = '-' * 70

    def __init__(self, stream, stream_err, descriptions, verbosity):
        """Constructor."""
        unittest.TestResult.__init__(self)
        self.stream = stream
        self.stream_err = stream_err
        self.showAll = verbosity > 1
        self.showErr = verbosity == 1
        self.descriptions = descriptions

    def startTest(self, test):
        """Adapted from unittest._TextTestResult. Method called just prior to
        test run
        """
        self.testsRun = self.testsRun + 1

    def addSuccess(self, test):
        """Adapted from unittest._TextTestResult"""
        unittest.TestResult.addSuccess(self, test)
        stream = None
        if self.showAll:
            stream = self.stream
        if stream:
            stream.write(self.getDescription(test))
            stream.write(" ... ")
            stream.writeln("ok")
            stream.flush()

    def addError(self, test, err):
        """Adapted from unittest._TextTestResult"""
        unittest.TestResult.addError(self, test, err)
        stream = None
        if self.showErr:
            stream = self.stream_err
        elif self.showAll:
            stream = self.stream
        if stream:
            stream.write(self.getDescription(test))
            stream.write(" ... ")
            stream.writeln("ERROR")
            stream.flush()

    def addFailure(self, test, err):
        """Adapted from unittest._TextTestResult"""
        unittest.TestResult.addFailure(self, test, err)
        if self.showErr:
            stream = self.stream_err
        elif self.showAll:
            stream = self.stream
        if stream:
            stream.write(self.getDescription(test))
            stream.write(" ... ")
            stream.writeln("FAIL")
            stream.flush()

    def printErrors(self):
        """Adapted from unittest._TextTestResult"""
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)

    def printErrorList(self, flavour, errors):
        """Adapted from unittest._TextTestResult"""
        for test, err in errors:
            self.stream_err.writeln(self.separator1)
            self.stream_err.writeln("%s: %s" % (flavour,
                self.getDescription(test)))
            self.stream_err.writeln(self.separator2)
            self.stream_err.writeln("%s" % err)


class MyTextTestRunner(unittest.TextTestRunner):
    """A test runner class that displays results in textual form.

    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    """
    # Many varibles are copied as is from unittest code.
    # pylint: disable=C0103
    # pylint: disable=C0321
    # pylint: disable=R0903
    # pylint: disable=W0141
    # pylint: disable=W0212
    # pylint: disable=W0231

    def __init__(self, stream=sys.stdout, stream_err=sys.stderr,
            descriptions=1, verbosity=1):
        """Constructor."""
        self.stream = unittest.runner._WritelnDecorator(stream)
        self.stream_err = unittest.runner._WritelnDecorator(stream_err)
        self.descriptions = descriptions
        self.verbosity = verbosity

    def _makeResult(self):
        """Format test results"""
        return _MyTextTestResult(self.stream, self.stream_err,
                self.descriptions, self.verbosity)

    def run(self, test):
        """Run the given test case or test suite."""
        result = self._makeResult()
        startTime = time.time()
        test(result)
        stopTime = time.time()
        timeTaken = stopTime - startTime
        run = result.testsRun
        if self.verbosity > 1:
            self.stream.writeln(result.separator2)
            self.stream.writeln("Ran %d test%s in %.3fs" %
                                (run, run != 1 and "s" or "", timeTaken))
            if result.wasSuccessful():
                self.stream.writeln()

        if not result.wasSuccessful():
            self.stream.writeln()
            result.printErrors()
            self.stream_err.write("FAILED (")
            failed, errored = map(len, (result.failures, result.errors))
            if failed:
                self.stream_err.write("failures=%d" % failed)
            if errored:
                if failed:
                    self.stream_err.write(", ")
                self.stream_err.write("errors=%d" % errored)
            self.stream_err.writeln(")")
        else:
            if self.verbosity > 1:
                self.stream.writeln("OK")
        return result


class LocalTestSuite(object):
    """Class to represent tests local to the test module."""

    def __init__(self):
        """Constructor."""
        self.suite = unittest.TestSuite()
        self.options = None
        return

    def add_tests(self, test_suite_object):
        """Add tests to suite"""
        self.options = test_suite_object.options
        self.suite.addTests(test_suite_object.suite)

    @count_diff
    def run_tests(self):
        """Run tests in suite"""
        verbosity = 1
        if self.options and self.options.verbose:
            verbosity = 2
        MyTextTestRunner(verbosity=verbosity).run(self.suite)


class ModuleTestSuite(object):
    """Base class for Test_Suite objects in test modules."""

    # pylint: disable=R0903

    def __init__(self, module=None):
        """Constructor. Define the test suite"""
        self.module = module
        self.options = None
        self.args = []
        self.set_parser()
        self.objects = self._test_class_objects()
        self.tests = []
        if self.options and self.options.test:
            self.tests.append(self.options.test)
        if not self.tests:
            self.tests = self.objects.keys()
        if self.options and self.options.list:
            for test in sorted(self.objects.keys()):
                print test
            quit()

        self.invalid_test_names = self._invalid_test_names()

        if self.invalid_test_names:
            for test in self.invalid_test_names:
                print "Invalid test name: %s" % test
            print "Use --list option to display valid test names."
            quit()

        self.suite = self._suite()
        return

    def _invalid_test_names(self):
        """Method to extract invalid tests from in list of tests

        Returns:
            list, list of names of invalid tests.
        """
        invalids = []
        for test in self.tests:
            if not test in self.objects.keys():
                invalids.append(test)
        return invalids

    def _suite(self):
        """Create a unittest.TestSuite(suites) from the module tests.

        Returns:
            unittest.TestSuite(suites)
        """
        suites = []
        for test in sorted(self.tests):
            if not test in self.invalid_test_names:
                self.objects[test].mock_date = _mock_date
                self.objects[test].mock_datetime = _mock_datetime
                suites.append(
                        unittest.TestLoader().loadTestsFromTestCase(
                            self.objects[test]
                            )
                        )
        return unittest.TestSuite(suites)

    def _test_class_objects(self):
        """Obtain all class objects that are Tests.

        Test class objects have names beginning with "Test"

        Returns
            list, list of class objects.
        """
        re_test = re.compile(r'Test(.*)')
        objects = {}
        # Get all members of the module
        for unused_name, obj in inspect.getmembers(self.module):
            # Look for class definitions with name "Test*"
            if inspect.isclass(obj):
                if obj.__module__ == self.module.__name__:
                    match = re_test.match(obj.__name__)
                    if match:
                        objects[match.group(1)] = obj
        return objects

    def set_parser(self):
        """Create the OptionParser for the tests"""
        parser = OptionParser()

        parser.add_option('-t', '--test', type='str', dest='test',
                          help="name of test to run", metavar="TEST")
        parser.add_option("-l", "--list",
                         action="store_true", dest="list", default=False,
                         help="print list of test names")
        parser.add_option("-v", "--verbose",
                         action="store_true", dest="verbose", default=False,
                         help="print messages to stdout")
        (options, args) = parser.parse_args()
        self.options = options
        self.args = args
        return


def has_terminal():
    """Return True if the script is run in a terminal environment"""

    if 'PS1' in os.environ:
        return True
    return False


def _mock_date(self, today_value=None):
    """Function used to override the datetime.date function in tests."""
    # pylint: disable=W0613
    class MockDate(datetime.date):
        """Class representing mock date"""
        @classmethod
        def today(cls):
            """Function to override datatime.date.today()"""
            return today_value
    return MockDate


def _mock_datetime(self, now_value=None):
    """Function used to override the datetime.datetime function in tests."""
    # pylint: disable=W0613
    class MockDatetime(datetime.datetime):
        """Class representing mock datetime"""
        @classmethod
        def now(cls):
            """Function to override datatime.datetime.now()"""
            return now_value
    return MockDatetime


def main():

    """
    Run all test modules in test directories
    """
    usage = "%prog [options] path/to/web2py [app... ] [test_file.py...]"

    parser = OptionParser(usage=usage)

    parser.add_option("-v", "--verbose",
                     action="store_true", dest="verbose", default=False,
                     help="print messages to stdout")

    (options, args) = parser.parse_args()

    if len(args) < 1:
        print >> sys.stderr, \
            'Please provide the path to the project web2py directory.'
        print >> sys.stderr, 'Example: /srv/http/example.com/web2py'
        parser.print_help()
        exit(1)

    project_path = args.pop(0)
    if not os.path.exists(project_path):
        print >> sys.stderr, \
            'Invalid project. Directory does not exist: {path}'.format(
                    path=project_path)
        exit(1)

    testset = FileSet(project_path, want=args)
    modules = testset.relative_modules()

    suite = LocalTestSuite()
    for module in sorted(modules):
        if options.verbose:
            print "Adding to test suite, module: %s" % (module)
        # The next code is the equivalent of:
        #   import applications.imdb.tests.test_page
        #   page_suite =
        #       ModuleTestSuite(module=applications.imdb.tests.test_page)
        #   suite.add_tests(page_suite)
        __import__(module)
        suite.add_tests(ModuleTestSuite(module=sys.modules[module]))
    suite.run_tests()

if __name__ == '__main__':
    main()
