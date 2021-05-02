#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import codecs
import json
import time
import datetime
import re
import logging
from datetime import date

import django
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseNotFound,
    QueryDict)
from django.forms.fields import ChoiceField
from django.template import loader, Context, RequestContext
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.forms import ModelForm
from django.db.models import Sum, Q
from django.db import transaction
from django.utils import timezone
from django.apps import apps
from ats.models import *


logger = logging.getLogger(__name__)
ats_settings = apps.get_app_config('ats')


def error500(request):
    return my_render(request, 'ats/500.html', {}, status_code=500)


def error404(request, exception=HttpResponseNotFound):
    return my_render(request, 'ats/404.html', {}, status_code=404)


def format_totaltime(td):
    totalhour = (td.days * 24) + int(td.seconds / 3600)
    minute = int(td.seconds / 60) - (int(td.seconds / 3600) * 60)

    return '%d:%02d' % (totalhour, minute)


def format_hours_float(td):
    return (td.days * 24) + (td.seconds / 3600.0)


def errorinternal(request):
    """
    for test. always 500 error.
    """
    raise Exception('ErrorInternalView')


def index(request):
    """
    if request.:
        return HttpResponseRedirect('/top/')
    else:
        return HttpResponseRedirect('/login/')
    """
    return HttpResponseRedirect(reverse('ats:top'))


@login_required
def top(request):
    return my_render(request, 'ats/top/index.html', {})


def login_view(request):
    error_reason = 0

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)

                    if 'next' in request.GET:
                        nextpage = request.GET.get('next')
                    else:
                        nextpage = reverse('ats:top')

                    return HttpResponseRedirect(nextpage)
                else:
                    error_reason = 1
            else:
                form = LoginForm()
                error_reason = 2
        else:
            form = LoginForm()
            error_reason = 3
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('ats:top'))
        else:
            form = LoginForm()

    return my_render(request, 'ats/login/login.html', {
        'form': form,
        'error_reason': error_reason
    })


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('ats:login_view'))


