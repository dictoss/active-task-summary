# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from . import bigint_patch


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


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=False)
    job = models.ForeignKey('Job', on_delete=models.PROTECT)
    sortkey = models.IntegerField(null=False)
    invalid = models.BooleanField(default=False)

    def __str__(self):
        if self.invalid:
            return '%d : %s (%s) [invalid]' % (
                self.id, self.name, self.job.name)
        else:
            return '%d : %s (%s)' % (
                self.id, self.name, self.job.name)


class ProjectWorker(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    project = models.ForeignKey('Project', on_delete=models.PROTECT)
    job = models.ForeignKey('Job', on_delete=models.PROTECT)
    invalid = models.BooleanField(default=False)

    def __str__(self):
        if self.invalid:
            return '%d : %s (%s - %s) [invalid]' % (
                self.id, self.user.username, self.project.name, self.job.name)
        else:
            return '%d : %s (%s - %s)' % (
                self.id, self.user.username, self.project.name, self.job.name)


class UsedTaskTime(models.Model):
    id = bigint_patch.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    project = models.ForeignKey('Project', on_delete=models.PROTECT)
    task = models.ForeignKey('Task', on_delete=models.PROTECT)
    taskdate = models.DateField(null=False)
    tasktime = models.TimeField(null=False)

    def __str__(self):
        return '%d : [%s - %s] %s - %s - %s' % (
            self.id, self.taskdate, self.tasktime,
            self.user.username, self.project.name, self.task.name)
