#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import codecs
import time
import datetime
import logging
import csv
import six
from datetime import date

from django.apps import apps
from django.utils import timezone

logger = logging.getLogger(__name__)
ats_settings = apps.get_app_config('ats')


def get_user_realname(first_name, last_name):
    if ats_settings.ATS_IS_LASTNAME_FRONT:
        return '%s %s' % (last_name, first_name)
    else:
        return '%s %s' % (first_name, last_name)


def format_totaltime(td):
    totalhour = (td.days * 24) + int(td.seconds / 3600)
    minute = int(td.seconds / 60) - (int(td.seconds / 3600) * 60)

    return '%d:%02d' % (totalhour, minute)


def format_hours_float(td):
    return (td.days * 24) + (td.seconds / 3600.0)


def format_time(timedata):
    return '%d:%02d' % (timedata.hour, timedata.minute)


def get_localtime():
    _now = timezone.localtime()

    # logger.debug("get_localtime()    : %s" % (_now))
    return _now


def get_thismonth_1st():
    _now = timezone.localtime()
    _ret = _now.replace(day=1)

    # logger.debug("get_thismonth_1st(): %s" % (_ret))
    return _ret


def export_csv_task(datalist, add_header, new_line):
    _s = ''
    if six.PY2:
        bufffer = six.BytesIO()
    else:
        bufffer = six.StringIO()

    try:
        if True:
            _writer = csv.writer(
                bufffer, lineterminator=new_line,
                quotechar='"', quoting=csv.QUOTE_ALL)

            if add_header:
                _header = ['date', 'project', 'code', 'job', 'task', 'user', 'tasktime']
                _writer.writerow(_header)

            for d in datalist:
                _line = []

                _date = d['taskdate'].isoformat()
                _line.append(_date)

                _line.append(d['project__name'])

                if d['project__external_project__code']:
                    _line.append(d['project__external_project__code'])
                else:
                    _line.append('')

                _line.append(d['task__job__name'])
                _line.append(d['task__name'])
                _line.append(get_user_realname(d['user__first_name'], d['user__last_name']))
                _line.append(format_time(d['tasktime']))

                if six.PY2:
                    for i in range(len(_line)):
                        _line[i] = _line[i].encode('utf8')

                _writer.writerow(_line)

            _s = bufffer.getvalue()
            bufffer.close()

            if six.PY3:
                _s = _s.encode('utf8')
    except Exception as e:
        logger.error('fail export_csv_task().')
        logger.error('EXCEPT: export_csv_task(). e=%s, msg1=%s,msg2=%s',
                     e, sys.exc_info()[1], sys.exc_info()[2])

        return None

    return _s
