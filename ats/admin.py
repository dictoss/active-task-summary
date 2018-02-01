from django.contrib import admin

from .models import ProjectWorker


class ProjectWorkerAdmin(admin.ModelAdmin):
    list_filter = ['user', 'project', 'job']


admin.site.register(ProjectWorker, ProjectWorkerAdmin)
