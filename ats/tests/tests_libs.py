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

    def test_export_csv_task(self):
        _datalist = [
            {
                'taskdate': datetime.date(year=2015, month=4, day=5),
                'project__name': 'projname1',
                'project__external_project__code': 'abcd',
                'task__job__name': 'jobname1',
                'task__name': 'taskname1',
                'user__first_name': 'user1_first',
                'user__last_name': 'user1_last',
                'tasktime': datetime.time(hour=1, minute=15),
                'task__userdata1': '111',
                'task__userdata2': '222',
                'task__userdata3': '333',
                'task__userdata4': '444',
                'task__userdata5': '555',
             },
        ]

        #
        # if _add_header is True
        #
        _add_header = True
        _data_bin = export_csv_task(_datalist, _add_header, "\n")
        self.assertIsNotNone(_data_bin)
        print(_data_bin)

        _data_str = _data_bin.decode('utf8')
        _rows = _data_str.split("\n")

        _cols_0 = _rows[0].split(',')
        self.assertEqual(_cols_0[0], '"date"')
        self.assertEqual(_cols_0[1], '"project"')
        self.assertEqual(_cols_0[2], '"code"')
        self.assertEqual(_cols_0[3], '"job"')
        self.assertEqual(_cols_0[4], '"task"')
        self.assertEqual(_cols_0[5], '"user"')
        self.assertEqual(_cols_0[6], '"tasktime"')
        self.assertEqual(_cols_0[7], '"task_userdata1"')
        self.assertEqual(_cols_0[8], '"task_userdata2"')
        self.assertEqual(_cols_0[9], '"task_userdata3"')
        self.assertEqual(_cols_0[10], '"task_userdata4"')
        self.assertEqual(_cols_0[11], '"task_userdata5"')

        _cols_1 = _rows[1].split(',')
        self.assertEqual(_cols_1[0], '"2015-04-05"')
        self.assertEqual(_cols_1[1], '"projname1"')
        self.assertEqual(_cols_1[2], '"abcd"')
        self.assertEqual(_cols_1[3], '"jobname1"')
        self.assertEqual(_cols_1[4], '"taskname1"')
        self.assertEqual(_cols_1[5], '"user1_first user1_last"')
        self.assertEqual(_cols_1[6], '"1:15"')
        self.assertEqual(_cols_1[7], '"111"')
        self.assertEqual(_cols_1[8], '"222"')
        self.assertEqual(_cols_1[9], '"333"')
        self.assertEqual(_cols_1[10], '"444"')
        self.assertEqual(_cols_1[11], '"555"')

        #
        # if _add_header is False
        #
        _add_header = False
        _data_bin = export_csv_task(_datalist, _add_header, "\n")
        self.assertIsNotNone(_data_bin)
        print(_data_bin)

        _data_str = _data_bin.decode('utf8')
        _rows = _data_str.split("\n")

        _cols_1 = _rows[0].split(',')
        self.assertEqual(_cols_1[0], '"2015-04-05"')
        self.assertEqual(_cols_1[1], '"projname1"')
        self.assertEqual(_cols_1[2], '"abcd"')
        self.assertEqual(_cols_1[3], '"jobname1"')
        self.assertEqual(_cols_1[4], '"taskname1"')
        self.assertEqual(_cols_1[5], '"user1_first user1_last"')
        self.assertEqual(_cols_1[6], '"1:15"')
        self.assertEqual(_cols_1[6], '"1:15"')
        self.assertEqual(_cols_1[7], '"111"')
        self.assertEqual(_cols_1[8], '"222"')
        self.assertEqual(_cols_1[9], '"333"')
        self.assertEqual(_cols_1[10], '"444"')
        self.assertEqual(_cols_1[11], '"555"')
