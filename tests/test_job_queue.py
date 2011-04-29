#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
test_job_queue.py

Test suite for shared/modules/job_queue.py

"""

import os
import sys
import time
import unittest

from applications.shared.modules.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.job_queue import Job, Queue, \
        QueueEmptyError, QueueLockedError, QueueLockedExtendedError, \
        trigger_queue_handler
from gluon.shell import env

# C0111: *Missing docstring*
# R0904: *Too many public methods (%s/%s)*
# pylint: disable=C0111,R0904

# The test script requires an existing database to work with. The shared
# database should have a job table. The models/db.py should define the table.

APP_ENV = env(__file__.split('/')[-3], import_models=True)
DBH = APP_ENV['db']

TMP_DIR = '/tmp/test_suite/job_queue'

if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)


class TestJob(unittest.TestCase):

    def test____init__(self):
        job = Job(DBH.job)
        self.assertTrue(job)

    def test__run(self):
        job = Job(DBH.job)
        # No command defined, should fail.
        self.assertFalse(job.run())

        tmp_file = os.path.join(TMP_DIR, 'test__run_output.txt')
        text = 'Hello World!'

        script = """
#!/usr/bin/python
import sys

def main():
    with open('{file}', 'w') as f:
        f.write("{text}")
        f.write("\\n")
        for c, arg in enumerate(sys.argv):
            if c == 0:
                continue
            f.write(str(c) + ': ' + arg + "\\n")

if __name__ == '__main__':
    main()
    """.format(file=tmp_file, text=text)

        script_name = os.path.join(TMP_DIR, 'test__run.py')
        with open(script_name, 'w') as f:
            f.write(script.strip())
        os.chmod(script_name, 0700)

        # Test without args or options
        job.command = script_name
        self.assertEqual(job.run(), 0)

        expect = """Hello World!
"""
        got = ''
        with open(tmp_file, 'r') as f:
            got = f.read()
        self.assertEqual(got, expect)

        # Test with args or options
        job.command = "{script} -v -a delete 123".format(script=script_name)
        self.assertEqual(job.run(), 0)
        expect = """Hello World!
