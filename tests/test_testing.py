#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Test suite for shared/modules/mysql.py

"""

from applications.shared.modules.local.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.testing import File, FileSet, Module
import os
import sys
import unittest

# pylint: disable=C0111


def root_path():
    return '/tmp/test_testing'


def create_test_data():
    root = root_path()

    stubs = [
        'applications/app1/tests/test_module_a.py',
        'applications/app1/modules/module_a.py',
        'applications/app1/tests/test_module_b.py',
        'applications/app1/modules/module_b.py',
        'applications/app1/tests/non_test_script.py',
        'applications/app2/tests/test_module_c.py',
        'applications/app2/modules/module_c.py',
        'applications/app2/tests/adir/test_module_d.py',
        'applications/app2/modules/adir/module_d.py',
        ]

    files = [os.path.join(root, x) for x in stubs]

    text_a = \
        """
from applications.app1.modules.module_a import *

class ClassA(object):
    def __init__(self):
        \"""docstring for __init__\"""
        return

class ClassAA(object):
    def __init__(self):
        \"""docstring for __init__\"""
        return
"""

    text_b = \
        """
from applications.app1.modules.module_b import *

class ClassB(object):
    def __init__(self):
        \"""docstring for __init__\"""
        return
"""
    text_c = \
        """
from applications.app2.modules.module_c import *

class ClassC(object):
    def __init__(self):
        \"""docstring for __init__\"""
        return
"""

    text_d = \
        """
from applications.app2.modules.adir.module_d import *

class ClassD(object):
    def __init__(self):
        \"""docstring for __init__\"""
        return
"""

    module_to_text = {
        'module_a.py': text_a,
        'module_b.py': text_b,
        'module_c.py': text_c,
        'module_d.py': text_d,
        }

    for test_file in files:
        base_name = os.path.basename(test_file)
        dir_name = os.path.dirname(test_file)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        open(test_file, 'w').close()
        if base_name in module_to_text:
            test_file_h = open(test_file, 'w')
            test_file_h.write(module_to_text[base_name])
            test_file_h.close()
    return


create_test_data()


class TestFile(unittest.TestCase):

    def test____init__(self):
        filename = os.path.join(root_path(),
                                'applications/app1/tests/test_module_a.py'
                                )
        test_file = File(filename, root_path())
        self.assertTrue(test_file)  # Creates object
        return

    def test____cmp__(self):
        filename = os.path.join(root_path(),
                                'applications/app1/tests/test_module_a.py'
                                )
        test_file = File(filename, root_path())
        filename2 = os.path.join(root_path(),
                                 'applications/app1/tests/test_module_b.py'
                                 )
        test_file2 = File(filename2, root_path())
        self.assertEqual(cmp(test_file, test_file2), -1)
        self.assertEqual(cmp(test_file, test_file), 0)
        self.assertEqual(cmp(test_file2, test_file), 1)
        self.assertEqual(sorted([test_file, test_file2]), [test_file,
                         test_file2])
        self.assertEqual(sorted([test_file, test_file2], reverse=True),
                         [test_file2, test_file])
        return

    def test____eq__(self):
        filename = os.path.join(root_path(),
                                'applications/app1/tests/test_module_a.py'
                                )
        test_file = File(filename, root_path())
        test_file2 = File(filename, root_path())
        self.assertEqual(test_file, test_file2)
        return

    def test____ne__(self):
        filename = os.path.join(root_path(),
                                'applications/app1/tests/test_module_a.py'
                                )
        test_file = File(filename, root_path())
        filename2 = os.path.join(root_path(),
                                 'applications/app1/tests/test_module_b.py'
                                 )
        test_file2 = File(filename2, root_path())
        self.assertNotEqual(test_file, test_file2)
        return

    def test____repr__(self):
        filename = os.path.join(root_path(),
                                'applications/app1/tests/test_module_a.py'
                                )
        test_file = File(filename, root_path())
        self.assertEqual(str(test_file), filename)
        return

    def test__import_line(self):
        filename = os.path.join(root_path(),
                                'applications/app1/tests/test_module_a.py'
                                )
        test_file = File(filename, root_path())
        test_file.parse()
        expect = \
            'from applications.app1.modules.module_a import ClassA, ClassAA'
        self.assertEqual(test_file.import_line(), expect)

        # Test parse with script with sub directory

        filename = os.path.join(root_path(),
                                'applications/app2/tests/adir/test_module_d.py'
                                )
        test_file = File(filename, root_path())
        test_file.parse()
        expect = \
            'from applications.app2.modules.adir.module_d import ClassD'
        self.assertEqual(test_file.import_line(), expect)
        return

    def test__module_object(self):
        filename = os.path.join(root_path(),
                                'applications/app1/tests/test_module_a.py'
                                )
        test_file = File(filename, root_path())
        test_file.parse()
        expect = Module(os.path.join(root_path(),
                        'applications/app1/modules/module_a.py'),
                        root_path())
        self.assertEqual(test_file.module_object(), expect)
        return

    def test__module_file(self):
        filename = os.path.join(root_path(),
                                'applications/app1/tests/test_module_a.py'
                                )
        test_file = File(filename, root_path())
        test_file.parse()
        expect = os.path.join(root_path(),
                              'applications/app1/modules/module_a.py')
        self.assertEqual(test_file.module_file(), expect)

        # Test parse with script with sub directory

        filename = os.path.join(root_path(),
                                'applications/app2/tests/adir/test_module_d.py'
                                )
        test_file = File(filename, root_path())
        test_file.parse()
        expect = os.path.join(root_path(),
                              'applications/app2/modules/adir/module_d.py'
                              )
        self.assertEqual(test_file.module_file(), expect)
        return

    def test__parse(self):
        filename = os.path.join(root_path(),
                                'applications/app1/tests/test_module_a.py'
                                )
        test_file = File(filename, root_path())

        # Test parse with script without sub directory

        test_file.parse()
        self.assertEqual(test_file.application, 'app1')
        self.assertEqual(test_file.sub_directory, '')
        self.assertEqual(test_file.module, 'module_a')

        # Test parse with script with sub directory

        filename = os.path.join(root_path(),
                                'applications/app2/tests/adir/test_module_d.py'
                                )
        test_file = File(filename, root_path())
        test_file.parse()
        self.assertEqual(test_file.application, 'app2')
        self.assertEqual(test_file.sub_directory, 'adir')
        self.assertEqual(test_file.module, 'module_d')
        return

    def test__relative_module(self):
        filename = os.path.join(root_path(),
                                'applications/app1/tests/test_module_a.py'
                                )
        test_file = File(filename, root_path())
        test_file.parse()
        expect = 'applications.app1.tests.test_module_a'
        self.assertEqual(test_file.relative_module(), expect)

        # Test parse with script with sub directory

        filename = os.path.join(root_path(),
                                'applications/app2/tests/adir/test_module_d.py'
                                )
        test_file = File(filename, root_path())
        test_file.parse()
        expect = 'applications.app2.tests.adir.test_module_d'
        self.assertEqual(test_file.relative_module(), expect)
        return


