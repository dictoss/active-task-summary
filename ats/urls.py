from django.urls import include, path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

from . import views

app_name = 'ats'

urlpatterns = [
    path('', views.index, name='index'),
    path('error_internal/', views.errorinternal, name='error_internal'),
    path('top/', views.top, name='top'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('regist/', views.regist, name='regist'),
    #
    # path('summary/', views.summary, name='summary'),
    path('summary/project/', views.summary_p, name='summary_p'),
    path('summary/job/', views.summary_j, name='summary_j'),
    path('summary/user/', views.summary_u, name='summary_u'),
    #
    # direct link
    #
    # path('summary/(?P<project_id>\d+)/', views.summary_p),
    # path('summary/(?P<project_id>\d+)/(?P<from_date>\d+)_(?P<to_date>\d+)/', vi ews.summary_pd),
    # path('summary/(?P<project_id>\d+)/(?P<from_date>\d+)_(?P<to_date>\d+)/u(?P<user_id>\d+)/', views.summary_pdu),
    # path('summary/(?P<project_id>\d+)/(?P<from_date>\d+)_(?P<to_date>\d+)/j(?P<job_id>\d+)/, views.summary_pdj),
    #
    path('query/', views.query, name='query'),
    #
    # path('api/', views.api),
    #
    path('manage/', views.manage, name='manage'),
    #
    path('manage/chpasswd/', views.manage_chpasswd, name='manage_chpasswd'),
    # path('manage/user/', views.manage_user_list, name='manage_user_list'),
    # path('manage/user/(?P<user_id>\d+)/', views.manage_user_detail, name='manage_user_detail'),
    # path('manage/project/', views.manage_project_list, name='manage_project_list'),
    # path('manage/project/(?P<project_id>\d+)/', views.manage_project_detail, name='manage_project_detail'),
    # path('manage/task/', views.manage_task_list, name='manage_task_list'),
    # path('manage/task/(?P<task_id>\d+)/', views.manage_task_detail, name='manage_task_detail'),
    # path('manage/job/', views.manage_job_list, name='manage_job_list'),
    # path('manage/job/(?P<job_id>\d+)/', views.manage_job_detail, name='manage_job_detail'),
]

urlpatterns += staticfiles_urlpatterns()
