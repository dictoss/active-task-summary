#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import codecs
import json
import time
import datetime
import re
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
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


def error500(request):
    return render_to_response('500.html', {})


def error404(request):
    return render_to_response('404.html', {})


def get_url_prefix():
    return '%s/%s' % (ats_settings.APP_MOUNTDIR, ats_settings.APP_NAME)


def format_totaltime_delta(td):
    return '%d:%02d' % (td.days * 24 + td.seconds / 3600,
                        td.seconds % 60)


def format_totaltime_int(f):
    '''
    paramter type is float.(return group by)

    format:
      12500 = 12000 + 500
            = 12 hour + 30 min
    '''
    hour = int(f / 1000)

    # convert from decimal to sexagesimal
    minute = int((int(f) - (hour * 1000)) * 0.06)

    return '%d:%02d' % (hour, minute)


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

        ds_form = DateSelectForm(request.POST)
        if ds_form.is_valid():
            regist_date = ds_form.cleaned_data['regist_date']
        else:
            ds_form = DateSelectForm()

        # todo:
        # receive form data from django form.
        if 'submit_dateselect' in request.POST:
            print("push dateselect")
            re_form = RegistForm()
        else:
            print("push regist")
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
                id_re = re.compile(r'p([0-9]{1,})_t([0-9]){1,}')
                for i in targetindexlist:
                    m = id_re.search(uttid[i])
                    pid, tid = m.group(1, 2)

                    uttinst = None
                    ud_ttime = datetime.time(hour=int(tasktime_hour[i]),
                                             minute=int(tasktime_min[i]))
                    try:
                        uttinst = UsedTaskTime.objects.get(
                            taskdate=regist_date,
                            project=pid,
                            task=tid)
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

                    print(uttinst)
                    try:
                        if uttinst:
                            uttinst.save()
                            regist_count = regist_count + 1
                        else:
                            print("not save")
                    except:
                        pass

                if 0 < len(targetindexlist):
                    if regist_count == len(targetindexlist):
                        transaction.commit()
                        print("commit")
                    else:
                        transaction.rollback()
                        print("rollback")
                else:
                    # no check.
                    pass
            else:
                re_form = RegistForm()
    else:
        ds_form = DateSelectForm()
        re_form = RegistForm()

        regist_date = ds_form['regist_date'].value

    #select project
    cursor_p = ProjectWorker.objects.select_related(
        'project_name').filter(user=request.user)
    cursor_p = cursor_p.filter(project__end_dt__isnull=True)
    cursor_p = cursor_p.filter(invalid=False)
    cursor_p = cursor_p.order_by('project__sortkey')

    datalist = []
    for p in cursor_p:
        # todo:
        # select assign job only
        cursor_j = Job.objects.filter(invalid=False).order_by('sortkey')

        usedtasktimelist = []
        for j in cursor_j:
            # task
            cursor_t = Task.objects.filter(job=j)
            cursor_t = cursor_t.filter(invalid=False)
            cursor_t = cursor_t.order_by('sortkey')
            # usedtasktime
            cursor_u = UsedTaskTime.objects.filter(user=request.user)
            cursor_u = cursor_u.filter(project=p)
            cursor_u = cursor_u.filter(taskdate=regist_date)
            cursor_u = cursor_u.order_by('task__sortkey')
            #print(cursor_u)

            for t in cursor_t:
                utt = {'job_id': t.job.id,
                       'job_name': t.job.name,
                       'task_id': t.id,
                       'task_name': t.name,
                       'tasktime_hour': 0,
                       'tasktime_min': 0}

                for u in cursor_u:
                    if t.id == u.task_id:
                        utt['tasktime_hour'] = u.tasktime.hour
                        utt['tasktime_min'] = u.tasktime.minute
                        break

                usedtasktimelist.append(utt)

        d = {'project_id': p.project.id,
             'project_name': p.project.name,
             'usedtasktimelist': usedtasktimelist}
        datalist.append(d)

    # enable select hour and minute.
    hourlist = []
    for i in range(24):
        hourlist.append(i)

    minutelist = []
    for i in range((60 / ats_settings.ATS_REGIST_MIN_SPAN)):
        minutelist.append(i * (ats_settings.ATS_REGIST_MIN_SPAN))

    transaction.commit()

    return my_render_to_response(request,
                                 'regist/regist.html',
                                 {'form': ds_form,
                                  'regist_form': re_form,
                                  'regist_date': regist_date,
                                  'datalist': datalist,
                                  'hourlist': hourlist,
                                  'minutelist': minutelist})


