#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Utility script for modify all test scripts.

"""

from applications.shared.modules.testing import FileSet
import os
import shutil
import sys
import tempfile

TMP_DIR = '/tmp'


def main():
    """ Main routine. """

    testset = FileSet('/srv/http/igeejo/web2py', want=sys.argv[1:])
    for test_file in testset.want_test_files():
        print 'Updating: {script}'.format(script=test_file.filename)
        module_object = test_file.module_object()
        import_line = test_file.import_line()
        import_all = module_object.import_all_line()
        (os_handle, tmp_name) = tempfile.mkstemp(dir=TMP_DIR)
        file_h = os.fdopen(os_handle, 'w')
        with open(test_file.filename, 'r') as f_test_script:
            lines = f_test_script.readlines()
            for line in lines:
                if line.strip() == import_all:
                    file_h.write(import_line)
                    file_h.write('\n')
                else:
                    file_h.write(line)
        file_h.close()
        # The next line is commented as a safety precaution.
        # shutil.copyfile(tmp_name, test_file.filename)


if __name__ == '__main__':
    main()