class TestFileSet(unittest.TestCase):

    def test____init__(self):
        file_set = FileSet(root_path())
        self.assertTrue(file_set)  # Creates object
        self.assertEqual(file_set.apps_path, os.path.join(root_path(),
                         'applications'))

        # Test want options

        # None

        file_set = FileSet(root_path())
        self.assertEqual(file_set.want_apps, [])
        self.assertEqual(file_set.want_files, [])

        # Medley of apps and files

        want = ['app2', 'test_module_b.py', 'app1', 'test_module_d.py']
        file_set = FileSet(root_path(), want=want)
        self.assertEqual(file_set.want_apps, ['app1', 'app2'])
        self.assertEqual(file_set.want_files, ['test_module_b.py',
                         'test_module_d.py'])
        return

    def test__all_test_files(self):
        file_set = FileSet(root_path())
        expect_stubs = ['applications/app1/tests/test_module_a.py',
                        'applications/app1/tests/test_module_b.py',
                        'applications/app2/tests/adir/test_module_d.py'
                        , 'applications/app2/tests/test_module_c.py']
        expect = [File(os.path.join(root_path(), x), root_path())
                  for x in expect_stubs]
        self.assertEqual(file_set.all_test_files(), sorted(expect))
        return

    def test__relative_modules(self):
        file_set = FileSet(root_path())
        expect = ['applications.app1.tests.test_module_a',
                  'applications.app1.tests.test_module_b',
                  'applications.app2.tests.adir.test_module_d',
                  'applications.app2.tests.test_module_c']
        self.assertEqual(file_set.relative_modules(), sorted(expect))
        return

    def test__test_directories(self):
        file_set = FileSet(root_path())
        expect_stubs = ['applications/app1/tests',
                        'applications/app2/tests']
        expect = [os.path.join(root_path(), x) for x in expect_stubs]
        self.assertEqual(file_set.test_directories(), expect)
        return

    def test__want_test_files(self):

        # Want neither app nor file, ie get all

        file_set = FileSet(root_path())
        expect_stubs = ['applications/app1/tests/test_module_a.py',
                        'applications/app1/tests/test_module_b.py',
                        'applications/app2/tests/adir/test_module_d.py'
                        , 'applications/app2/tests/test_module_c.py']
        expect = [File(os.path.join(root_path(), x), root_path())
                  for x in expect_stubs]
        self.assertEqual(file_set.want_test_files(), sorted(expect))

        # Want an app
        # Want neither app nor file

        file_set = FileSet(root_path(), want=['app2'])
        expect_stubs = ['applications/app2/tests/adir/test_module_d.py'
                        , 'applications/app2/tests/test_module_c.py']
        expect = [File(os.path.join(root_path(), x), root_path())
                  for x in expect_stubs]
        self.assertEqual(file_set.want_test_files(), sorted(expect))

        # Want two apps

        file_set = FileSet(root_path(), want=['app1', 'app2'])
        expect_stubs = ['applications/app1/tests/test_module_a.py',
                        'applications/app1/tests/test_module_b.py',
                        'applications/app2/tests/adir/test_module_d.py'
                        , 'applications/app2/tests/test_module_c.py']
        expect = [File(os.path.join(root_path(), x), root_path())
                  for x in expect_stubs]
        self.assertEqual(file_set.want_test_files(), sorted(expect))

        # Want a file

        file_set = FileSet(root_path(), want=['test_module_b.py'])
        expect_stubs = ['applications/app1/tests/test_module_b.py']
        expect = [File(os.path.join(root_path(), x), root_path())
                  for x in expect_stubs]
        self.assertEqual(file_set.want_test_files(), sorted(expect))

        # Want two files

        file_set = FileSet(root_path(), want=['test_module_b.py',
                           'test_module_d.py'])
        expect_stubs = ['applications/app1/tests/test_module_b.py',
                        'applications/app2/tests/adir/test_module_d.py']
        expect = [File(os.path.join(root_path(), x), root_path())
                  for x in expect_stubs]
        self.assertEqual(file_set.want_test_files(), sorted(expect))

        # Want an app and file

        file_set = FileSet(root_path(), want=['app1', 'test_module_c.py'
                           ])
        expect_stubs = ['applications/app1/tests/test_module_a.py',
                        'applications/app1/tests/test_module_b.py',
                        'applications/app2/tests/test_module_c.py']
        expect = [File(os.path.join(root_path(), x), root_path())
                  for x in expect_stubs]
        self.assertEqual(file_set.want_test_files(), sorted(expect))
        return


