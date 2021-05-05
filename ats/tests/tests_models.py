from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import IntegrityError

import datetime
from datetime import timedelta

import pytz

from ..models import (
    Job,
    Task,
    Project,
    ProjectWorker,
    UsedTaskTime)


class TestModel(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_job(self):
        _o = Job(id=100, name='aaa', sortkey=10000, invalid=False)
        _s = str(_o)
        self.assertEqual(_s, '100 : aaa')

        _o = Job(id=100, name='aaa', sortkey=10000, invalid=True)
        _s = str(_o)
        self.assertEqual(_s, '100 : aaa [invalid]')

    def test_task(self):
        _job = Job.objects.create(
            id=100, name='jobname', sortkey=10000, invalid=False)

        _o = Task(id=101, name='taskname1', job=_job, sortkey=10001,
                  invalid=False)
        _s = str(_o)
        self.assertEqual(_s, '101 : taskname1 (jobname)')

        _o = Task(id=102, name='taskname2', job=_job, sortkey=10002,
                  invalid=True)
        _s = str(_o)
        self.assertEqual(_s, '102 : taskname2 (jobname) [invalid]')

    def test_project(self):
        _tzgmt = pytz.timezone('Etc/GMT')
        _delta = datetime.timedelta(days=1)
        _now = datetime.datetime.now(tz=_tzgmt)
        _at_s = datetime.date(year=2000, month=1, day=1)

        _o = Project.objects.create(
            id=200, name='projname1',
            start_dt=_at_s, end_dt=None, sortkey=10000)
        _s = str(_o)
        self.assertEqual(_s, '200 : projname1 [opened]')

        _at_e1 = _now.date()
        _o = Project.objects.create(
            id=201, name='projname2',
            start_dt=_at_s, end_dt=_at_e1, sortkey=10001)
        _s = str(_o)
        self.assertEqual(_s, '201 : projname2 [opened]')

        _at_tmp = _now - _delta
        _at_e2 = _at_tmp.date()
        _o = Project.objects.create(
            id=202, name='projname3',
            start_dt=_at_s, end_dt=_at_e2, sortkey=10001)
        _s = str(_o)
        self.assertEqual(_s, '202 : projname3 [closed]')

    def test_projectworker(self):
        _user = User.objects.create_user(
            'testuser1',
            'testuser1@example.com',
            'password')
        _at_s = datetime.date(year=2000, month=1, day=1)
        _proj = Project.objects.create(
            id=200, name='projname200',
            start_dt=_at_s, end_dt=None, sortkey=10000)
        _job = Job.objects.create(
            id=100, name='job100', sortkey=10000, invalid=False)

        _o = ProjectWorker.objects.create(
                id=50000, user=_user, project=_proj, job=_job, invalid=False)
        _s = str(_o)
        self.assertEqual(_s, '50000 : testuser1 (projname200 - job100)')

        # unique error test
        try:
            _o = ProjectWorker.objects.create(
                id=50001, user=_user, project=_proj, job=_job, invalid=True)
        except IntegrityError as e:
            self.assertTrue(True)
        else:
            self.fail('permit add unique job, project and user on ProjectWorker.')

    def test_usedtasktime(self):
        _user = User.objects.create_user(
            'testuser1',
            'testuser1@example.com',
            'password')
        _at_s = datetime.date(year=2000, month=1, day=1)
        _proj = Project.objects.create(
            id=200, name='proj200',
            start_dt=_at_s, end_dt=None, sortkey=10000)
        _job = Job.objects.create(
            id=100, name='job100', sortkey=10000, invalid=False)

        _task = Task.objects.create(
            id=201, name='task201',
            job=_job, sortkey=10001, invalid=False)

        _td = datetime.date(year=2019, month=2, day=1)
        _tt = datetime.time(hour=1, minute=30, second=0)
        _o = UsedTaskTime.objects.create(
            id=60000,
            user=_user, project=_proj, task=_task,
            taskdate=_td, tasktime=_tt)
        _s = str(_o)
        self.assertEqual(
            _s,
            '60000 : [2019-02-01 - 01:30:00] testuser1 - proj200 - task201')
