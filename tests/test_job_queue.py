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

from applications.shared.modules.local.test_runner import LocalTestSuite, \
    ModuleTestSuite
from applications.shared.modules.job_queue import Job, Queue, \
        QueueEmptyError, QueueLockedError, QueueLockedExtendedError
from gluon.shell import env

# C0111: *Missing docstring*
# R0904: *Too many public methods (%s/%s)*
# pylint: disable=C0111,R0904

# The test script requires an existing database to work with. The
# database needs to be set up for web2py.  We'll use the igeejo
# database for lack of a better one.

APPLICATION = 'igeejo'

APP_ENV = env(APPLICATION, import_models=True)
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


def main():
    suite = LocalTestSuite()
    suite.add_tests(ModuleTestSuite(module=sys.modules[__name__]))
    suite.run_tests()


if __name__ == '__main__':
    main()
