from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

from . import views

handler500 = 'ats.views.error500'
handler404 = 'ats.views.error404'

urlpatterns = [
    url(r'^$', views.index),
    url(r'^top/$', views.top),
    url(r'^login/$', views.login_view),
    url(r'^logout/$', views.logout_view),
    url(r'^regist/$', views.regist),
    #
    #url(r'^summary/$', views.summary),
    url(r'^summary/project/$', views.summary_p),
    url(r'^summary/job/$', views.summary_j),
    url(r'^summary/user/$', views.summary_u),
    #
    # direct link
    #url(r'^summary/(?P<project_id>\d+)/$', views.summary_p),
    #url(r'^summary/(?P<project_id>\d+)/(?P<from_date>\d+)_(?P<to_date>\d+)/$', views.summary_pd),
    #url(r'^summary/(?P<project_id>\d+)/(?P<from_date>\d+)_(?P<to_date>\d+)/u(?P<user_id>\d+)/$', views.summary_pdu),
    #url(r'^summary/(?P<project_id>\d+)/(?P<from_date>\d+)_(?P<to_date>\d+)/j(?P<job_id>\d+)/$', views.summary_pdj),
    #
    url(r'^query/$', views.query),
    #
    #url(r'^api/$', views.api),
    #
    url(r'^manage/$', views.manage),
    #
    url(r'^manage/chpasswd/$', views.manage_chpasswd),
]

urlpatterns += staticfiles_urlpatterns()
