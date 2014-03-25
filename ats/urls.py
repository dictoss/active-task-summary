from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

handler500 = 'ats.views.error500'
handler404 = 'ats.views.error404'

urlpatterns = patterns('ats.views',
         (r'^$', 'index'),
         (r'^top/$', 'top'),
         (r'^login/$','login_view'),
         (r'^logout/$','logout_view'),
         (r'^regist/$', 'regist'),
         (r'^regist/(?P<date>\d+)/$', 'regist_d'),
         #
         #(r'^summary/$', 'summary'),
         (r'^summary/date/$', 'summary_d'),
         (r'^summary/job/$', 'summary_j'),
         (r'^summary/user/$', 'summary_u'),
         # 
         # direct link
         #(r'^summary/(?P<project_id>\d+)/$', 'summary_p'),
         #(r'^summary/(?P<project_id>\d+)/(?P<from_date>\d+)_(?P<to_date>\d+)/$', 'summary_pd'),
         #(r'^summary/(?P<project_id>\d+)/(?P<from_date>\d+)_(?P<to_date>\d+)/u(?P<user_id>\d+)/$', 'summary_pdu'),
         #(r'^summary/(?P<project_id>\d+)/(?P<from_date>\d+)_(?P<to_date>\d+)/j(?P<job_id>\d+)/$', 'summary_pdj'),
         #
         (r'^query/$', 'query'),
         #
         (r'^api/$', 'api'),
         #
         (r'^manage/$', 'manage'),
         #
         (r'^manage/user/$',
          'manage_user_list'),
         (r'^manage/user/(?P<user_id>\d+)/$',
          'manage_user_detail'),
         (r'^manage/user/(?P<user_id>\d+)/edit/$',
          'manage_user_edit'),
         #
         (r'^manage/project/$',
          'manage_project_list'),
         (r'^manage/project/(?P<project_id>\d+)/$',
          'manage_project_detail'),
         (r'^manage/project/(?P<project_id>\d+)/edit/$',
          'manage_project_edit'),
         #
         (r'^manage/task/$',
          'manage_task_list'),
         (r'^manage/task/(?P<task_id>\d+)/$',
          'manage_task_detail'),
         (r'^manage/task/(?P<task_id>\d+)/edit/$',
          'manage_task_edit'),
         #
         (r'^manage/job/$',
          'manage_job_list'),
         (r'^manage/job/(?P<job_id>\d+)/$',
          'manage_job_detail'),
         (r'^manage/job/(?P<job_id>\d+)/edit/$',
          'manage_job_edit'),
         #
         #(r'^manage/notify/$',
         # 'manage_notify_list'),
         #(r'^manage/notify/(?P<notify_id>\d+)/$',
         # 'manage_notify_detail'),
         #(r'^manage/notify/(?P<notify_id>\d+)/edit/$',
         # 'manage_notify_edit'),
         )
