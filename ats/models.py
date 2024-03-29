# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=False)
    start_dt = models.DateField(null=False, blank=False)
    end_dt = models.DateField(null=True, blank=True)
    sortkey = models.IntegerField(null=False)
    external_project = models.ForeignKey('ExternalProject',
        on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        if self.end_dt:
            if self.end_dt < datetime.date.today():
                return '%d : %s [closed]' % (self.id, self.name)
            else:
                return '%d : %s [opened]' % (self.id, self.name)
        else:
            return '%d : %s [opened]' % (self.id, self.name)


class ExternalProject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=False)
    code = models.CharField(max_length=255, db_index=True,
        blank=True, null=True, default='',)

    def __str__(self):
        return '%d : %s' % (self.id, self.name)


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
    userdata1 = models.CharField(max_length=128, blank=True, null=True)
    userdata2 = models.CharField(max_length=128, blank=True, null=True)
    userdata3 = models.CharField(max_length=128, blank=True, null=True)
    userdata4 = models.CharField(max_length=128, blank=True, null=True)
    userdata5 = models.CharField(max_length=128, blank=True, null=True)

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

    class Meta:
        unique_together = [
            ['job', 'project','user']
        ]

    def __str__(self):
        if self.invalid:
            return '%d : %s (%s - %s) [invalid]' % (
                self.id, self.user.username, self.project.name, self.job.name)
        else:
            return '%d : %s (%s - %s)' % (
                self.id, self.user.username, self.project.name, self.job.name)


class UsedTaskTime(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    project = models.ForeignKey('Project', on_delete=models.PROTECT)
    task = models.ForeignKey('Task', on_delete=models.PROTECT)
    taskdate = models.DateField(null=False)
    tasktime = models.TimeField(null=False)
    comment = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return '%d : [%s - %s] %s - %s - %s' % (
            self.id, self.taskdate, self.tasktime,
            self.user.username, self.project.name, self.task.name)
