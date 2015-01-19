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

    def message(self, **kwargs):
        self.signal.send('cron message {0}'.format(kwargs['message']))

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
        ret = {
            'minute': expressions[0],
            'hour': expressions[1],
            'day': expressions[2],
            'month': expressions[3],
            'day_of_week': expressions[4]
        }
        return ret

    def add_job(self, job, message):
        kwargs = {'message': message}
        cron = self.parse_cron_expression(job)
        job = self.scheduler.add_job(self.message, 'cron',
                                     kwargs=kwargs, **cron)

        return job

    def list_job(self, id):
        pass

    def remove_job(self, id):
        pass

    def pause_job(self, id):
        pass


class Cron(object):
    def __init__(self):
        self.scheduler = Scheduler()
        self._signal = None

    @property
    def signal(self):
        return None

    @signal.setter
    def signal(self, signal):
        self.scheduler.signal = signal

    @cmd(regex=r'add job "(?P<schedule>.+)" (?P<body>.+)')
    def add(self, message, **kwargs):
        group = message.match
        job = self.scheduler.add_job(group(1), group(2))

        return 'Job {0} created.'.format(job)
