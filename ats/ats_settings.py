#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from django.conf import settings

APP_NAME = 'ats'
APP_LONGNAME = 'Active Task Summary'
APP_VERSION = '0.1.0'
APP_AUTHER = 'dictoss'

# valid range is between 1 and 30.
ATS_REGIST_MIN_SPAN = 15

ATS_IS_LASTNAME_FRONT = False

try:
    from ats_settings_devel import *
except:
    pass
