from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User

import datetime
from datetime import timedelta

import pytz

from .views import (
    format_totaltime,
    format_hours_float,
    validate_password,
    error404,
    error500,
    index,
    login_view,
    logout_view)

from .models import (
    Job,
    Task,
    Project,
    ProjectWorker,
    UsedTaskTime)


class AtsTestClient(Client):
    pass


class AtsViewTestCase(TestCase):
    pass


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

        _o = ProjectWorker.objects.create(
            id=50001, user=_user, project=_proj, job=_job, invalid=True)
        _s = str(_o)
        self.assertEqual(
            _s, '50001 : testuser1 (projname200 - job100) [invalid]')

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


class TestLib(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_format_totaltime(self):
        # easy
        _delta = datetime.timedelta(days=0, hours=0, minutes=0, seconds=0)
        _result = format_totaltime(_delta)
        self.assertEqual(_result, '0:00')

        # min 24h
        _delta = datetime.timedelta(days=0, hours=23, minutes=59, seconds=0)
        _result = format_totaltime(_delta)
        self.assertEqual(_result, '23:59')

        # over 24h
        _delta = datetime.timedelta(days=0, hours=24, minutes=0, seconds=0)
        _result = format_totaltime(_delta)
        self.assertEqual(_result, '24:00')

        # min 100h
        _delta = datetime.timedelta(days=4, hours=3, minutes=59, seconds=0)
        _result = format_totaltime(_delta)
        self.assertEqual(_result, '99:59')

        # over100h
        _delta = datetime.timedelta(days=4, hours=4, minutes=00, seconds=0)
        _result = format_totaltime(_delta)
        self.assertEqual(_result, '100:00')

    def test_format_hours_float(self):
        # easy
        _delta = datetime.timedelta(days=0, hours=0, minutes=0, seconds=0)
        _result = format_hours_float(_delta)
        self.assertEqual(_result, 0.0)

        # 15min = a quarter
        _delta = datetime.timedelta(days=0, hours=23, minutes=15, seconds=0)
        _result = format_hours_float(_delta)
        self.assertEqual(_result, 23.25)

        # 30min = a harf
        _delta = datetime.timedelta(days=0, hours=23, minutes=30, seconds=0)
        _result = format_hours_float(_delta)
        self.assertEqual(_result, 23.5)

        # 45min = three quarters
        _delta = datetime.timedelta(days=0, hours=23, minutes=45, seconds=0)
        _result = format_hours_float(_delta)
        self.assertEqual(_result, 23.75)

        # convert to hour from days
        _delta = datetime.timedelta(days=4, hours=3, minutes=45, seconds=0)
        _result = format_hours_float(_delta)
        self.assertEqual(_result, 99.75)

    def test_validate_password(self):
        _ret = None

        _ret = validate_password("12345")
        self.assertEqual(_ret, False)

        _ret = validate_password("123456")
        self.assertEqual(_ret, True)

        _ret = validate_password("1234567")
        self.assertEqual(_ret, True)


class Ats404ViewTestCase(AtsViewTestCase):
    fixtures = ['test_views.json']
    client_class = AtsTestClient
    view_name = ''
    _password = 'passpass'

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            'testuser1',
            'testuser1@example.com',
            self._password)

    def tearDown(self):
        pass

    def test_404(self):
        _response = self.client.get('/ats/zzz/')
        self.assertEqual(_response.status_code, 404)

        _request = self.factory.get('/ats/zzz/')
        _responsev = error404(_request)
        self.assertEqual(_responsev.status_code, 404)
        self.assertTrue(_responsev.content.find(b'404 NOT FOUND'))


class Ats500ViewTestCase(AtsViewTestCase):
    fixtures = ['test_views.json']
    client_class = AtsTestClient
    view_name = 'ats:error_internal'
    _password = 'passpass'

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            'testuser1',
            'testuser1@example.com',
            self._password)

    def tearDown(self):
        pass

    def test_500(self):
        try:
            _response = self.client.get(reverse(self.view_name))
        except Exception as e:
            pass
        else:
            self.fail()


class IndexViewTestCase(AtsViewTestCase):
    fixtures = ['test_views.json']
    client_class = AtsTestClient
    view_name = 'ats:index'
    _password = 'passpass'

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            'testuser1',
            'testuser1@example.com',
            self._password)

    def tearDown(self):
        pass

    def test_index(self):
        _response = self.client.get(reverse('ats:top'))
        self.assertEqual(_response.status_code, 302)

        _request = self.factory.get(reverse('ats:top'))
        _responsev = index(_request)
        self.assertEqual(_responsev.status_code, 302)


