#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Classes used for automating testing with test_*.py scripts.

"""

import os
import re


class File(object):

    """Class representing a testing script file."""

    def __init__(self, filename, root_path):
        """Constructor.

        Args:
            filename: fully pathed name of test script
            root_path: web2py root path

        """

        self.filename = filename
        self.root_path = root_path
        self.application = ''
        self.sub_directory = ''
        self.module = ''
        return

    def __cmp__(self, other):
        return cmp(str(self), str(other))

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def __repr__(self):
        return self.filename

    def import_line(self):
        """Return a line of code appropriate for importing module
        classes into the test script.

        Returns:
            str, line of code, the code that imports from the module
        """

        module_obj = self.module_object()
        fmt = 'from applications.{app}.modules.{module} import'
        if self.sub_directory:
            fmt = \
                'from applications.{app}.modules.{subdir}.{module} import'
        line = fmt.format(app=self.application,
                          subdir=self.sub_directory, module=self.module)
        words = []
        for module_class in module_obj.classes():
            words.append(module_class)
        imp_line = ' '.join((line, ', '.join(sorted(words))))
        return imp_line

    def module_object(self):
        """Get Module object instance of object associated with this
        test script.

        Returns:
            Module object instance

        """

        return Module(self.module_file(), self.root_path)

    def module_file(self):
        """Determine the name of the module file associated with the
        test script.

        Returns:
            str, fully pathed name of module file.
        """

        if not self.module:
            return ''
        filename = ''
        fmt = 'applications/{app}/modules/{module}.py'
        if self.sub_directory:
            fmt = 'applications/{app}/modules/{subdir}/{module}.py'
        filename = os.path.join(self.root_path,
                                fmt.format(app=self.application,
                                subdir=self.sub_directory,
                                module=self.module))
        return filename

    def parse(self):
        """Convert filename into it's components: application name,
        subdirectory name (optional) module name.

        Example:
        /path/to/project/web2py/applications/shared/tests/html/table_crud.py
        application = shared
        sub_directory = html
        module_name = table_crud
        """
        re_app = \
            re.compile(r"""
            .*/
            applications/
            (?P<app>.*?)
            /tests/
            (?:(?P<subdir>.*)/)?
            (?P<script>.*)
            """, re.VERBOSE)
        re_module = re.compile(r'test_(?P<module>.*).py')
        app_match = re_app.search(self.filename)
        if app_match:
            self.application = app_match.group('app')
            if app_match.group('subdir'):
                self.sub_directory = app_match.group('subdir')
            test_script = app_match.group('script')
            module_match = re_module.match(test_script)
            if module_match:
                self.module = module_match.group('module')
        return

    def relative_module(self):
        """Create the relative module string for the test script.

        Example
        test script:
        /path/to/project/web2py/applications/shared/tests/html/table_crud.py
        relative_module: applications.shared.modules.tests.html.table_crud

        Returns:
            str, string representing the relative module

        """

        # Remove .py extension

        (without_ext, unused_ext) = os.path.splitext(self.filename)

        # Remove leading root path
        # Replace '/' with '.'
        # Strip leading '.'

        module = re.compile(r'^\.').sub('', re.sub('/', '.',
                re.sub(self.root_path, '', without_ext)))
        return module


class FileSet(object):

    """Class representing a set of testing script files, eg test_aaaa.py."""

    def __init__(self, root_path, want=None):
        """Constructor

        Args:
            root_path: string, the web2py root path
            want: list of application and test file names to include in
                set, eg ['app1', 'test_module.py']

        Notes:
            Test files for all applications are included in set.
        """

        self.root_path = root_path
        self.want = want
        self.apps_path = os.path.join(self.root_path, 'applications')

        re_file = re.compile(r'test_.*\.py')
        want_apps = []
        want_files = []
        if self.want:
            for item in self.want:
                if re_file.match(item):
                    want_files.append(item)
                else:
                    want_apps.append(item)
        self.want_apps = sorted(want_apps)
        self.want_files = sorted(want_files)
        return

    def all_test_files(self):
        """Get File object instances representing all files of format
        test_xxxx.py within test directories

        Returns:
            list, list of File objects
        """

        test_files = []
        test_dirs = self.test_directories()
        re_test = re.compile(r'^test_.*.py$')
        for test_path in test_dirs:
            for (root, unused_dirs, files) in os.walk(test_path):
                for filename in files:

                    # Ignore any file not formatted like a test file

                    match = re_test.match(filename)
                    if match:
                        test_file = File(os.path.join(root, filename),
                                self.root_path)
                        test_files.append(test_file)
        return sorted(test_files)

    def relative_modules(self):
        """Get relative module names for the files wanted for testing.

        Example:
            filename:
                /path/to/project/web2py/applications/imdb/tests/test_page.py
            relative module:
                applications.imdb.tests.test_page
        Return:
            list, list of relative module names
        """

        modules = []
        for test_file in self.want_test_files():
            modules.append(test_file.relative_module())
        return sorted(modules)

    def test_directories(self):
        """Get tests directories for all applications

        Example: /path/to/project/web2py/applications/imdb/tests

        Returns:
            list, list of path names
        """

        test_dirs = []
        for app_dir in os.listdir(self.apps_path):
            tests_dir = os.path.join(self.apps_path, app_dir, 'tests')
            if os.path.exists(tests_dir) and os.path.isdir(tests_dir):
                test_dirs.append(tests_dir)
        return sorted(test_dirs)

    def want_test_files(self):
        """Get File object instances representing files wanted for
        testing.

        Returns:
            list, list of File objects
        """

        want_files = []
        test_files = self.all_test_files()
        for test_file in test_files:
            test_file.parse()

        if self.want_apps:
            for want_app in self.want_apps:
                for test_file in test_files:
                    if want_app == test_file.application:
                        want_files.append(test_file)
        if self.want_files:
            for want_file in self.want_files:
                for test_file in test_files:
                    if want_file \
                        == os.path.basename(test_file.filename):
                        want_files.append(test_file)

        if not self.want_apps and not self.want_files:
            want_files = test_files
        return sorted(want_files)


class Module(object):

    """Class representing a module a testing script tests."""

    def __init__(self, filename, root_path):
        """Constructor.

        Args:
            filename: fully pathed name of test script
            root_path: web2py root path

        """

        self.filename = filename
        self.root_path = root_path
        self.application = ''
        self.sub_directory = ''
        self.module = ''
        return

    def __cmp__(self, other):
        return cmp(str(self), str(other))

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def __repr__(self):
        return self.filename

    def classes(self):
        """Get a list of class object names from the module file

        Returns:
            list, list of class names.

        """

        module_classes = []
        lines = []
        with open(self.filename, 'r') as f_module:
            lines = f_module.readlines()
        re_class = re.compile(r'class (?P<class>.*?)\(')
        for line in lines:
            class_match = re_class.match(line)
            if class_match:
                module_classes.append(class_match.group('class'))
        return module_classes

    def import_all_line(self):
        """Return the string of code representing the import all line.

        Returns:
            str, the import all line of code
        """

        module = self.relative_module()
        invalid = 'from {module} import *'.format(module=module)
        return invalid

    def parse(self):
        """Convert filename into it's components: application name,
        subdirectory name (optional) module name.

        Example:
        /path/to/project/web2py/applications/shared/modules/html/table_crud.py

            application = shared
            sub_directory = db
            module_name = table
        """

        re_app = \
            re.compile(r"""
            .*/
            applications/
            (?P<app>.*?)
            /modules/
            (?:(?P<subdir>.*)/)?
            (?P<script>.*)
            """, re.VERBOSE)
        re_module = re.compile(r'(?P<module>.*).py')
        app_match = re_app.search(self.filename)
        if app_match:
            self.application = app_match.group('app')
            if app_match.group('subdir'):
                self.sub_directory = app_match.group('subdir')
            test_script = app_match.group('script')
            module_match = re_module.match(test_script)
            if module_match:
                self.module = module_match.group('module')
        return

    def relative_module(self):
        """Create the relative module string for a module

        Example
        filename:
        /path/to/project/web2py/applications/shared/modules/html/table_crud.py
        relative_module: applications.shared.modules.html.table_crud

        Returns:
            str, string representing the relative module

        """

        # Remove .py extension

        (without_ext, unused_ext) = os.path.splitext(self.filename)

        # Remove leading root path
        # Replace '/' with '.'
        # Strip leading '.'

        module = re.compile(r'^\.').sub('', re.sub('/', '.',
                re.sub(self.root_path, '', without_ext)))
        return module


def generic_table_ref_tests(
        unittest_obj,
        main_class,
        main_table,
        main_field,
        ref_class,
        ref_table,
        method_name):
    """Generic unit tests for a method that returns an object instance
    associated with the referenced record.

    Args:
        unittest_obj: unittest.TestCase instance
        main_class: class of main table
        main_table: gluon.dal.Table instance of main table
        main_field: string, name of the main field
        ref_class: class of referenced table
        ref_table: gluon.dal.Table instance of reference table
        method_name: name of method tested.

    Example
        main table
            album
                id
                artist_id

        referenced table
            artist
                id
                name

    Test a Album.artist() method that returns an Artist object instance
    associated with the album.

        test__artist(self):
            generic_table_ref_test(self, Album, DB.album, 'artist_id', Artist,
                DB.artist, 'artist')
    """
    # No record
    main_obj = main_class(main_table)
    unittest_obj.assertFalse(getattr(main_obj, method_name)())

    main_obj = main_class(main_table).add()
    # No associated reffed record
    unittest_obj.assertFalse(getattr(main_obj, method_name)())

    ref_obj = ref_class(ref_table).add()
    # Reffed instance not associated with main_obj
    unittest_obj.assertFalse(getattr(main_obj, method_name)())

    # Id doesn't match
    setattr(main_obj, main_field, -1)
    unittest_obj.assertTrue(main_obj.update())
    unittest_obj.assertFalse(getattr(main_obj, method_name)())

    # Match
    setattr(main_obj, main_field, ref_obj.id)
    unittest_obj.assertTrue(main_obj.update())
    o = getattr(main_obj, method_name)()
    # Returns correct object type
    unittest_obj.assertTrue(isinstance(o, ref_class))
    # Returns correct instance
    unittest_obj.assertEqual(o.id, ref_obj.id)

    # Cleanup
    ref_obj.remove()
    main_obj.remove()
