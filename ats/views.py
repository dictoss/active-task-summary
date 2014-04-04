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
from django.db.models import Sum
from django.db import transaction
from ats.models import *
from ats import ats_settings

APP_NAME = 'ats'
APP_LONGNAME = 'Active Task Summary'
APP_VERSION = '0.1.0'
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
@transaction.commit_manually
def regist(request):
    if request.method == 'POST':
        regist_count = 0

        rs_form = RegistSelectForm(request.POST, user=request.user)
        if rs_form.is_valid():
            regist_date = rs_form.cleaned_data['regist_date']
            sel_project = rs_form.cleaned_data['projectlist']
        else:
            rs_form = RegistSelectForm(user=request.user)
            regist_date = rs_form['regist_date'].value
            sel_project = rs_form.fields['projectlist'].choices[0]

        # todo:
        # receive form data from django form.
        if 'submit_dateselect' in request.POST:
            re_form = RegistForm()
        else:
            re_form = RegistForm(request.POST)
            if re_form.is_valid():
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

                # insert or update usedtasktime
                id_re = re.compile(r'p([0-9]{1,})_t([0-9]{1,})')
                for i in targetindexlist:
                    m = id_re.search(uttid[i])
                    pid, tid = m.group(1, 2)

                    uttinst = None
                    ud_ttime = datetime.time(hour=int(tasktime_hour[i]),
                                             minute=int(tasktime_min[i]))
                    try:
                        uttinst = UsedTaskTime.objects.get(
                            user=request.user,
                            project=pid,
                            task=tid,
                            taskdate=regist_date)

                        uttinst.tasktime = ud_ttime
                    except UsedTaskTime.DoesNotExist:
                        uttinst = UsedTaskTime(
                            id=None,
                            user=request.user,
                            project=Project.objects.get(id=pid),
                            task=Task.objects.get(id=tid),
                            taskdate=regist_date,
                            tasktime=ud_ttime)
                    except:
                        pass

                    try:
                        if uttinst:
                            uttinst.save()
                            regist_count = regist_count + 1
                        else:
                            pass
                    except:
                        pass

                if 0 < len(targetindexlist):
                    if regist_count == len(targetindexlist):
                        transaction.commit()
                    else:
                        transaction.rollback()
                else:
                    # no check.
                    pass
            else:
                re_form = RegistForm()
    else:
        re_form = RegistForm()

        rs_form = RegistSelectForm(user=request.user)
        regist_date = rs_form['regist_date'].value
        sel_project = rs_form.fields['projectlist'].choices[0]

    # select project
    project = Project.objects.filter(id=sel_project[0])

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

    for u in cursor_u:
        uttobj = {'projectname': u.project.name,
                  'jobname': u.task.job.name,
                  'taskname': u.task.name,
                  'tasktime_hour': u.tasktime.hour,
                  'tasktime_min': u.tasktime.minute}

        existdatalist.append(uttobj)

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
    for i in range((60 / ats_settings.ATS_REGIST_MIN_SPAN)):
        minutelist.append(i * (ats_settings.ATS_REGIST_MIN_SPAN))

    transaction.commit()

    return my_render_to_response(request,
                                 'regist/regist.html',
                                 {'form': rs_form,
                                  'regist_form': re_form,
                                  'regist_date': regist_date,
                                  'existdatalist': existdatalist,
                                  'datalist': datalist,
                                  'hourlist': hourlist,
                                  'minutelist': minutelist})


@login_required
def summary_d(request):
    datalist = []
    totallist = []

    if request.method == 'POST':
        form = SummaryDateForm(request.POST)
        if form.is_valid():
            project = form.cleaned_data['projectlist']
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']

            # date
            cursor = UsedTaskTime.objects.filter(project=project)
            if from_date:
                cursor = cursor.filter(taskdate__gte=from_date)

            if to_date:
                cursor = cursor.filter(taskdate__lte=to_date)

            cursor = cursor.order_by('taskdate')

            datalist = list(cursor)

            # sum total
            td = datetime.timedelta()
            for r in datalist:
                td = td + datetime.timedelta(
                    hours=r.tasktime.hour, minutes=r.tasktime.minute)

            totaltime = format_totaltime(td)

            totallist = [{'project_id': project.id,
                          'project__name': project.name,
                          'total_tasktime': totaltime}]
        else:
            form = SummaryDateForm()
    else:
        form = SummaryDateForm()

    return my_render_to_response(request,
                                 'summary/date.html',
                                 {'form': form,
                                  'totallist': totallist,
                                  'datalist': datalist})


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
                                  'taskdata': taskdatalist})


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


def manage_user_edit(request, user_id):
    return my_render_to_response(request,
                                 'manage/user_edit.html', {})


def manage_project_list(request):
    return my_render_to_response(request,
                                 'manage/project_list.html', {})


def manage_project_detail(request, project_id):
    return my_render_to_response(request,
                                 'manage/project_detail.html', {})


def manage_project_edit(request, project_id):
    return my_render_to_response(request,
                                 'manage/project_edit.html', {})


def manage_task_list(request):
    return my_render_to_response(request,
                                 'manage/task_list.html', {})


def manage_task_detail(request, task_id):
    return my_render_to_response(request,
                                 'manage/task_detail.html', {})


def manage_task_edit(request, task_id):
    return my_render_to_response(request,
                                 'manage/task_edit.html', {})


def manage_job_list(request):
    return my_render_to_response(request,
                                 'manage/jpb_list.html', {})


def manage_job_detail(request, job_id):
    return my_render_to_response(request,
                                 'manage/job_detail.html', {})


def manage_job_edit(request, user_id):
    return my_render_to_response(request,
                                 'manage/job_edit.html', {})


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
                                  initial=datetime.datetime.now())
    projectlist = forms.ChoiceField(label='Project',
                                    choices=[('-1', '------')])

    def __init__(self, *args, **kwargs):
        _user = kwargs.pop('user')
        super(RegistSelectForm, self).__init__(*args, **kwargs)

        cursor = ProjectWorker.objects.filter(user=_user).order_by(
            'project').values('project__id', 'project__name').distinct()

        pjlist = []
        for r in cursor:
            t = (r['project__id'], r['project__name'])
            pjlist.append(t)

        if 0 < len(pjlist):
            self.fields['projectlist'].choices = pjlist


class RegistForm(forms.Form):
    registcheck = forms.BooleanField(required=False)


class SummaryDateForm(forms.Form):
    from_date = forms.DateField(label='from date', required=False,
                                initial=datetime.datetime.now().replace(day=1))
    to_date = forms.DateField(label='to date', required=False,
                              initial=datetime.datetime.now())
    projectlist = forms.ModelChoiceField(label='Project', queryset=Project.objects.all())


class SummaryJobForm(forms.Form):
    from_date = forms.DateField(label='from date', required=False,
                                initial=datetime.datetime.now().replace(day=1))
    to_date = forms.DateField(label='to date', required=False,
                              initial=datetime.datetime.now())
    joblist = forms.ModelMultipleChoiceField(label='job', required=True, queryset=Job.objects.all())


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
                                initial=datetime.datetime.now().replace(day=1))
    to_date = forms.DateField(label='to date', required=False,
                              initial=datetime.datetime.now())
    userlist = MyUserModelMultipleChoiceField(label='user', required=True, queryset=User.objects.all())


class LoginForm(forms.Form):
    username = forms.CharField(label='username',
                               max_length=256,
                               required=True)
    password = forms.CharField(label='password',
                               max_length=256,
                               widget=forms.PasswordInput(),
                               required=True)