class LoginViewTestCase(AtsViewTestCase):
    fixtures = ['test_views.json']
    client_class = AtsTestClient
    view_name = ''
    _password = 'passpass'

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            'testuser1',
            'testuser1@example.com',
            self._password)

    def tearDown(self):
        pass

    def test_login_success(self):
        self.client.logout()

        # if not login
        _response = self.client.get(reverse('ats:login_view'))
        self.assertEqual(_response.status_code, 200)

        # login
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get(reverse('ats:login_view'))
        self.assertRedirects(_response,
                             expected_url=reverse('ats:top'),
                             status_code=302,
                             target_status_code=200)

        # logout
        _response = self.client.get(reverse('ats:logout_view'))
        self.assertRedirects(_response,
                             expected_url=reverse('ats:login_view'),
                             status_code=302,
                             target_status_code=200)

    def test_loginform(self):
        # success login
        _response = self.client.post(
            reverse('ats:login_view'),
            {'username': self.user.username,
             'password': self._password})
        self.assertRedirects(_response,
                             expected_url=reverse('ats:top'),
                             status_code=302,
                             target_status_code=200)

        # wrong password
        _response = self.client.post(
            reverse('ats:login_view'),
            {'username': self.user.username,
             'password': 'dummypass'})
        self.assertEqual(_response.status_code, 200)

        # wrong user and password
        _response = self.client.post(
            reverse('ats:login_view'),
            {'username': 'dummyuser',
             'password': 'dummypass'})
        self.assertEqual(_response.status_code, 200)

    def test_login_fail_password_miss(self):
        self.client.logout()

        # if not login
        _response = self.client.get('/ats/login/')
        self.assertEqual(_response.status_code, 200)

        _result = self.client.login(username=self.user.username,
                                    password="dummypass")
        self.assertFalse(_result)

        _response = self.client.get('/ats/login/')
        self.assertEqual(_response.status_code, 200)

    def test_login_fail(self):
        self.client.logout()

        # if not login
        _response = self.client.get('/ats/login/')
        self.assertEqual(_response.status_code, 200)

        _result = self.client.login(username="dummyuser",
                                    password="12345678")
        self.assertFalse(_result)

        _response = self.client.get('/ats/login/')
        self.assertEqual(_response.status_code, 200)


class TopViewTestCase(AtsViewTestCase):
    fixtures = ['test_views.json']
    client_class = AtsTestClient
    view_name = 'ats:top'
    _password = 'passpass'

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            'testuser1',
            'testuser1@example.com',
            self._password)

    def tearDown(self):
        pass

    def test_top(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get(reverse(self.view_name))
        self.assertEqual(_response.status_code, 200)


class QueryViewTestCase(AtsViewTestCase):
    fixtures = ['test_views.json']
    client_class = AtsTestClient
    view_name = 'ats:query'
    _password = 'passpass'

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            'testuser1',
            'testuser1@example.com',
            self._password)

    def tearDown(self):
        pass

    def test_query(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get(reverse(self.view_name))
        self.assertEqual(_response.status_code, 200)


class ManageViewTestCase(AtsViewTestCase):
    fixtures = ['test_views.json']
    client_class = AtsTestClient
    view_name = 'ats:manage'
    _password = 'passpass'

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            'testuser1',
            'testuser1@example.com',
            self._password)

    def tearDown(self):
        pass

    def test_manage(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get(reverse(self.view_name))
        self.assertEqual(_response.status_code, 200)


class ManageChpasswdViewTestCase(AtsViewTestCase):
    fixtures = ['test_views.json']
    client_class = AtsTestClient
    view_name = 'ats:manage_chpasswd'
    _password = 'passpass'

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            'testuser1',
            'testuser1@example.com',
            self._password)

    def tearDown(self):
        pass

    def test_manage_chpasswd(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get(reverse(self.view_name))
        self.assertEqual(_response.status_code, 200)


class SummaryProjectViewTestCase(AtsViewTestCase):
    fixtures = ['test_views.json']
    client_class = AtsTestClient
    view_name = 'ats:summary_p'
    _password = 'passpass'

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            'testuser1',
            'testuser1@example.com',
            self._password)

    def tearDown(self):
        pass

    def test_summary_project(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get(reverse(self.view_name))
        self.assertEqual(_response.status_code, 200)


class SummaryJobViewTestCase(AtsViewTestCase):
    fixtures = ['test_views.json']
    client_class = AtsTestClient
    view_name = 'ats:summary_j'
    _password = 'passpass'

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            'testuser1',
            'testuser1@example.com',
            self._password)

    def tearDown(self):
        pass

    def test_summary_job(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get(reverse(self.view_name))
        self.assertEqual(_response.status_code, 200)


class SummaryUserViewTestCase(AtsViewTestCase):
    fixtures = ['test_views.json']
    client_class = AtsTestClient
    view_name = 'ats:summary_u'
    _password = 'passpass'

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            'testuser1',
            'testuser1@example.com',
            self._password)

    def tearDown(self):
        pass

    def test_summary_user(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get(reverse(self.view_name))
        self.assertEqual(_response.status_code, 200)


class RegistViewTestCase(AtsViewTestCase):
    fixtures = ['test_views.json']
    client_class = AtsTestClient
    view_name = 'ats:regist'
    _password = 'passpass'

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            'testuser1',
            'testuser1@example.com',
            self._password)

    def tearDown(self):
        pass

    def test_regist(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get(reverse(self.view_name))
        self.assertEqual(_response.status_code, 200)

    def test_regist_get_dateselect(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get(
            reverse(self.view_name), {'submit_type': 'dateselect'})
        self.assertEqual(_response.status_code, 200)

    def test_regist_post_regist(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.post(
            reverse(self.view_name), {
                'submit_type': 'regist',
                'regist_date': '2015-04-15',
                'project_id': '1',
            })
        self.assertEqual(_response.status_code, 200)
