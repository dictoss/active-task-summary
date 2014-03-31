from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
import bigint_patch


class UserExtraAttr(models.Model):
    user = models.ForeignKey(User)
    expire_dt = models.DateField(auto_now=False,
                                 auto_now_add=False, null=False)
    accounttype = models.IntegerField()

admin.site.register(UserExtraAttr)


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=False)
    start_dt = models.DateField(auto_now=False, auto_now_add=False, null=False, blank=False)
    end_dt = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    sortkey = models.IntegerField(null=False)

    def __unicode__(self):
        return self.name

admin.site.register(Project)


class Job(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=False)
    sortkey = models.IntegerField(null=False)
    invalid = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

admin.site.register(Job)


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=False)
    job = models.ForeignKey('Job')
    sortkey = models.IntegerField(null=False)
    invalid = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s' % (self.name)

admin.site.register(Task)


class ProjectWorker(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    project = models.ForeignKey('Project')
    invalid = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s - %s' % (self.project.name, self.user.username)

admin.site.register(ProjectWorker)


class UsedTaskTime(models.Model):
    id = bigint_patch.BigAutoField(primary_key=True)
    user = models.ForeignKey(User)
    project = models.ForeignKey('Project')
    task = models.ForeignKey('Task')
    taskdate = models.DateField(auto_now=False, auto_now_add=False, null=False)
    tasktime = models.TimeField(auto_now=False, auto_now_add=False, null=False)

    def __unicode__(self):
        return '%s - %s -%s - %s' % (self.project.name, self.task.name, self.user.username, self.tasktime)

admin.site.register(UsedTaskTime)
