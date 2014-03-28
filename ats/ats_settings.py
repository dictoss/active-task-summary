#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from django.conf import settings

APP_NAME = 'ats'
APP_MOUNTDIR = '/'

try:
    from ats_settings_devel import *
except:
    pass