@login_required
def regist_d(request, date):
    return my_render_to_response(request,
                                 'regist/regist_d.html', {})


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

            datalist = list(cursor)

            # sum total
            td = datetime.timedelta()
            for r in datalist:
                td = td + datetime.timedelta(
                    hours=r.tasktime.hour, minutes=r.tasktime.minute)

            totaltime = format_totaltime_delta(td)

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
            project = form.cleaned_data['projectlist']
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            joblist = form.cleaned_data['joblist']

            #calc job
            cursor = UsedTaskTime.objects.filter(
                project=project).order_by(
                'taskdate', 'task__job', 'task__sortkey')
            cursor = cursor.filter(task__job__in=joblist)

            if from_date:
                cursor = cursor.filter(taskdate__gte=from_date)

            if to_date:
                cursor = cursor.filter(taskdate__lte=to_date)

            cursor = cursor.values('project_id',
                                   'project__name',
                                   'task__job__id',
                                   'task__job__name').annotate(
                total_tasktime=Sum('tasktime'))

            jobdatalist = list(cursor)

            # convert hour
            for r in jobdatalist:
                r['total_tasktime'] = format_totaltime_int(r['total_tasktime'])

            #calc task
            cursor = UsedTaskTime.objects.filter(
                project=project).order_by(
                'taskdate', 'task__job', 'task__sortkey')
            cursor = cursor.filter(task__job__in=joblist)

            if from_date:
                cursor = cursor.filter(taskdate__gte=from_date)

            if to_date:
                cursor = cursor.filter(taskdate__lte=to_date)

            cursor = cursor.values('project_id',
                                   'project__name',
                                   #'task__job__id',
                                   'task__job__name',
                                   'task_id',
                                   'task__name').annotate(
                total_tasktime=Sum('tasktime'))

            taskdatalist = list(cursor)

            # convert hour
            for r in taskdatalist:
                r['total_tasktime'] = format_totaltime_int(r['total_tasktime'])
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
            project = form.cleaned_data['projectlist']
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            userlist = form.cleaned_data['userlist']

            #calc user
            cursor = UsedTaskTime.objects.filter(
                project=project).order_by(
                'taskdate', 'task__job', 'task__sortkey')
            cursor = cursor.filter(user__in=userlist)

            if from_date:
                cursor = cursor.filter(taskdate__gte=from_date)

            if to_date:
                cursor = cursor.filter(taskdate__lte=to_date)

            cursor = cursor.values('project_id',
                                   'project__name',
                                   #'task__job__id',
                                   'task__job__name',
                                   #'user__id',
                                   'user__last_name',
                                   'user__first_name').annotate(
                total_tasktime=Sum('tasktime'))

            userdatalist = list(cursor)

            # convert hour
            for r in userdatalist:
                r['total_tasktime'] = format_totaltime_int(r['total_tasktime'])

            #calc task
            cursor = UsedTaskTime.objects.filter(
                project=project).order_by(
                'taskdate', 'task__job', 'task__sortkey')
            cursor = cursor.filter(user__in=userlist)

            if from_date:
                cursor = cursor.filter(taskdate__gte=from_date)

            if to_date:
                cursor = cursor.filter(taskdate__lte=to_date)

            cursor = cursor.values('project_id',
                                   'project__name',
                                   #'task__job__id',
                                   'task__job__name',
                                   'task_id',
                                   'task__name',
                                   #'user__id',
                                   'user__last_name',
                                   'user__first_name').annotate(
                total_tasktime=Sum('tasktime'))

            taskdatalist = list(cursor)

            # convert hour
            for r in taskdatalist:
                r['total_tasktime'] = format_totaltime_int(r['total_tasktime'])
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
    paramdict['app_longname'] = ats_settings.APP_LONGNAME
    paramdict['app_auther'] = ats_settings.APP_AUTHER
    paramdict['app_version'] = ats_settings.APP_VERSION
    paramdict['is_lastname_front'] = ats_settings.ATS_IS_LASTNAME_FRONT

    t = loader.get_template(template_file)
    c = RequestContext(request, paramdict)
    response.write(t.render(c))
    return response


class DateSelectForm(forms.Form):
    regist_date = forms.DateField(label='regist_date', required=True,
                                  initial=datetime.datetime.now())


class RegistForm(forms.Form):
    registcheck = forms.BooleanField(required=False)


class SummaryDateForm(forms.Form):
    projectlist = forms.ModelChoiceField(label='Project', queryset=Project.objects.all())
    from_date = forms.DateField(label='from date', required=False,
                                initial=datetime.datetime.now().replace(day=1))
    to_date = forms.DateField(label='to date', required=False,
                              initial=datetime.datetime.now())


class SummaryJobForm(forms.Form):
    projectlist = forms.ModelChoiceField(label='Project', queryset=Project.objects.all())
    from_date = forms.DateField(label='from date', required=False,
                                initial=datetime.datetime.now().replace(day=1))
    to_date = forms.DateField(label='to date', required=False,
                              initial=datetime.datetime.now())
    joblist = forms.ModelMultipleChoiceField(label='job', required=True, queryset=Job.objects.all())


class SummaryUserForm(forms.Form):
    projectlist = forms.ModelChoiceField(label='Project', queryset=Project.objects.all())
    from_date = forms.DateField(label='from date', required=False,
                                initial=datetime.datetime.now().replace(day=1))
    to_date = forms.DateField(label='to date', required=False,
                              initial=datetime.datetime.now())
    userlist = forms.ModelMultipleChoiceField(label='user', required=True, queryset=User.objects.all())


class LoginForm(forms.Form):
    username = forms.CharField(label='username',
                               max_length=256,
                               required=True)
    password = forms.CharField(label='password',
                               max_length=256,
                               widget=forms.PasswordInput(),
                               required=True)
