robo.handlers.cron
==================
.. image:: https://travis-ci.org/heavenshell/py-robo-cron.svg?branch=master
    :target: https://travis-ci.org/heavenshell/py-robo-cron

Mount cron system to `robo <https://github.com/heavenshell/py-robo/>`_.

Send messages on a specific time.

Dependency
----------

This handler depends on `APScheduler <https://bitbucket.org/agronholm/apscheduler/>`_.

Usage
-----

Add job to run `robo` handler.

.. code::

  > robo add job "*/1 * * * *" robo echo hello
  Job Scheduler.message (trigger: cron[month='*', day='*', day_of_week='*', hour='*', minute='*/1'], next run at: 2015-01-23 00:53:00 JST) created.
  hello

List all jobs.

.. code::

  > robo list jobs
  61530a5a8e7e40c7814ce90768792476: "*/1 * * * *" 2015/01/23 00:55:00 robo echo hello

Pause specific job.

.. code::
  > robo pause job 61530a5a8e7e40c7814ce90768792476
  Job paused.

Resume paused job.

.. code::

  > robo resume job 61530a5a8e7e40c7814ce90768792476
  Job resumed.

Delete job.

.. code::
  > robo delete job 61530a5a8e7e40c7814ce90768792476
  Success to delete job.
