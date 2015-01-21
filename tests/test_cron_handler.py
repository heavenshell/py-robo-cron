# -*- coding: utf-8 -*-
"""
    robo.tests.test_cron
    ~~~~~~~~~~~~~~~~~~~~

    Tests for robo.handlers.cron.


    :copyright: (c) 2015 Shinya Ohyanagi, All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
from unittest import TestCase
from robo.handlers.cron import Scheduler


class TestScheduler(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scheduler = Scheduler()

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
        ret = self.scheduler.add_job('15 1 5 12', 'test job')
        self.assertIsNone(ret)

    def test_should_list_jobs(self):
        self.scheduler.add_job('15 1 1 12 *', 'test job')
        jobs = self.scheduler.list_job()
        self.assertTrue('"15 1 1 12 *"' in jobs[0])
        self.assertTrue('test job' in jobs[0])

    def test_should_delete_job(self):
        """ Scheduler().remove_job() shoudl return True when job remove sucess. """
        job = self.scheduler.add_job('15 1 1 12 *', 'test job')
        ret = self.scheduler.remove_job(job.id)
        self.assertTrue(ret)

    def test_should_delete_job_fail(self):
        """ Scheduler().remove_job() should return True when job remove sucess. """
        ret = self.scheduler.remove_job('foobar')
        self.assertFalse(ret)

    def test_should_pouse_job(self):
        """ Scheduler().pause_job() should pause registered job. """
        job = self.scheduler.add_job('15 1 1 12 *', 'test job')
        self.scheduler.pause_job(job.id)
        jobs = self.scheduler.list_job()
        self.assertTrue('paused' in jobs[0])

    def test_should_resume_job(self):
        """ Scheduler().resume_job() should resume paused job. """
        job = self.scheduler.add_job('15 1 1 12 *', 'test job2')
        self.scheduler.pause_job(job.id)
        jobs = self.scheduler.list_job()
        self.assertTrue('paused' in jobs[0])

        self.scheduler.resume_job(job.id)
        jobs = self.scheduler.list_job()
        self.assertFalse('paused' in jobs[0])


class TestCronHandler(TestCase):
    pass
