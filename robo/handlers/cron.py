# -*- coding: utf-8 -*-
"""
    robo.handlers.cron
    ~~~~~~~~~~~~~~~~~~

    cron handler for robo.


    :copyright: (c) 2015 Shinya Ohyanagi, All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from robo.decorators import cmd


class Scheduler(object):
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.signal = None
        self.robot_name = None

    def message(self, **kwargs):
        self.signal.send('{0} {1}'.format(self.robot_name, kwargs['message']))

    def parse_cron_expression(self, cron):
        """Parse cron expression.

        * * * * *
        T T T T T
        | | | | `- day_of_week - 0 ..  6
        | | | `--- month ------- 1 .. 12
        | | `----- day --------- 1 .. 31
        | `------- hour -------- 0 .. 23
        `--------- minute ------ 0 .. 59

        :param cron:
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

    def add_job(self, cron, message):
        """Add job to scheduler.

        :param cron: Cron style expression
        :param message: Message to show
        """
        kwargs = {'message': message}
        cron = self.parse_cron_expression(cron)
        if cron is None:
            return None
        job = self.scheduler.add_job(self.message, 'cron',
                                     kwargs=kwargs, **cron)

        return job

    def list_job(self):
        """List job.

        Job contains id, cron expression, message, next trigger.
        """
        jobs = self.scheduler.get_jobs()
        results = []
        for job in jobs:
            cron = '{0} {1} {2} {3} {4}'.format(
                job.trigger.fields[6], #: minute
                job.trigger.fields[5], #: hour
                job.trigger.fields[2], #: day
                job.trigger.fields[1], #: month
                job.trigger.fields[4], #: day of week
            )
            results.append({
                'id': job.id,
                'message': job.kwargs['message'],
                'trigger': cron,
                'next': job.next_run_time.strftime('%Y/%m/%d %H:%M:%S')
            })

        return results

    def remove_job(self, id):
        pass

    def pause_job(self, id):
        pass


class Cron(object):
    def __init__(self):
        self.scheduler = Scheduler()
        self._signal = None
        self._name = None

    @property
    def robot_name(self):
        return None

    @robot_name.setter
    def name(self, robot_name):
        self.scheduler.robot_name = robot_name

    @property
    def signal(self):
        return None

    @signal.setter
    def signal(self, signal):
        self.scheduler.signal = signal

    @cmd(regex=r'add job "(?P<schedule>.+)" (?P<body>.+)',
         description='add job')
    def add(self, message, **kwargs):
        group = message.match
        job = self.scheduler.add_job(group(1), group(2))

        return 'Job {0} created.'.format(job)
