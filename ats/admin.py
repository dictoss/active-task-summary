from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import admin

from .models import (
    Project,
    Job,
    Task,
    ProjectWorker,
    UsedTaskTime,
)

UserAdmin.list_display = (
    'username', 'email', 'first_name', 'last_name',
    'is_active', 'is_superuser', 'is_staff')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'start_dt', 'end_dt', 'sortkey')
    list_display_links = ('id', 'name')
    ordering = ['sortkey']


admin.site.register(Project, ProjectAdmin)


class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sortkey', 'is_vaild')
    list_display_links = ('id', 'name')
    ordering = ['sortkey']

    def is_vaild(self, obj):
        return not obj.invalid
    is_vaild.boolean = True


admin.site.register(Job, JobAdmin)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'job', 'sortkey', 'is_vaild')
    list_display_links = ('id', 'name')
    ordering = ['job', 'sortkey']

    def is_vaild(self, obj):
        return not obj.invalid
    is_vaild.boolean = True


admin.site.register(Task, TaskAdmin)


class ProjectWorkerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'job', 'is_vaild')
    list_filter = ['user', 'project', 'job']
    ordering = ['user', 'project', 'job']

    def is_vaild(self, obj):
        return not obj.invalid
    is_vaild.boolean = True


admin.site.register(ProjectWorker, ProjectWorkerAdmin)


class UsedTaskTimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'taskdate', 'tasktime', 'user', 'project', 'task')
    list_filter = ['user']
    ordering = ['-id']


admin.site.register(UsedTaskTime, UsedTaskTimeAdmin)
