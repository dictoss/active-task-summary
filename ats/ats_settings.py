#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

APP_NAME = 'ats'
REGIST_SELECT_SPAN_DAYS = 7

try:
    from ats_settings_devel import *
    print "settings is devel."
except:
    print "settings is production."
