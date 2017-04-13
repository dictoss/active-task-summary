# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from . import bigint_patch


class UserExtraAttr(models.Model):
    user = models.ForeignKey(User)
    expire_dt = models.DateField(null=False)
    accounttype = models.IntegerField()

admin.site.register(UserExtraAttr)


@python_2_unicode_compatible
class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=False)
    start_dt = models.DateField(null=False, blank=False)
    end_dt = models.DateField(null=True, blank=True)
    sortkey = models.IntegerField(null=False)

    def __str__(self):
        if self.end_dt:
            if self.end_dt < datetime.date.today():
                return '%d : %s [closed]' % (self.id, self.name)
            else:
                return '%d : %s [opened]' % (self.id, self.name)
        else:
            return '%d : %s [opened]' % (self.id, self.name)

admin.site.register(Project)


@python_2_unicode_compatible
class Job(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=False)
    sortkey = models.IntegerField(null=False)
    invalid = models.BooleanField(default=False)

    def __str__(self):
        if self.invalid:
            return '%d : %s [invalid]' % (self.id, self.name)
        else:
            return '%d : %s' % (self.id, self.name)

admin.site.register(Job)


@python_2_unicode_compatible
class Task(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=False)
    job = models.ForeignKey('Job')
    sortkey = models.IntegerField(null=False)
    invalid = models.BooleanField(default=False)

    def __str__(self):
        if self.invalid:
            return '%d : %s (%s) [invalid]' % (
                self.id, self.name, self.job.name)
        else:
            return '%d : %s (%s)' % (
                self.id, self.name, self.job.name)

admin.site.register(Task)


@python_2_unicode_compatible
class ProjectWorker(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    project = models.ForeignKey('Project')
    job = models.ForeignKey('Job')
    invalid = models.BooleanField(default=False)

    def __str__(self):
        if self.invalid:
            return '%d : %s (%s - %s) [invalid]' % (
                self.id, self.user.username, self.project.name, self.job.name)
        else:
            return '%d : %s (%s - %s)' % (
                self.id, self.user.username, self.project.name, self.job.name)

admin.site.register(ProjectWorker)


@python_2_unicode_compatible
class UsedTaskTime(models.Model):
    id = bigint_patch.BigAutoField(primary_key=True)
    user = models.ForeignKey(User)
    project = models.ForeignKey('Project')
    task = models.ForeignKey('Task')
    taskdate = models.DateField(null=False)
    tasktime = models.TimeField(null=False)

    def __str__(self):
        return '%d : [%s - %s] %s - %s - %s' % (
            self.id, self.taskdate, self.tasktime,
            self.user.username, self.project.name, self.task.name)

admin.site.register(UsedTaskTime)