@login_required
def regist(request):
    if (request.method == 'POST') and ('submit_type' in request.POST):
        regist_count = 0

        if 'regist' in request.POST['submit_type']:
            logger.info('IN submit_type = regist')

            re_form = RegistForm(request.POST)
            if re_form.is_valid():
                regist_date = re_form.cleaned_data['regist_date']
                sel_project = re_form.cleaned_data['project_id']

                # RegistSelect form
                rs_form = RegistSelectForm(
                    user=request.user,
                    initial={'regist_date': regist_date,
                             'projectlist': sel_project})

                # Regist form
                checkregist = request.POST.getlist('registcheck')
                uttid = request.POST.getlist('uttid')
                tasktime_hour = request.POST.getlist('tasktime_hour')
                tasktime_min = request.POST.getlist('tasktime_min')

                targetindexlist = []
                # get index from form data
                for i in range(len(uttid)):
                    for c in checkregist:
                        if uttid[i] == c:
                            targetindexlist.append(i)
                            break

                if 0 < len(targetindexlist):
                    logger.info('check count = %s' % (len(targetindexlist)))
                else:
                    logger.info('no check.')

                # insert or update usedtasktime
                id_re = re.compile(r'p([0-9]{1,})_t([0-9]{1,})')

                # parse post data to adjust database model.
                _inputdatas = []
                for i in targetindexlist:
                    _o = {}
                    m = id_re.search(uttid[i])
                    _o['pid'], _o['tid'] = m.group(1, 2)

                    _o['ud_ttime'] = datetime.time(
                        hour=int(tasktime_hour[i]),
                        minute=int(tasktime_min[i]))

                    _inputdatas.append(_o)

                with transaction.atomic():
                    try:
                        for i in _inputdatas:
                            if (0 == i['ud_ttime'].hour) and \
                               (0 == i['ud_ttime'].minute):
                                UsedTaskTime.objects.filter(
                                    user=request.user,
                                    project=Project.objects.get(pk=i['pid']),
                                    task=Task.objects.get(pk=i['tid']),
                                    taskdate=regist_date).delete()
                            else:
                                uttinst, _created = \
                                  UsedTaskTime.objects.get_or_create(
                                      user=request.user,
                                      project=Project.objects.get(pk=i['pid']),
                                      task=Task.objects.get(pk=i['tid']),
                                      taskdate=regist_date,
                                      defaults={'tasktime': i['ud_ttime']})
                                if not _created:
                                    uttinst.tasktime = i['ud_ttime']
                                    uttinst.save()
                    except Exception as e:
                        msg = "EXCEPT: fail save or delete. msg=%s,%s" % (
                            sys.exc_info()[1], sys.exc_info()[2])
                        logger.error(msg)
                        logger.error("do rollback")
                        # add notify message on template.
                        raise Exception(msg)
            else:
                logger.warning('RegistForm.is_valid = False')

                rs_form = RegistSelectForm(user=request.user)
                regist_date = datetime.date.today()
                sel_project = (rs_form.fields['projectlist'].choices[0])[0]

                re_form = RegistForm(initial={'regist_date': regist_date,
                                              'project_id': sel_project})
    elif request.method == 'GET':
        logger.info('regist : method=GET, submit_type={}'.format(
            request.GET.get('submit_type')))

        if 'dateselect' == request.GET.get('submit_type', ''):
            rs_form = RegistSelectForm(request.GET, user=request.user)
            if rs_form.is_valid():
                regist_date = rs_form.cleaned_data['regist_date']
                sel_project = rs_form.cleaned_data['projectlist']
            else:
                logger.warning('RegistSelectForm.is_valid = False (1)')
                logger.warning('rs_form.errors = {}'.format(rs_form.errors))

                #
                # check parameter
                #
                try:
                    regist_date = datetime.datetime.strptime(
                        request.GET.get('regist_date'), '%Y-%m-%d')
                    regist_date = request.GET.get('regist_date')
                except Exception as e:
                    logger.warning(
                        'regist_date is wrong. regist_date = {}'.format(
                         request.GET.get('regist_date')))
                    regist_date = datetime.date.today().strftime('%Y-%m-%d')

                # if change date, may no have project at the date.
                _has_projects = get_projects_in_date(request.user, regist_date)
                if 0 < len(_has_projects):
                    for p in _has_projects:
                        if p.project_id == int(request.GET.get('projectlist')):
                            # continue has projectlist.
                            sel_project = int(request.GET.get('projectlist'))
                            break
                    else:
                        sel_project = _has_projects[0].project_id
                else:
                    sel_project = -1

                # create dummy GET parameter.
                qd_get_dateselect = QueryDict('', mutable=True)
                qd_get_dateselect['regist_date'] = regist_date
                qd_get_dateselect['projectlist'] = sel_project
                qd_get_dateselect['submit_type'] = 'dateselect'

                # re-try create form with validated paramater.
                rs_form = RegistSelectForm(
                    qd_get_dateselect, user=request.user)
                if rs_form.is_valid():
                    logger.debug("RegistSelectForm.is_valid = True  (2)")

                    regist_date = rs_form.cleaned_data['regist_date']
                    sel_project = rs_form.cleaned_data['projectlist']
                else:
                    logger.warning('RegistSelectForm.is_valid = False (2)')
                    logger.warning('rs_form.errors = {}'.format(
                        rs_form.errors))

                    # force default screen. (without submit_type=dateselect)
                    rs_form = RegistSelectForm(user=request.user)
                    regist_date = datetime.date.today()
                    sel_project = (rs_form.fields['projectlist'].choices[0])[0]

            # re_form
            re_form = RegistForm(initial={'regist_date': regist_date,
                                          'project_id': sel_project})
        else:
            rs_form = RegistSelectForm(user=request.user)
            regist_date = datetime.date.today()
            sel_project = (rs_form.fields['projectlist'].choices[0])[0]

            re_form = RegistForm(initial={
                'regist_date': regist_date,
                'project_id': sel_project})
    else:
        logger.info('regist : method={}. unsupport. replace GET.'.format(
            request.method))

        rs_form = RegistSelectForm(user=request.user)
        regist_date = datetime.date.today()
        sel_project = (rs_form.fields['projectlist'].choices[0])[0]

        re_form = RegistForm(initial={'regist_date': regist_date,
                                      'project_id': sel_project})

    # get project
    try:
        project = Project.objects.get(id=sel_project)

        cursor_pjw = ProjectWorker.objects.filter(user=request.user)
        cursor_pjw = cursor_pjw.filter(project__id=project.id)
        cursor_pjw = cursor_pjw.filter(project__start_dt__lte=regist_date)
        cursor_pjw = cursor_pjw.filter(project__end_dt__isnull=True)
        cursor_pjw = cursor_pjw.filter(invalid=False)
        cursor_pjw = cursor_pjw.order_by('project__sortkey', 'job__sortkey')
    except Project.DoesNotExist as e:
        logger.warning('regist(): project is not found (id=%s)' % (
            sel_project))
        cursor_pjw = []

    datalist = []
    existdatalist = []

    # select exist usedtasktime
    cursor_u = UsedTaskTime.objects.filter(user=request.user)
    cursor_u = cursor_u.filter(taskdate=regist_date)
    cursor_u = cursor_u.select_related('project', 'task', 'task__job')
    cursor_u = cursor_u.order_by('project__sortkey',
                                 'task__job__sortkey', 'task__sortkey')

    day_total = datetime.timedelta()

    for u in cursor_u:
        uttobj = {'projectname': u.project.name,
                  'jobname': u.task.job.name,
                  'taskname': u.task.name,
                  'tasktime_hour': u.tasktime.hour,
                  'tasktime_min': u.tasktime.minute}

        existdatalist.append(uttobj)

        day_total = day_total + datetime.timedelta(
            hours=u.tasktime.hour, minutes=u.tasktime.minute)

    # create input form
    for pjw in cursor_pjw:
        usedtasktimelist = []

        # task
        cursor_t = Task.objects.filter(job=pjw.job)
        cursor_t = cursor_t.filter(invalid=False)
        cursor_t = cursor_t.select_related('job')
        cursor_t = cursor_t.order_by('sortkey')

        for t in cursor_t:
            utt = {'job_id': t.job.id,
                   'job_name': t.job.name,
                   'task_id': t.id,
                   'task_name': t.name,
                   'tasktime_hour': 0,
                   'tasktime_min': 0}

            for u in cursor_u:
                if (pjw.project == u.project) and (t.id == u.task_id):
                    utt['tasktime_hour'] = u.tasktime.hour
                    utt['tasktime_min'] = u.tasktime.minute
                    break

            usedtasktimelist.append(utt)

        d = {'project_id': pjw.project.id,
             'project_name': pjw.project.name,
             'usedtasktimelist': usedtasktimelist}
        datalist.append(d)

    # enable select hour and minute.
    hourlist = []
    for i in range(ats_settings.ATS_REGIST_HOUR_MAX):
        hourlist.append(i)

    minutelist = []
    for i in ats_settings.ATS_REGIST_MIN_SPAN:
        minutelist.append(i)

    day_total_hour = int(day_total.seconds / 3600)
    day_total_min = int((day_total.seconds - (day_total_hour * 3600)) / 60)

    return my_render(request, 'ats/regist/regist.html', {
        'form': rs_form,
        'regist_form': re_form,
        'regist_date': regist_date,
        'projectid': sel_project,
        'existdatalist': existdatalist,
        'datalist': datalist,
        'hourlist': hourlist,
        'minutelist': minutelist,
        'oneday_total_hour': day_total_hour,
        'oneday_total_min': day_total_min
    })


