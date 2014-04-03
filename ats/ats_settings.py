#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
from django.conf import settings

# valid range is between 1 and 24.
ATS_REGIST_HOUR_MAX = 16

# valid range is between 1 and 30.
ATS_REGIST_MIN_SPAN = 15

ATS_IS_LASTNAME_FRONT = False

LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s,%(levelname)-8s,%(message)s'
LOG_PATH = '%s/ats.log' % '/var/log/apache2'

try:
    from ats_settings_devel import *
except:
    pass
