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
         #
         #(r'^summary/$', 'summary'),
         (r'^summary/project/$', 'summary_p'),
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
         (r'^manage/chpasswd/$',
          'manage_chpasswd'),
         )

urlpatterns += staticfiles_urlpatterns()