@login_required
def summary_p(request):
    totallist = []
    p_monthlist = []
    pj_monthlist = []
    datelist = []
    tasklist = []
    is_show_taskdetail = False
    from_date = ''
    to_date = ''

    if request.method == 'POST':
        form = SummaryProjectForm(request.POST)
        if form.is_valid():
            project = form.cleaned_data['projectlist']
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            is_show_taskdetail = form.cleaned_data['is_show_taskdetail']

            logger.debug('IN summary_p : is_show_taskdetail(%s)' % (
                is_show_taskdetail))
            _starttime = timezone.localtime()
            logger.debug('starttime: %s' % (_starttime))

            # calc date
            cursor = UsedTaskTime.objects.filter(project=project)
            if from_date:
                cursor = cursor.filter(taskdate__gte=from_date)

            if to_date:
                cursor = cursor.filter(taskdate__lte=to_date)

            cursor = cursor.values('project__name').annotate(
                total_tasktime=Sum('tasktime'))

            totallist = list(cursor)

            # convert hour
            for r in totallist:
                r['total_tasktime'] = format_totaltime(r['total_tasktime'])

            # calc task
            if is_show_taskdetail:
                cursor = UsedTaskTime.objects.filter(project=project)

                if from_date:
                    cursor = cursor.filter(taskdate__gte=from_date)

                if to_date:
                    cursor = cursor.filter(taskdate__lte=to_date)

                cursor = cursor.order_by('taskdate',
                                         'task__job__sortkey',
                                         'task__sortkey')

                tasklist = list(cursor)

            # calc date
            cursor = UsedTaskTime.objects.filter(project=project)

            if from_date:
                cursor = cursor.filter(taskdate__gte=from_date)

            if to_date:
                cursor = cursor.filter(taskdate__lte=to_date)

            cursor = cursor.values('project__name', 'taskdate').annotate(
                date_tasktime=Sum('tasktime'))
            cursor = cursor.order_by('taskdate')
            datelist = list(cursor)
            # convert hour
            for r in datelist:
                r['date_tasktime'] = format_totaltime(r['date_tasktime'])

            # get month list for project
            cursor = UsedTaskTime.objects.filter(project=project)

            if from_date:
                cursor = cursor.filter(taskdate__gte=from_date)

            if to_date:
                cursor = cursor.filter(taskdate__lte=to_date)

            cursor = cursor.extra({
                'year': '''date_part('year', taskdate)''',
                'month': '''date_part('month', taskdate)'''}).\
                values('project__name', 'year', 'month').\
                annotate(month_tasktime=Sum('tasktime')).\
                order_by('year', 'month')

            p_monthlist = list(cursor)
            for r in p_monthlist:
                # year and month return double, so cast integer.
                r['year'] = int(r['year'])
                r['month'] = int(r['month'])
                # convert timedelta to HHH:MM
                r['month_tasktime_float'] = format_hours_float(
                    r['month_tasktime'])
                r['month_tasktime'] = format_totaltime(r['month_tasktime'])

            # get month list for project,job
            pj_cursor = UsedTaskTime.objects.filter(project=project)

            if from_date:
                pj_cursor = pj_cursor.filter(taskdate__gte=from_date)

            if to_date:
                pj_cursor = pj_cursor.filter(taskdate__lte=to_date)

            pj_cursor = pj_cursor.extra({
                'year': '''date_part('year', taskdate)''',
                'month': '''date_part('month', taskdate)'''}).\
                values('project__name', 'task__job__name', 'year', 'month').\
                annotate(month_tasktime=Sum('tasktime')).\
                order_by('year', 'month')

            pj_monthlist = list(pj_cursor)
            for r in pj_monthlist:
                # year and month return double, so cast integer.
                r['year'] = int(r['year'])
                r['month'] = int(r['month'])
                # convert timedelta to HHH:MM
                r['month_tasktime_float'] = format_hours_float(
                    r['month_tasktime'])
                r['month_tasktime'] = format_totaltime(r['month_tasktime'])

            _endtime = timezone.localtime()
            logger.debug('endtime  : %s' % (_endtime))
            logger.debug('dur: %s' % (_endtime - _starttime))
        else:
            form = SummaryProjectForm()
    else:
        form = SummaryProjectForm()

    return my_render(request, 'ats/summary/project.html', {
        'form': form,
        'totallist': totallist,
        'p_monthlist': p_monthlist,
        'pj_monthlist': pj_monthlist,
        'datelist': datelist,
        'tasklist': tasklist,
        'is_show_taskdetail': is_show_taskdetail,
        'from_date': from_date,
        'to_date': to_date
    })


