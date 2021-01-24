from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

from . import views

app_name = 'ats'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^top/$', views.top, name='top'),
    url(r'^login/$', views.login_view, name='login_view'),
    url(r'^logout/$', views.logout_view, name='logout_view'),
    url(r'^regist/$', views.regist, name='regist'),
    #
    #url(r'^summary/$', views.summary, name='summary'),
    url(r'^summary/project/$', views.summary_p, name='summary_p'),
    url(r'^summary/job/$', views.summary_j, name='summary_j'),
    url(r'^summary/user/$', views.summary_u, name='summary_u'),
    #
    # direct link
    #url(r'^summary/(?P<project_id>\d+)/$', views.summary_p),
    #url(r'^summary/(?P<project_id>\d+)/(?P<from_date>\d+)_(?P<to_date>\d+)/$', views.summary_pd),
    #url(r'^summary/(?P<project_id>\d+)/(?P<from_date>\d+)_(?P<to_date>\d+)/u(?P<user_id>\d+)/$', views.summary_pdu),
    #url(r'^summary/(?P<project_id>\d+)/(?P<from_date>\d+)_(?P<to_date>\d+)/j(?P<job_id>\d+)/$', views.summary_pdj),
    #
    url(r'^query/$', views.query, name='query'),
    #
    #url(r'^api/$', views.api),
    #
    url(r'^manage/$', views.manage, name='manage'),
    #
    url(r'^manage/chpasswd/$', views.manage_chpasswd, name='manage_chpasswd'),
    #url(r'^manage/user/$', views.manage_user_list, name='manage_user_list'),
    #url(r'^manage/user/(?P<user_id>\d+)/$', views.manage_user_detail, name='manage_user_detail'),
    #url(r'^manage/project/$', views.manage_project_list, name='manage_project_list'),
    #url(r'^manage/project/(?P<project_id>\d+)/$', views.manage_project_detail, name='manage_project_detail'),
    #url(r'^manage/task/$', views.manage_task_list, name='manage_task_list'),
    #url(r'^manage/task/(?P<task_id>\d+)/$', views.manage_task_detail, name='manage_task_detail'),
    #url(r'^manage/job/$', views.manage_job_list, name='manage_job_list'),
    #url(r'^manage/job/(?P<job_id>\d+)/$', views.manage_job_detail, name='manage_job_detail'),
]

urlpatterns += staticfiles_urlpatterns()
