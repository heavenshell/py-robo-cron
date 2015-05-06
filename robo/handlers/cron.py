# -*- coding: utf-8 -*-
"""
    robo.handlers.cron
    ~~~~~~~~~~~~~~~~~~

    cron handler for robo.


    :copyright: (c) 2015 Shinya Ohyanagi, All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from robo.decorators import cmd

logger = logging.getLogger('robo')


class Scheduler(object):
    #: Robo's signal.
    signal = None

    def __init__(self):
        """Construct a scheduler."""
        self.scheduler = BackgroundScheduler()
        if not self.scheduler.running:
            self.scheduler.start()

        self.alias = None

    @classmethod
    def message(cls, **kwargs):
        """Send registered message to robot.

        :param **kwargs: Data to be sent to receivers
        """
        cls.signal.send(kwargs['message_body'], **kwargs)

    def parse_cron_expression(self, cron):
        """Parse cron expression.

        * * * * *
        T T T T T
        | | | | `- day_of_week - 0 ..  6
        | | | `--- month ------- 1 .. 12
        | | `----- day --------- 1 .. 31
        | `------- hour -------- 0 .. 23
        `--------- minute ------ 0 .. 59

        :param cron: Cron expression
        """
        expressions = cron.split(' ')
        if len(expressions) != 5:
            return None

        ret = {
            'minute': expressions[0],
            'hour': expressions[1],
            'day': expressions[2],
            'month': expressions[3],
            'day_of_week': expressions[4]
        }
        return ret

    def add_job(self, cron, message, **kwargs):
        """Add job to scheduler.

        :param cron: Cron style expression
        :param message: Message to show
        """
        kwargs.update({'message_body': message})
        cron = self.parse_cron_expression(cron)
        if cron is None:
            return None
        job = None
        try:
            job = self.scheduler.add_job(self.message, 'cron',
                                         jobstore=self.alias,
                                         kwargs=kwargs, **cron)
        except Exception as e:
            logger.error(e)
            logger.info('Cron expression is {0}.'.format(cron))
            logger.info('Action is {0}.'.format(message))

        return job

    def list_jobs(self):
        """List jobs.

        Returns job contains id, cron expression, message, next trigger.
        """
        jobs = self.scheduler.get_jobs()
        results = []
        fmt = '{0}: "{1}" {2} {3}'
        for job in jobs:
            cron = '{0} {1} {2} {3} {4}'.format(
                job.trigger.fields[6],  # minute
                job.trigger.fields[5],  # hour
                job.trigger.fields[2],  # day
                job.trigger.fields[1],  # month
                job.trigger.fields[4],  # day of week
            )
            #: When job is paused, job.next_run_time is null.
            if job.next_run_time is None:
                time = 'paused'
            else:
                time = job.next_run_time.strftime('%Y/%m/%d %H:%M:%S')
            message = job.kwargs['message_body']
            results.append(fmt.format(job.id, cron, time, message))

        return results

    def remove_job(self, id):
        """Remove job.

        :param id: Job id
        """
        try:
            self.scheduler.remove_job(id)
        except JobLookupError as e:
            logger.error(e)

            return False

        return True

    def pause_job(self, id):
        """Pause job.

        :param id: Job id
        """
        self.scheduler.pause_job(id)

    def resume_job(self, id):
        """Resume job.

        :param id: Job id
        """
        self.scheduler.resume_job(id)

    def add_jobstore(self, jobstore, **kwargs):
        """Add a job store to scheduler.

        :param jobstore: Job store
        """
        try:
            self.scheduler.add_jobstore(jobstore, **kwargs)
        except ValueError as e:
            logger.error(e)
            return False

        return True


class Cron(object):

    def __init__(self):
        """Construct a cron handler.

        > robo add job "0 * * * *" robo echo message
        Every 0 minute fired `robo echo message` command.
        """
        #: Disable apscheduler's log.
        apslogger = logging.getLogger('apscheduler')
        apslogger.setLevel(logging.ERROR)

        self.scheduler = Scheduler()
        self._signal = None
        self._options = None

    @property
    def signal(self):
        return None

    @signal.setter
    def signal(self, signal):
        #: Signal should be classmethod because if signal is instance,
        #: `apscheduler` would raise ValueError.
        #: ValueError: This Job cannot be serialized since the reference to
        #: its callable
        Scheduler.signal = signal

    @property
    def options(self):
        return None

    @options.setter
    def options(self, options):
        if isinstance(options, dict) and 'cron' in options:
            if 'jobstore' in options['cron']:
                jobstore = options['cron']['jobstore']
            else:
                return

            job_options = {}
            if 'options' in options['cron']:
                job_options = options['cron']['options']

                if 'alias' in job_options:
                    self.scheduler.alias = job_options['alias']

            self.scheduler.add_jobstore(jobstore, **job_options)

    @cmd(regex=r'add job "(?P<schedule>.+)" (?P<body>.+)',
         description='Add a cron job.')
    def add(self, message, **kwargs):
        job = self.scheduler.add_job(message.match.group(1),
                                     message.match.group(2),
                                     **kwargs)

        return 'Job {0} created.'.format(job)

    @cmd(regex=r'list jobs$', description='List all cron jobs.')
    def list(self, message, **kwargs):
        jobs = self.scheduler.list_jobs()

        return '\n'.join(jobs)

    @cmd(regex=r'delete job (?P<id>.+)', description='Delte a cron job.')
    def delete(self, message, **kwargs):
        ret = self.scheduler.remove_job(message.match.group(1))
        if ret is False:
            return 'Fail to delete job. Job not found.'

        return 'Success to delete job.'

    @cmd(regex=r'pause job (?P<id>.+)', description='Pause a cron job.')
    def pause(self, message, **kwargs):
        self.scheduler.pause_job(message.match.group(1))

        return 'Job paused.'

    @cmd(regex=r'resume job (?P<id>.+)', description='Resume a cron job.')
    def resume(self, message, **kwargs):
        self.scheduler.resume_job(message.match.group(1))

        return 'Job resumed.'

    @cmd(regex=r'job expression$', description='Show job expression.')
    def usage(self, message, **kwargs):
        usage = """
        * * * * *
        T T T T T
        | | | | `- day_of_week - 0 ..  6
        | | | `--- month ------- 1 .. 12
        | | `----- day --------- 1 .. 31
        | `------- hour -------- 0 .. 23
        `--------- minute ------ 0 .. 59
        """

        return usage