@login_required
def summary_j(request):
    jobdatalist = []
    pj_monthlist = []
    j_monthlist = []
    taskdatalist = []

    if request.method == 'POST':
        form = SummaryJobForm(request.POST)
        if form.is_valid():
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            joblist = form.cleaned_data['joblist']

            # calc job
            cursor = UsedTaskTime.objects.filter(task__job__in=joblist)

            if from_date:
                cursor = cursor.filter(taskdate__gte=from_date)

            if to_date:
                cursor = cursor.filter(taskdate__lte=to_date)

            cursor = cursor.order_by('project__sortkey',
                                     'task__job__sortkey')

            cursor = cursor.values('project__name',
                                   'task__job__name').annotate(
                total_tasktime=Sum('tasktime'))

            jobdatalist = list(cursor)

            # convert hour
            for r in jobdatalist:
                r['total_tasktime'] = format_totaltime(r['total_tasktime'])

            # calc task
            cursor = UsedTaskTime.objects.filter(task__job__in=joblist)

            if from_date:
                cursor = cursor.filter(taskdate__gte=from_date)

            if to_date:
                cursor = cursor.filter(taskdate__lte=to_date)

            cursor = cursor.order_by('project__sortkey',
                                     'task__job__sortkey',
                                     'task__sortkey')

            cursor = cursor.values('project__name',
                                   'task__job__name',
                                   'task__name').annotate(
                total_tasktime=Sum('tasktime'))

            taskdatalist = list(cursor)

            # convert hour
            for r in taskdatalist:
                r['total_tasktime'] = format_totaltime(r['total_tasktime'])

            # get month list for job
            cursor = UsedTaskTime.objects.filter(task__job__in=joblist)

            if from_date:
                cursor = cursor.filter(taskdate__gte=from_date)

            if to_date:
                cursor = cursor.filter(taskdate__lte=to_date)

            cursor = cursor.extra({
                'year': '''date_part('year', taskdate)''',
                'month': '''date_part('month', taskdate)'''}).\
                values('task__job__name', 'year', 'month').\
                annotate(month_tasktime=Sum('tasktime')).\
                order_by('year', 'month')

            j_monthlist = list(cursor)
            for r in j_monthlist:
                # year and month return double, so cast integer.
                r['year'] = int(r['year'])
                r['month'] = int(r['month'])
                # convert timedelta to HHH:MM
                r['month_tasktime_float'] = format_hours_float(
                    r['month_tasktime'])
                r['month_tasktime'] = format_totaltime(r['month_tasktime'])

            # get month list for project,job
            pj_cursor = UsedTaskTime.objects.filter(task__job__in=joblist)

            if from_date:
                pj_cursor = pj_cursor.filter(taskdate__gte=from_date)

            if to_date:
                pj_cursor = pj_cursor.filter(taskdate__lte=to_date)

            pj_cursor = pj_cursor.extra({
                'year': '''date_part('year', taskdate)''',
                'month': '''date_part('month', taskdate)'''}).\
                values('project__name', 'task__job__name', 'year', 'month').\
                annotate(month_tasktime=Sum('tasktime')).\
                order_by('year', 'month')

            pj_monthlist = list(pj_cursor)
            for r in pj_monthlist:
                # year and month return double, so cast integer.
                r['year'] = int(r['year'])
                r['month'] = int(r['month'])
                # convert timedelta to HHH:MM
                r['month_tasktime_float'] = format_hours_float(
                    r['month_tasktime'])
                r['month_tasktime'] = format_totaltime(r['month_tasktime'])
        else:
            form = SummaryJobForm()
    else:
        form = SummaryJobForm()

    return my_render(request, 'ats/summary/job.html', {
        'form': form,
        'jobdata': jobdatalist,
        'pj_monthlist': pj_monthlist,
        'j_monthlist': j_monthlist,
        'taskdata': taskdatalist
    })