class TestModule(unittest.TestCase):

    def test____init__(self):
        filename = os.path.join(root_path(),
                                'applications/app1/modules/module_a.py')
        module = Module(filename, root_path())
        self.assertTrue(module)
        return

    def test____cmp__(self):
        filename = os.path.join(root_path(),
                                'applications/app1/modules/module_a.py')
        module = Module(filename, root_path())
        filename2 = os.path.join(root_path(),
                                 'applications/app1/modules/module_b.py'
                                 )
        module2 = Module(filename2, root_path())
        self.assertEqual(cmp(module, module2), -1)
        self.assertEqual(cmp(module, module), 0)
        self.assertEqual(cmp(module2, module), 1)
        self.assertEqual(sorted([module, module2]), [module, module2])
        self.assertEqual(sorted([module, module2], reverse=True),
                         [module2, module])
        return

    def test____eq__(self):
        filename = os.path.join(root_path(),
                                'applications/app1/modules/module_a.py')
        module = Module(filename, root_path())
        module2 = Module(filename, root_path())
        self.assertEqual(module, module2)
        return

    def test____ne__(self):
        filename = os.path.join(root_path(),
                                'applications/app1/modules/module_a.py')
        module = Module(filename, root_path())
        filename2 = os.path.join(root_path(),
                                 'applications/app1/modules/module_b.py'
                                 )
        module2 = Module(filename2, root_path())
        self.assertNotEqual(module, module2)
        return

    def test____repr__(self):
        filename = os.path.join(root_path(),
                                'applications/app1/modules/module_a.py')
        module = Module(filename, root_path())
        self.assertEqual(str(module), filename)
        return

    def test__classes(self):
        filename = os.path.join(root_path(),
                                'applications/app1/modules/module_a.py')
        module = Module(filename, root_path())
        module.parse()
        expect = ['ClassA', 'ClassAA']
        self.assertEqual(module.classes(), expect)
        return

    def test__import_all_line(self):
        filename = os.path.join(root_path(),
                                'applications/app1/modules/module_a.py')
        module = Module(filename, root_path())
        module.parse()
        expect = 'from applications.app1.modules.module_a import *'
        self.assertEqual(module.import_all_line(), expect)

        # Test parse with script with sub directory

        filename = os.path.join(root_path(),
                                'applications/app2/modules/adir/module_d.py'
                                )
        module = Module(filename, root_path())
        module.parse()
        expect = 'from applications.app2.modules.adir.module_d import *'
        self.assertEqual(module.import_all_line(), expect)
        return

    def test__parse(self):
        filename = os.path.join(root_path(),
                                'applications/app1/modules/module_a.py')
        module = Module(filename, root_path())

        # Test parse with script without sub directory

        module.parse()
        self.assertEqual(module.application, 'app1')
        self.assertEqual(module.sub_directory, '')
        self.assertEqual(module.module, 'module_a')

        # Test parse with script with sub directory

        filename = os.path.join(root_path(),
                                'applications/app2/modules/adir/module_d.py'
                                )
        module = Module(filename, root_path())
        module.parse()
        self.assertEqual(module.application, 'app2')
        self.assertEqual(module.sub_directory, 'adir')
        self.assertEqual(module.module, 'module_d')
        return


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()

