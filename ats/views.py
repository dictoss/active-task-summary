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
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.forms.fields import ChoiceField
from django.template import loader, Context, RequestContext
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf
from django.forms import ModelForm
from django.db.models import Sum, Q
from django.db import transaction
from ats.models import *
from ats import ats_settings

APP_NAME = 'ats'
APP_LONGNAME = 'Active Task Summary'
APP_VERSION = '0.3.0'
APP_AUTHER = 'dictoss'


formatter = logging.Formatter(ats_settings.LOG_FORMAT)
h = logging.FileHandler(ats_settings.LOG_PATH)
h.setFormatter(formatter)

logger = logging.getLogger(APP_NAME)
logger.setLevel(ats_settings.LOG_LEVEL)
logger.addHandler(h)


def error500(request):
    return render_to_response('500.html', {})


def error404(request):
    return render_to_response('404.html', {})


def get_url_prefix():
    return '%s/%s' % (settings.APP_MOUNTDIR, APP_NAME)


def format_totaltime(td):
    totalhour = (td.days * 24) + int(td.seconds / 3600)
    minute = int(td.seconds / 60) - (int(td.seconds / 3600) * 60)

    return '%d:%02d' % (totalhour, minute)


def index(request):
    """
    if request.:
        return HttpResponseRedirect('/top/')
    else:
        return HttpResponseRedirect('/login/')
    """
    return HttpResponseRedirect('%s/top' % get_url_prefix())


@login_required
def top(request):
    return my_render_to_response(request,
                                 'top/index.html', {})
    #return HttpResponse("""<html><body>this is top.</body></html>""")


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
                        nextpage = '%s/top' % get_url_prefix()

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
        if request.user.is_authenticated():
            return HttpResponseRedirect('%s/top' % get_url_prefix())
        else:
            form = LoginForm()

    return my_render_to_response(request,
                                 'login/login.html',
                                 {'form': form,
                                  'error_reason': error_reason})


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('%s/login/' % get_url_prefix())


