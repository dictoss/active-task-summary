from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User

import datetime
from datetime import timedelta

from .views import (
    format_totaltime,
    format_hours_float,
    validate_password,
    error404,
    error500)


class AtsTestClient(Client):
    pass


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


class TestViews(TestCase):
    fixtures = ['test_views.json']
    client_class = AtsTestClient
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
        self.assertEqual(_responsev.status_code, 200)
        self.assertTrue(_responsev.content.find(b'404 NOT FOUND'))

    def test_index(self):
        _response = self.client.get('/ats/top/')
        self.assertEqual(_response.status_code, 302)

    def test_login_top(self):
        # if not login
        _response = self.client.get('/ats/top/')
        self.assertEqual(_response.status_code, 302)

        # login
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        # enable access logined.
        _response = self.client.get('/ats/top/')
        self.assertEqual(_response.status_code, 200)
        self.client.logout()

    def test_query(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get('/ats/query/')
        self.assertEqual(_response.status_code, 200)

    def test_manage(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get('/ats/manage/')
        self.assertEqual(_response.status_code, 200)

    def test_manage_chpasswd(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get('/ats/manage/')
        self.assertEqual(_response.status_code, 200)

    def test_summary_project(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get('/ats/summary/project/')
        self.assertEqual(_response.status_code, 200)

    def test_summary_job(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get('/ats/summary/job/')
        self.assertEqual(_response.status_code, 200)

    def test_summary_user(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get('/ats/summary/user/')
        self.assertEqual(_response.status_code, 200)

    def test_regist(self):
        _result = self.client.login(username=self.user.username,
                                    password=self._password)
        self.assertTrue(_result)

        _response = self.client.get('/ats/regist/')
        self.assertEqual(_response.status_code, 200)
