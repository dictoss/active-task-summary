# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import logging
from django.conf import settings
from django.apps import AppConfig


class AtsConfig(AppConfig):
    name = 'ats'

    # app info
    APP_LONGNAME = 'Active Task Summary'
    APP_VERSION = '0.8.0'
    APP_AUTHER = 'dictoss'

    # valid range is between 1 and 24.
    ATS_REGIST_HOUR_MAX = 16

    # valid range is between 1 and 30.
    ATS_REGIST_MIN_SPAN = [0, 15, 30, 45]

    ATS_IS_LASTNAME_FRONT = False