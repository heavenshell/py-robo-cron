# -*- coding: utf-8 -*-
"""
    robo.tests.test_cron
    ~~~~~~~~~~~~~~~~~~~~

    Tests for robo.handlers.cron.


    :copyright: (c) 2016 Shinya Ohyanagi, All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import logging
from unittest import TestCase
from robo.robot import Robot
from robo.handlers.cron import Scheduler, Cron


class NullAdapter(object):
    def __init__(self, signal):
        self.signal = signal
        self.responses = []

    def say(self, message, **kwargs):
        self.responses.append(message)
        return message


class TestScheduler(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scheduler = Scheduler()
        cls.scheduler.alias = 'default'

    def tearDown(self):
        self.scheduler.scheduler.remove_all_jobs()

    def test_should_parse_cron_expression(self):
        """ Scheduler().parse_cron_expression() should parse to `apscheduler` expressions. """
        ret = self.scheduler.parse_cron_expression('15 1 5 12 6')
        expected = {
            'minute': '15',
            'hour': '1',
            'day': '5',
            'month': '12',
            'day_of_week': '6'
        }
        self.assertEqual(ret, expected)

    def test_should_add_job(self):
        """ Scheduler().add_job() should add job. """
        ret = self.scheduler.add_job('15 1 5 12 6', 'test job')
        self.assertIsNotNone(ret)

    def test_should_not_add_job(self):
        """ Scheduler().add_job() should return None when expprssion is invalid. """
        ret = self.scheduler.add_job('* * * *', 'test job')
        self.assertIsNone(ret)

    def test_should_list_jobs(self):
        self.scheduler.add_job('* * * * *', 'test job')
        jobs = self.scheduler.list_jobs()
        self.assertTrue('"* * * * *"' in jobs[0])
        self.assertTrue('test job' in jobs[0])

    def test_should_delete_job(self):
        """ Scheduler().remove_job() shoudl return True when job remove sucess. """
        job = self.scheduler.add_job('*/10 * * * *', 'test job')
        ret = self.scheduler.remove_job(job.id)
        self.assertTrue(ret)

    def test_should_delete_job_fail(self):
        """ Scheduler().remove_job() should return True when job remove sucess. """
        ret = self.scheduler.remove_job('foobar')
        self.assertFalse(ret)

    def test_should_pouse_job(self):
        """ Scheduler().pause_job() should pause registered job. """
        job = self.scheduler.add_job('*/15 * * * *', 'test job')
        self.scheduler.pause_job(job.id)
        jobs = self.scheduler.list_jobs()
        self.assertTrue('paused' in jobs[0])

    def test_should_resume_job(self):
        """ Scheduler().resume_job() should resume paused job. """
        job = self.scheduler.add_job('*/30 * * * *', 'test job2')
        self.scheduler.pause_job(job.id)
        jobs = self.scheduler.list_jobs()
        self.assertTrue('paused' in jobs[0])

        self.scheduler.resume_job(job.id)
        jobs = self.scheduler.list_jobs()
        self.assertFalse('paused' in jobs[0])


class TestCronHandler(TestCase):
    @classmethod
    def setUpClass(cls):
        logger = logging.getLogger('robo')
        logger.level = logging.ERROR
        cls.robot = Robot('test', logger)

        cron = Cron()
        cron.signal = cls.robot.handler_signal
        cron.options = {
            'cron': {
                'jobstore': 'memory',
                'options': {'alias': 'default'}
            }
        }
        method = cls.robot.parse_handler_methods(cron)
        cls.robot.handlers.extend(method)

        adapter = NullAdapter(cls.robot.handler_signal)
        cls.robot.adapters['null'] = adapter

    def _job_id(self):
        self.robot.handler_signal.send('test list jobs')
        job = self.robot.adapters['null'].responses[0]
        id = job[:job.find(':')]
        self.robot.adapters['null'].responses = []

        return id

    def test_should_add_job(self):
        """ Cron().add() should register job to scheduler and return job message. """
        self.robot.handler_signal.send('test add job "* * * * *" foo')
        self.assertRegexpMatches(self.robot.adapters['null'].responses[0],
                                 r'^Job Scheduler\.message')
        self.robot.adapters['null'].responses = []

    def test_list_job(self):
        """Cron().list_jobs should contains job id, trigger expressions. """
        self.robot.handler_signal.send('test add job "* * * * *" foo')
        self.robot.adapters['null'].responses = []
        self.robot.handler_signal.send('test list jobs')
        job = self.robot.adapters['null'].responses[0]
        self.assertRegexpMatches(job, r'[A-z0-9]: "* * * * *"')
        self.robot.adapters['null'].responses = []

    def test_should_delete_job(self):
        """ Cron().delete() should not delete job from scheduler when job id not exists. """
        self.robot.handler_signal.send('test add job "* * * * *" foo')
        self.robot.adapters['null'].responses = []
        self.robot.handler_signal.send('test delete job aaa')

        self.assertEqual(self.robot.adapters['null'].responses[0],
                         'Fail to delete job. Job not found.')
        self.robot.adapters['null'].responses = []

    def test_should_not_delete_job(self):
        """ Cron().delete() should delete job from scheduler. """
        self.robot.handler_signal.send('test add job "* * * * *" foo')
        self.robot.adapters['null'].responses = []
        id = self._job_id()
        self.robot.handler_signal.send('test delete job {0}'.format(id))

        self.assertEqual(self.robot.adapters['null'].responses[0],
                         'Success to delete job.')
        self.robot.adapters['null'].responses = []

    def test_should_pause_job(self):
        """ Cron().pause() should pause job. """
        self.robot.handler_signal.send('test add job "* * * * *" foo')
        self.robot.adapters['null'].responses = []
        id = self._job_id()
        self.robot.handler_signal.send('test pause job {0}'.format(id))

        self.assertEqual(self.robot.adapters['null'].responses[0],
                         'Job paused.')

    def test_should_resume_job(self):
        """ Cron().resume() should pause job. """
        self.robot.handler_signal.send('test add job "* * * * *" foo')
        self.robot.adapters['null'].responses = []
        id = self._job_id()
        self.robot.handler_signal.send('test pause job {0}'.format(id))
        self.robot.adapters['null'].responses = []

        self.robot.handler_signal.send('test resume job {0}'.format(id))
        self.assertEqual(self.robot.adapters['null'].responses[0],
                         'Job resumed.')