@login_required
def summary_u(request):
    userdatalist = []
    taskdatalist = []
    datedatalist = []
    datesummarylist = []
    monthlist = []

    if request.method == 'POST':
        form = SummaryUserForm(request.POST)
        if form.is_valid():
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            userlist = form.cleaned_data['userlist']

            # calc user
            cursor = UsedTaskTime.objects.filter(user__in=userlist)

            if from_date:
                cursor = cursor.filter(taskdate__gte=from_date)

            if to_date:
                cursor = cursor.filter(taskdate__lte=to_date)

            # date data
            cursor_date = cursor.order_by('taskdate')
            cursor_date = cursor_date.values('project__name',
                                             'taskdate',
                                             'task__job__name',
                                             'task__name',
                                             'user__last_name',
                                             'user__first_name',
                                             'tasktime')

            datedatalist = list(cursor_date)

            # date data summary
            cursor_datesammary = cursor.order_by('taskdate')
            cursor_datesammary = cursor_datesammary.values(
                'taskdate',
                'user__last_name',
                'user__first_name',
                'tasktime')

            cursor_datesammary = cursor_datesammary.values(
                'taskdate',
                'user__last_name',
                'user__first_name').annotate(
                total_tasktime=Sum('tasktime'))
            datesummarylist = list(cursor_datesammary)

            # convert hour
            for r in datesummarylist:
                r['total_tasktime'] = format_totaltime(r['total_tasktime'])

            # user summary
            cursor = cursor.order_by('project__sortkey',
                                     'task__job__sortkey')

            cursor = cursor.values('project__name',
                                   'task__job__name',
                                   'user__last_name',
                                   'user__first_name').annotate(
                total_tasktime=Sum('tasktime'))

            userdatalist = list(cursor)

            # convert hour
            for r in userdatalist:
                r['total_tasktime'] = format_totaltime(r['total_tasktime'])

            # calc task
            cursor = UsedTaskTime.objects.filter(user__in=userlist)
            cursor = cursor.order_by('project__sortkey',
                                     'task__job__sortkey',
                                     'task__sortkey')

            if from_date:
                cursor = cursor.filter(taskdate__gte=from_date)

            if to_date:
                cursor = cursor.filter(taskdate__lte=to_date)

            cursor = cursor.values('project__name',
                                   'task__job__name',
                                   'task__name',
                                   'user__last_name',
                                   'user__first_name').annotate(
                total_tasktime=Sum('tasktime'))

            taskdatalist = list(cursor)

            # convert hour
            for r in taskdatalist:
                r['total_tasktime'] = format_totaltime(r['total_tasktime'])

            # get month list
            cursor = UsedTaskTime.objects.filter(user__in=userlist)

            if from_date:
                cursor = cursor.filter(taskdate__gte=from_date)

            if to_date:
                cursor = cursor.filter(taskdate__lte=to_date)

            cursor = cursor.extra({
                'year': '''date_part('year', taskdate)''',
                'month': '''date_part('month', taskdate)'''}).\
                values('user__username', 'year', 'month').\
                annotate(month_tasktime=Sum('tasktime')).\
                order_by('year', 'month')

            monthlist = list(cursor)
            for r in monthlist:
                # year and month return double, so cast integer.
                r['year'] = int(r['year'])
                r['month'] = int(r['month'])
                # convert timedelta to HHH:MM
                r['month_tasktime_float'] = format_hours_float(
                    r['month_tasktime'])
                r['month_tasktime'] = format_totaltime(r['month_tasktime'])
        else:
            form = SummaryUserForm()
    else:
        form = SummaryUserForm()

    return my_render(request, 'ats/summary/user.html', {
        'form': form,
        'userdata': userdatalist,
        'taskdata': taskdatalist,
        'datesummarydata': datesummarylist,
        'monthlist': monthlist,
        'datedetaildata': datedatalist
    })


