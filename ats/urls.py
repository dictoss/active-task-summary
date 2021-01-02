from django.urls import include, path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

from . import views

handler500 = 'ats.views.error500'
handler404 = 'ats.views.error404'

urlpatterns = [
    path('', views.index),
    path('top/', views.top),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('regist/', views.regist),
    #
    # path('summary/', views.summary),
    path('summary/project/', views.summary_p),
    path('summary/job/', views.summary_j),
    path('summary/user/', views.summary_u),
    #
    # direct link
    #
    # path('summary/(?P<project_id>\d+)/', views.summary_p),
    # path('summary/(?P<project_id>\d+)/(?P<from_date>\d+)_(?P<to_date>\d+)/', vi ews.summary_pd),
    # path('summary/(?P<project_id>\d+)/(?P<from_date>\d+)_(?P<to_date>\d+)/u(?P<user_id>\d+)/', views.summary_pdu),
    # path('summary/(?P<project_id>\d+)/(?P<from_date>\d+)_(?P<to_date>\d+)/j(?P<job_id>\d+)/, views.summary_pdj),
    #
    path('query/', views.query),
    #
    # path('api/', views.api),
    #
    path('manage/', views.manage),
    #
    path('manage/chpasswd/', views.manage_chpasswd),
    # path('manage/user/', views.manage_user_list),
    # path('manage/user/(?P<user_id>\d+)/', views.manage_user_detail),
    # path('manage/project/', views.manage_project_list),
    # path('manage/project/(?P<project_id>\d+)/', views.manage_project_detail),
    # path('manage/task/', views.manage_task_list),
    # path('manage/task/(?P<task_id>\d+)/', views.manage_task_detail),
    # path('manage/job/', views.manage_job_list),
    # path('manage/job/(?P<job_id>\d+)/', views.manage_job_detail),
]

urlpatterns += staticfiles_urlpatterns()
