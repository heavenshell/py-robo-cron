# -*- coding: utf-8 -*-
"""
    robo.tests.test_cron
    ~~~~~~~~~~~~~~~~~~~~

    Tests for robo.handlers.cron.


    :copyright: (c) 2015 Shinya Ohyanagi, All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
from unittest import TestCase
from src.handlers.cron import Scheduler


class TestScheduler(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scheduler = Scheduler()

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


class TestCronHandler(TestCase):
    pass