1: -v
2: -a
3: delete
4: 123
"""
        got = ''
        with open(tmp_file, 'r') as f:
            got = f.read()
        self.assertEqual(got, expect)


class TestQueue(unittest.TestCase):

    def test____init__(self):
        queue = Queue(DBH.job)
        self.assertTrue(queue)

    def test__jobs(self):
        queue = Queue(DBH.job)

        # Remove existing data
        for j in Job(DBH.job).set_.get():
            j.remove()
        self.assertEqual(len(queue.jobs()), 0)

        # (number, start, priority, status)
        job_data = [
            ('2010-01-01 10:00:00',  0, 'a'),
            ('2010-01-01 10:00:00',  0, 'd'),
            ('2010-01-01 10:00:01', -1, 'a'),
            ('2010-01-01 10:00:01', -1, 'd'),
            ('2010-01-01 10:00:02',  1, 'a'),
            ('2010-01-01 10:00:02',  1, 'd'),
            ]

        jobs = []
        for j in job_data:
            job_d = dict(command='pwd', start=j[0], priority=j[1], status=j[2])
            jobs.append(Job(DBH.job, **job_d).add())

        job_set = queue.jobs()
        self.assertEqual(len(job_set), 3)
        self.assertEqual([x.id for x in job_set],
                [jobs[0].id, jobs[2].id, jobs[4].id])

        job_set = queue.jobs(maximum_start='2010-01-01 10:00:01')
        self.assertEqual(len(job_set), 2)
        self.assertEqual([x.id for x in job_set],
                [jobs[0].id, jobs[2].id])

        # Test orderby
        # Orderby priority ASC
        job_set = queue.jobs(orderby=DBH.job.priority)
        self.assertEqual(len(job_set), 3)
        self.assertEqual([x.id for x in job_set],
                [jobs[2].id, jobs[0].id, jobs[4].id])

        # Orderby priority DESC
        job_set = queue.jobs(orderby=~DBH.job.priority)
        self.assertEqual(len(job_set), 3)
        self.assertEqual([x.id for x in job_set],
                [jobs[4].id, jobs[0].id, jobs[2].id])

        # Test limitby
        # Highest priority job
        job_set = queue.jobs(orderby=~DBH.job.priority, limitby=1)
        self.assertEqual(len(job_set), 1)
        self.assertEqual([x.id for x in job_set], [jobs[4].id])

        for j in jobs:
            j.remove()

    def test__lock(self):
        queue = Queue(DBH.job)

        # Test lock using default lock file. This test only works if the queue
        # is not currently locked by an outside program.
        if os.path.exists(queue.lock_filename):
            os.unlink(queue.lock_filename)
        self.assertFalse(os.path.exists(queue.lock_filename))
        queue.lock()
        self.assertTrue(os.path.exists(queue.lock_filename))
        queue.unlock()
        self.assertFalse(os.path.exists(queue.lock_filename))

        # Test lock with custom filename.
        lock_file = os.path.join(TMP_DIR, 'test__lock.pid')
        if os.path.exists(lock_file):
            os.unlink(lock_file)
        self.assertFalse(os.path.exists(lock_file))
        queue.lock(filename=lock_file)
        self.assertTrue(os.path.exists(lock_file))

        # Test raise QueueLockedError
        self.assertRaises(QueueLockedError, queue.lock, filename=lock_file)
        # Test raise QueueLockedExtendedError
        time.sleep(2)
        # Lock period < extended seconds, raises QueueLockedError
        self.assertRaises(QueueLockedError, queue.lock,
                filename=lock_file, extended_seconds=9999)
        # Lock period > extended seconds, raises QueueLockedExtendedError
        self.assertRaises(QueueLockedExtendedError, queue.lock,
                filename=lock_file, extended_seconds=1)
        queue.unlock(filename=lock_file)
        self.assertFalse(os.path.exists(lock_file))

    def test__top_job(self):
        queue = Queue(DBH.job)
        if len(queue.jobs()) > 0:
            for j in queue.jobs():
                j.remove()
        self.assertEqual(len(queue.jobs()), 0)

        self.assertRaises(QueueEmptyError, queue.top_job)

        job_1 = Job(DBH.job, start='2010-01-01 10:00:00', priority=0).add()
        job_2 = Job(DBH.job, start='2010-01-01 10:00:01', priority=-1).add()
        job_3 = Job(DBH.job, start='2010-01-01 10:00:02', priority=1).add()
        job_4 = Job(DBH.job, start='2999-12-31 23:59:59', priority=1).add()

        job = queue.top_job()
        self.assertEqual(job.id, job_3.id)

        job_1.remove()
        job_2.remove()
        job_3.remove()
        job_4.remove()

    def test__unlock(self):
        # See test__lock()
        pass


class TestFunctions(unittest.TestCase):

    def test__trigger_queue_handler(self):
        """
        Note: this test requires private/bin/queue_trigger.sh exists with this
        line:
        echo 'queue_trigger.sh success' > $TMP_DIR/test__trigger_queue_handler.txt
        """
        request = APP_ENV['request']
        expect_content = 'queue_trigger.sh success'
        tmp_file = os.path.join(TMP_DIR, 'test__trigger_queue_handler.txt')
        if os.path.exists(tmp_file):
            os.unlink(tmp_file)
        self.assertFalse(os.path.exists(tmp_file))

        # Create a queue_trigger.sh script.
        trigger_script = os.path.join(request.folder, 'private/bin', 'queue_trigger.sh')
        if os.path.exists(trigger_script):
            self.fail('Refusing to overwrite existing file: {f}'.format(f=trigger_script))

        text = """#!/bin/bash
# queue_trigger.sh
# This script is used for testing: test__trigger_queue_handler
exec 1> >(logger -p "local7.error" -t "${{0##*/}} (ERROR)" )
exec 2>&1
echo '{txt}' > {tmp}
""".format(txt=expect_content, tmp=tmp_file)

        f = open(trigger_script, 'w')
        f.write(text)
        f.close()
        os.chmod(trigger_script, 0700)

        @trigger_queue_handler(request)
        def test_function(arg, kwarg=''):
            """Test function docstring"""
            return 'arg: {arg}, kwarg: {kwarg}'.format(arg=arg, kwarg=kwarg)

        # Make sure functools.wraps prevents decorator from morphing function.
        self.assertEqual(test_function.__doc__, 'Test function docstring')

        # Test calling function. Ensure args are passed and expected value
        # returned.
        expect = 'arg: 111, kwarg: aaa'
        self.assertEqual(test_function(111, kwarg='aaa'), expect)

        # decorator runs script in background. Pause a bit for that to
        # complete.
        time.sleep(2)

        # Test that queue_trigger.sh was called
        # * file exists
        # * file has content.
        self.assertTrue(os.path.exists(tmp_file))
        f = open(tmp_file)
        got = f.read().strip()
        f.close()
        self.assertEqual(got, expect_content)

        os.unlink(trigger_script)


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