@login_required
def query(request):
    return my_render(request, 'ats/query/index.html', {})


@login_required
def manage(request):
    return my_render(request, 'ats/manage/index.html', {})


def validate_password(password):
    if 6 <= len(password):
        return True
    else:
        return False


@login_required
def manage_chpasswd(request):
    message = ''

    if 'POST' == request.method:
        form = PasswordChangeForm(request.user, request.POST)

        # If True is form.is_valid(),
        # success to check old_password and
        # it is same to password1 and password2.
        if form.is_valid():
            p = form.clean_new_password2()

            if validate_password(p):
                form.save()
                message = 'success change password.'
            else:
                message = 'password is not good. not change password.'
        else:
            pass
    else:
        form = PasswordChangeForm(request.user)

    return my_render(request, 'ats/manage/chpasswd.html', {
        'form': form,
        'message': message
    })


def my_render(request, template_file, paramdict, status_code=200):
    response = render(request, template_file, paramdict)
    response.status_code = status_code

    return response


def get_thismonth_1st():
    _now = timezone.localtime()
    _ret = _now.replace(day=1)

    # logger.debug("get_thismonth_1st(): %s" % (_ret))
    return _ret


def get_localtime():
    _now = timezone.localtime()

    # logger.debug("get_localtime()    : %s" % (_now))
    return _now


