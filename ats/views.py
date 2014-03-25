#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import codecs
import json
import time
import datetime
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

from ats.models import *
from ats import ats_settings


def error500(request):
    return render_to_response('500.html', {})


def error404(request):
    return render_to_response('404.html', {})


def get_appname():
    if settings.DEBUG:
        return ats_settings.APP_NAME
    else:
        return ""


def index(request):
    """
    if request.:
        return HttpResponseRedirect('/top/')
    else:
        return HttpResponseRedirect('/login/')
    """
    return HttpResponseRedirect('/%s/top' % get_appname())


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
                        nextpage = '/%s/top' % get_appname()

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
            return HttpResponseRedirect('/%s/top' % get_appname())
        else:
            form = LoginForm()

    return my_render_to_response(request,
                                 'login/login.html',
                                 {'form': form,
                                  'error_reason': error_reason})


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/%s/login/' % get_appname())


@login_required
def regist(request):
    if request.method == 'POST':
        form = RegistForm(request.POST)
        if form.is_valid():
            regist_date = form.cleaned_data['regist_date']
        else:
            form = RegistForm()
    else:
        form = RegistForm()
        regist_date = form['regist_date'].value

    #画面にはその日の登録済みデータが表示される

    #select project
    cursor1 = ProjectWorker.objects.select_related("project_name").filter(user=request.user)
    cursor1 = cursor1.filter(project__end_dt__isnull=True)
    cursor1 = cursor1.order_by("project")

    maxtasks = 5

    datalist = []
    for p in cursor1:

        cursor = UsedTaskTime.objects.select_related("project__name").filter(user=request.user)
        cursor = cursor.filter(taskdate=regist_date)
        cursor = cursor.filter(project=p)
        cursor = cursor.order_by("task__sortkey")

        #paramete
        # 常に表示する行数を固定にする。
        # データがないプロジェクトについては空データとして表示する
        cnt = 0

        projtasklist = []
        for r in cursor:
            data = r
            print(r)
            projtasklist.append(data)
            cnt = cnt + 1

        for i in range(maxtasks - cnt):
            data = {}
            projtasklist.append(data)
            cnt = cnt + 1

        print cnt

        d = {'projectname': p.project.name, 'task': projtasklist }
        datalist.append(d)

    return my_render_to_response(request,
                                 'regist/regist.html',
                                 {'form': form,
                                  'regist_date' : regist_date,
                                  'datalist': datalist})


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

            totaltime = '%d:%02d' % (td.days * 24 + td.seconds / 3600,
                                     td.seconds % 60)

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
                r['total_tasktime'] = r['total_tasktime'] / 1000

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
                r['total_tasktime'] = r['total_tasktime'] / 1000
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
                r['total_tasktime'] = r['total_tasktime'] / 1000

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
                r['total_tasktime'] = r['total_tasktime'] / 1000
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

    t = loader.get_template(template_file)
    c = RequestContext(request, paramdict)
    response.write(t.render(c))
    return response


class RegistForm(forms.Form):
    regist_date = forms.DateField(label='regist_date', required=True,
                                  initial=datetime.datetime.now())


class SummaryDateForm(forms.Form):
    projectlist = forms.ModelChoiceField(label='Project', queryset=Project.objects.all())
    from_date = forms.DateField(label='from date', required=False)
    to_date = forms.DateField(label='to date', required=False)


class SummaryJobForm(forms.Form):
    projectlist = forms.ModelChoiceField(label='Project', queryset=Project.objects.all())
    from_date = forms.DateField(label='from date', required=False)
    to_date = forms.DateField(label='to date', required=False)
    joblist = forms.ModelMultipleChoiceField(label='job', required=True, queryset=Job.objects.all())


class SummaryUserForm(forms.Form):
    projectlist = forms.ModelChoiceField(label='Project', queryset=Project.objects.all())
    from_date = forms.DateField(label='from date', required=False)
    to_date = forms.DateField(label='to date', required=False)
    userlist = forms.ModelMultipleChoiceField(label='user', required=True, queryset=User.objects.all())


class LoginForm(forms.Form):
    username = forms.CharField(label='username',
                               max_length=256,
                               required=True)
    password = forms.CharField(label='password',
                               max_length=256,
                               widget=forms.PasswordInput(),
                               required=True)
