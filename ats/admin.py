from django.contrib import admin

from .models import Project, Job, Task, ProjectWorker, UsedTaskTime


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'start_dt', 'end_dt', 'sortkey')
    ordering = ['sortkey']

admin.site.register(Project, ProjectAdmin)


class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sortkey', 'invalid')
    ordering = ['sortkey']

admin.site.register(Job, JobAdmin)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'job', 'sortkey', 'invalid')
    ordering = ['sortkey']

admin.site.register(Task, TaskAdmin)


class ProjectWorkerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'job', 'invalid')
    list_filter = ['user', 'project', 'job']
    ordering = ['user', 'project', 'job']


admin.site.register(ProjectWorker, ProjectWorkerAdmin)


class UsedTaskTimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'taskdate', 'tasktime', 'user', 'project', 'task')
    list_filter = ['user']
    ordering = ['-id']

admin.site.register(UsedTaskTime, UsedTaskTimeAdmin)
