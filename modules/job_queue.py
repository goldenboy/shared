#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
job_queue.py

Classes related to job queues.

"""
import os
import shlex
import subprocess
import time

from applications.shared.modules.database import DbObject


class QueueEmptyError(Exception):
    """Exception indicating the Queue is empty."""
    pass


class QueueLockedError(Exception):
    """Exception indicating the Queue is locked."""
    pass


class QueueLockedExtendedError(Exception):
    """Exception indicating the Queue is locked and has been locked for an
    extended period.
    """
    pass


class Job(DbObject):
    """Class representing a job record."""
    def __init__(self, tbl_, **kwargs):
        """Constructor."""
        DbObject.__init__(self, tbl_, **kwargs)

    def run(self):
        """Run the job command.

        The command is expected to be a python script with optional arguments
        and options. It is run as:
            $ python <command>
        """
        # E1101: *%s %r has no %r member*
        # pylint: disable=E1101

        if not self.command:
            return
        args = ['python']
        args.extend(shlex.split(self.command))
        return subprocess.call(args)


class Queue(object):
    """Class representing a job queue."""
    lock_filename = '/var/run/job_queue.pid'

    def __init__(self, tbl_):
        """Constructor.

        Args:
            tbl_: gluon.dal.Table of table jobs are stored in.
        """
        self.tbl_ = tbl_

    def jobs(self, maximum_start=None, orderby=None, limitby=None):
        """Return the jobs in the queue.

        Args:
            maximum_start: string, datetime value 'yyyy-mm-dd hh:mm:ss'. If
                provided, the jobs returned are restricted to those where the
                start value is less than or equal to this. Set this to the
                current time and jobs scheduled in the future are not run.
            orderby: list, tuple or string, cmp orderby attribute as per
                    gluon.sql.SQLSet._select()
                    Example: db.person.name
            limitby: integer or tuple. Tuple is format (start, stop). If
                    integer converted to tuple (0, integer)
                    See database.py Collection.get() for more details.
        Returns:
            list, list of Job object instances.
        """
        query = self.tbl_.status == 'a'
        if maximum_start:
            query = query & (self.tbl_.start <= maximum_start)
        return Job(self.tbl_).set_.get(query=query, orderby=orderby,
                limitby=limitby)

    def lock(self, filename=None, extended_seconds=0):
        """Lock the queue.

        Notes:
            Locking the queue involves creating a pid file.

        Args:
            filename: string, name of file including path used for locking.
                If not provided, the Queue.lock_filename class property is
                used.
            extended_seconds: integer, if not zero, and the queue is locked and
                the queue has been locked for more then this number of seconds,
                QueueLockedExtendedError is raised.
        Returns:
            String, name of file including path used for locking.

        Raises:
            QueueLockedError, if the queue is already locked.
            QueueLockedExtendedError, if the queue is already lock and has
                been for an extended period of time.
        """
        if not filename:
            filename = self.lock_filename

        if os.path.exists(filename):
            extended = False
            if extended_seconds > 0:
                now = time.mktime(time.localtime())
                statinfo = os.stat(filename)
                diff = now - statinfo.st_mtime
                if diff > extended_seconds:
                    extended = True
            msg = 'Queue is locked: {file}'.format(file=filename)
            if extended:
                raise QueueLockedExtendedError(msg)
            else:
                raise QueueLockedError(msg)

        with open(filename, 'w') as f:
            f.write(str(os.getpid()))
        return filename

    def top_job(self):
        """Return the highest priority job in the queue.

        Returns:
            Job object instance. None, if no job found.
        """
        start = time.strftime('%F %T', time.localtime())    # now
        orderby = ~self.tbl_.priority
        top_jobs = self.jobs(maximum_start=start, orderby=orderby, limitby=1)
        if len(top_jobs) == 0:
            msg = 'There are no jobs in the queue.'
            raise QueueEmptyError(msg)
        return top_jobs.first()

    def unlock(self, filename=None):
        """Lock the queue.

        Notes:
            Unlocking the queue involves deleting the pid file.

        Args:
            filename: string, name of file including path used for locking.
                If not provided, the Queue.lock_filename class property is
                used.
        """
        if not filename:
            filename = self.lock_filename
        if os.path.exists(filename):
            os.unlink(filename)
        return



def trigger_queue_handler(request):
    """Decorator for triggering activation of queue handler"""
    def wrapper(f):
        def wrapped_f(*args, **kwargs):
            result = f(*args, **kwargs)
            trigger_script = os.path.join('.', request.folder, 'private/bin', 'queue_trigger.sh')
            subprocess.Popen([trigger_script])
            return result
        return wrapped_f
    return wrapper