def get_projects_in_date(request_user, regist_date):
    cursor = ProjectWorker.objects.filter(
        user=request_user).order_by('project__sortkey')

    cursor = cursor.filter(
        Q(project__start_dt__isnull=True) | Q(project__start_dt__lte=regist_date))
    cursor = cursor.filter(
        Q(project__end_dt__isnull=True) | Q(project__end_dt__gte=regist_date))
    cursor = cursor.distinct()

    return list(cursor)


class RegistSelectForm(forms.Form):
    regist_date = forms.DateField(
        label='regist_date', required=True,
        initial=lambda: get_localtime(),
        widget=forms.DateInput(attrs={"type": "date"}))
    projectlist = forms.ChoiceField(label='Project',
                                    choices=[('-1', '------')])
    submit_type = forms.CharField(initial='dateselect',
                                  widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        _user = kwargs.pop('user')
        super(RegistSelectForm, self).__init__(*args, **kwargs)

        cursor = ProjectWorker.objects.filter(user=_user).order_by(
            'project__sortkey')

        cmp_dt = self.fields['regist_date'].initial()
        if args:
            # parameter check
            try:
                datetime.datetime.strptime(
                    args[0]['regist_date'], '%Y-%m-%d')
                cmp_dt = args[0]['regist_date']
            except Exception as e:
                # parameter error. fallback default value.
                pass

        cursor = cursor.filter(
            Q(project__start_dt__isnull=True) | Q(project__start_dt__lte=cmp_dt))
        cursor = cursor.filter(
            Q(project__end_dt__isnull=True) | Q(project__end_dt__gte=cmp_dt))
        cursor = cursor.values(
            'project__id', 'project__name').distinct()

        pjlist = []
        for r in cursor:
            t = (r['project__id'], r['project__name'])
            pjlist.append(t)

        if 0 < len(pjlist):
            self.fields['projectlist'].choices = pjlist


class RegistForm(forms.Form):
    regist_date = forms.DateField(required=True,
                                  widget=forms.HiddenInput())
    project_id = forms.IntegerField(widget=forms.HiddenInput())
    submit_type = forms.CharField(initial='regist',
                                  widget=forms.HiddenInput())


class SummaryProjectForm(forms.Form):
    from_date = forms.DateField(label='from date', required=False,
                                initial=lambda: get_thismonth_1st(),
                                widget=forms.DateInput(attrs={"type": "date"}))
    to_date = forms.DateField(label='to date', required=False,
                              initial=lambda: get_localtime(),
                              widget=forms.DateInput(attrs={"type": "date"}))
    projectlist = forms.ModelChoiceField(
        label='Project',
        queryset=Project.objects.all().order_by('sortkey'))
    is_show_taskdetail = forms.BooleanField(label="show Task Detail",
                                            required=False)


class SummaryJobForm(forms.Form):
    from_date = forms.DateField(label='from date', required=False,
                                initial=lambda: get_thismonth_1st(),
                                widget=forms.DateInput(attrs={"type": "date"}))
    to_date = forms.DateField(label='to date', required=False,
                              initial=lambda: get_localtime(),
                              widget=forms.DateInput(attrs={"type": "date"}))
    joblist = forms.ModelMultipleChoiceField(
        label='job',
        required=True,
        queryset=Job.objects.all().order_by('sortkey'))


class MyUserModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        if ats_settings.ATS_IS_LASTNAME_FRONT:
            return "%s (%s %s) " % (
                obj.username, obj.last_name, obj.first_name)
        else:
            return "%s (%s %s) " % (
                obj.username, obj.first_name, obj.last_name)


class SummaryUserForm(forms.Form):
    from_date = forms.DateField(label='from date', required=False,
                                initial=lambda: get_thismonth_1st(),
                                widget=forms.DateInput(attrs={"type": "date"}))
    to_date = forms.DateField(label='to date', required=False,
                              initial=lambda: get_localtime(),
                              widget=forms.DateInput(attrs={"type": "date"}))
    userlist = MyUserModelMultipleChoiceField(
        label='user',
        required=True,
        queryset=User.objects.filter(is_active=True).order_by('id'))


class LoginForm(forms.Form):
    username = forms.CharField(label='username',
                               max_length=256,
                               required=True)
    password = forms.CharField(label='password',
                               max_length=256,
                               widget=forms.PasswordInput(),
                               required=True)
