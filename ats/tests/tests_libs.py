import datetime
from datetime import timedelta, time

from django.test import TestCase

from ..libs import (
    get_user_realname,
    format_totaltime,
    format_hours_float,
    format_time,
    get_localtime,
    get_thismonth_1st,
    export_csv_task,
)


class TestLib(TestCase):
    fixtures = ['test_views.json']

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

    def test_get_user_realname(self):
        _s = get_user_realname('aaa', 'bbb', False)
        self.assertEqual(_s, 'aaa bbb')

        _s = get_user_realname('aaa', 'bbb', True)
        self.assertEqual(_s, 'bbb aaa')

    def test_format_time(self):
        _t = datetime.time(hour=1, minute=5)
        _s = format_time(_t)
        self.assertEqual(_s, '1:05')
