# coding: utf-8
from toolproj.settings_test import *

INSTALLED_APPS += (
    'django_jenkins',
)
JENKINS_TASKS = (
    'django_jenkins.tasks.django_tests',
)
PROJECT_APPS = (
    'ats',
)