@login_required
def regist(request):
    if request.method == 'POST':
        regist_count = 0

        if 'submit_dateselect' in request.POST:
            logger.info('IN submit_dateselect')

            # rs_form
            rs_form = RegistSelectForm(request.POST, user=request.user)
            if rs_form.is_valid():
                regist_date = rs_form.cleaned_data['regist_date']
                sel_project = rs_form.cleaned_data['projectlist']
            else:
                logger.warn('RegistSelectForm.is_valid = False')

                rs_form = RegistSelectForm(user=request.user)
                regist_date = rs_form['regist_date'].value
                sel_project = (rs_form.fields['projectlist'].choices[0])[0]

            # re_form
            re_form = RegistForm(initial={'regist_date': regist_date,
                                          'project_id': sel_project})
        elif 'submit_regist' in request.POST:
            logger.info('IN submit_regist')

            re_form = RegistForm(request.POST)
            if re_form.is_valid():
                regist_date = re_form.cleaned_data['regist_date']
                sel_project = re_form.cleaned_data['project_id']

                # RegistSelect form
                rs_form = RegistSelectForm(user=request.user,
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

                with transaction.atomic():
                    for i in targetindexlist:
                        m = id_re.search(uttid[i])
                        pid, tid = m.group(1, 2)

                        uttinst = None
                        ud_ttime = datetime.time(
                            hour=int(tasktime_hour[i]),
                            minute=int(tasktime_min[i]))

                        # search exist data.
                        try:
                            uttinst = UsedTaskTime.objects.get(
                                user=request.user,
                                project=pid,
                                task=tid,
                                taskdate=regist_date)

                            uttinst.tasktime = ud_ttime

                            if (0 == ud_ttime.hour) and (0 == ud_ttime.minute):
                                uttinst.delete()
                            else:
                                uttinst.save()
                        except UsedTaskTime.DoesNotExist:
                            if (0 < ud_ttime.hour) or (0 < ud_ttime.minute):
                                uttinst = UsedTaskTime.objects.create(
                                    user=request.user,
                                    project=Project.objects.get(id=pid),
                                    task=Task.objects.get(id=tid),
                                    taskdate=regist_date,
                                    tasktime=ud_ttime)

                                uttinst.save()
                        except:
                            msg = "EXCEPT: fail save or delete. msg=%s,%s" % (
                                sys.exc_info()[1], sys.exc_info()[2])
                            logger.error(msg)
                            logger.error("do rollback")
                            # add notify message on template.
                            raise Exception(msg)
            else:
                logger.warn('RegistForm.is_valid = False')

                rs_form = RegistSelectForm(user=request.user)
                regist_date = datetime.date.today()
                sel_project = (rs_form.fields['projectlist'].choices[0])[0]

                re_form = RegistForm(initial={'regist_date': regist_date,
                                              'project_id': sel_project})
    else:
        logger.info('regist : method=GET')

        rs_form = RegistSelectForm(user=request.user)
        regist_date = datetime.date.today()
        sel_project = (rs_form.fields['projectlist'].choices[0])[0]

        re_form = RegistForm(initial={'regist_date': regist_date,
                                      'project_id': sel_project})

    # select project
    project = Project.objects.filter(id=sel_project)

    if project:
        cursor_pjw = ProjectWorker.objects.filter(user=request.user)
        cursor_pjw = cursor_pjw.filter(project=project)
        cursor_pjw = cursor_pjw.filter(project__start_dt__lte=regist_date)
        cursor_pjw = cursor_pjw.filter(project__end_dt__isnull=True)
        cursor_pjw = cursor_pjw.filter(invalid=False)
        cursor_pjw = cursor_pjw.order_by('project__sortkey', 'job__sortkey')
    else:
        cursor_pjw = []

    datalist = []
    existdatalist = []

    # select exist usedtasktime
    cursor_u = UsedTaskTime.objects.filter(user=request.user)
    cursor_u = cursor_u.filter(taskdate=regist_date)
    cursor_u = cursor_u.order_by('project__sortkey', 'task__sortkey')

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

    return my_render_to_response(request,
                                 'regist/regist.html',
                                 {'form': rs_form,
                                  'regist_form': re_form,
                                  'regist_date': regist_date,
                                  'projectid': sel_project,
                                  'existdatalist': existdatalist,
                                  'datalist': datalist,
                                  'hourlist': hourlist,
                                  'minutelist': minutelist,
                                  'oneday_total_hour': day_total_hour,
                                  'oneday_total_min': day_total_min})


@login_required
def summary_p(request):
    totallist = []
    monthlist = []
    datelist = []
    tasklist = []

    if request.method == 'POST':
        form = SummaryProjectForm(request.POST)
        if form.is_valid():
            project = form.cleaned_data['projectlist']
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            is_show_taskdetail = form.cleaned_data['is_show_taskdetail']

            logger.debug('IN summary_p : is_show_taskdetail(%s)' % (
                is_show_taskdetail))
            _starttime = datetime.datetime.now()
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

            # get month list
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

            monthlist = list(cursor)
            for r in monthlist:
                # year and month return double, so cast integer.
                r['year'] = int(r['year'])
                r['month'] = int(r['month'])
                # convert timedelta to HHH:MM
                r['month_tasktime'] = format_totaltime(r['month_tasktime'])

            _endtime = datetime.datetime.now()
            logger.debug('endtime: %s' % (_endtime))
            logger.debug('dur: %s' % (_endtime - _starttime))
        else:
            form = SummaryProjectForm()
    else:
        form = SummaryProjectForm()

    return my_render_to_response(request,
                                 'summary/project.html',
                                 {'form': form,
                                  'totallist': totallist,
                                  'monthlist': monthlist,
                                  'datelist': datelist,
                                  'tasklist': tasklist,
                                  'is_show_taskdetail': is_show_taskdetail})


@login_required
def summary_j(request):
    jobdatalist = []
    taskdatalist = []

    if request.method == 'POST':
        form = SummaryJobForm(request.POST)
        if form.is_valid():
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            joblist = form.cleaned_data['joblist']

            #calc job
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

            #calc task
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
        else:
            form = SummaryJobForm()
    else:
        form = SummaryJobForm()

    return my_render_to_response(request,
                                 'summary/job.html',
                                 {'form': form,
                                  'jobdata': jobdatalist,
                                  'taskdata': taskdatalist})


@login_required
def summary_u(request):
    userdatalist = []
    taskdatalist = []
    datedatalist = []
    datesummarylist = []

    if request.method == 'POST':
        form = SummaryUserForm(request.POST)
        if form.is_valid():
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            userlist = form.cleaned_data['userlist']

            #calc user
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

            #calc task
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
        else:
            form = SummaryUserForm()
    else:
        form = SummaryUserForm()

    return my_render_to_response(request,
                                 'summary/user.html',
                                 {'form': form,
                                  'userdata': userdatalist,
                                  'taskdata': taskdatalist,
                                  'datesummarydata': datesummarylist,
                                  'datedetaildata': datedatalist})


def summary_pd(request, project_id, from_date, to_date):
    return my_render_to_response(request,
                                 'summary/summary_pd.html', {})


def summary_pdu(request, project_id, from_date, to_date, user_id):
    return my_render_to_response(request,
                                 'summary/summary_pdu.html', {})


def summary_pdj(request, project_id, from_date, to_date, job_id):
    return my_render_to_response(request,
                                 'summary/summary_pdj.html', {})


def query(request):
    return my_render_to_response(request,
                                 'query/index.html', {})


def api(request):
    return my_render_to_response(request,
                                 'api.html', {})


def manage(request):
    return my_render_to_response(request,
                                 'manage/index.html', {})


def validate_password(password):
    if 6 <= len(password):
        return True
    else:
        return False


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

    return my_render_to_response(request,
                                 'manage/chpasswd.html',
                                 {'form': form,
                                  'message': message})


def manage_user_list(request):
    return my_render_to_response(request,
                                 'manage/user_list.html', {})


def manage_user_detail(request, user_id):
    return my_render_to_response(request,
                                 'manage/user_detail.html', {})


def manage_project_list(request):
    return my_render_to_response(request,
                                 'manage/project_list.html', {})


def manage_project_detail(request, project_id):
    return my_render_to_response(request,
                                 'manage/project_detail.html', {})


def manage_task_list(request):
    return my_render_to_response(request,
                                 'manage/task_list.html', {})


def manage_task_detail(request, task_id):
    return my_render_to_response(request,
                                 'manage/task_detail.html', {})


def manage_job_list(request):
    return my_render_to_response(request,
                                 'manage/job_list.html', {})


def manage_job_detail(request, job_id):
    return my_render_to_response(request,
                                 'manage/job_detail.html', {})


def my_render_to_response(request, template_file, paramdict):
    response = HttpResponse()
    #paramdict['sitecounter'] = do_counter(request, response)

    paramdict['url_prefix'] = get_url_prefix()
    paramdict['app_name'] = APP_NAME
    paramdict['app_longname'] = APP_LONGNAME
    paramdict['app_auther'] = APP_AUTHER
    paramdict['app_version'] = APP_VERSION
    paramdict['is_lastname_front'] = ats_settings.ATS_IS_LASTNAME_FRONT

    t = loader.get_template(template_file)
    c = RequestContext(request, paramdict)
    response.write(t.render(c))
    return response


class RegistSelectForm(forms.Form):
    regist_date = forms.DateField(label='regist_date', required=True,
                                  initial=lambda: datetime.datetime.now(),
                                  widget=forms.DateInput(attrs={"type":"date"}))
    projectlist = forms.ChoiceField(label='Project',
                                    choices=[('-1', '------')])

    def __init__(self, *args, **kwargs):
        _user = kwargs.pop('user')
        super(RegistSelectForm, self).__init__(*args, **kwargs)

        cursor = ProjectWorker.objects.filter(user=_user).order_by(
            'project__sortkey')

        cmp_dt = self.fields['regist_date'].initial()
        if args:
            cmp_dt = args[0]['regist_date']

        cursor = cursor.filter(Q(project__start_dt__isnull=True) | Q(project__start_dt__lte=cmp_dt))
        cursor = cursor.filter(Q(project__end_dt__isnull=True) | Q(project__end_dt__gte=cmp_dt))
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


class SummaryProjectForm(forms.Form):
    from_date = forms.DateField(label='from date', required=False,
                                initial=lambda: datetime.datetime.now().replace(day=1))
    to_date = forms.DateField(label='to date', required=False,
                              initial=lambda: datetime.datetime.now())
    projectlist = forms.ModelChoiceField(label='Project', queryset=Project.objects.all().order_by('sortkey'))
    is_show_taskdetail = forms.BooleanField(label="show Task Detail",
                                            required=False)


class SummaryJobForm(forms.Form):
    from_date = forms.DateField(label='from date', required=False,
                                initial=lambda: datetime.datetime.now().replace(day=1))
    to_date = forms.DateField(label='to date', required=False,
                              initial=lambda: datetime.datetime.now())
    joblist = forms.ModelMultipleChoiceField(label='job', required=True, queryset=Job.objects.all().order_by('sortkey'))


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
                                initial=lambda: datetime.datetime.now().replace(day=1))
    to_date = forms.DateField(label='to date', required=False,
                              initial=lambda: datetime.datetime.now())
    userlist = MyUserModelMultipleChoiceField(label='user', required=True, queryset=User.objects.filter(is_active=True).order_by('id'))


class LoginForm(forms.Form):
    username = forms.CharField(label='username',
                               max_length=256,
                               required=True)
    password = forms.CharField(label='password',
                               max_length=256,
                               widget=forms.PasswordInput(),
                               required=True)
