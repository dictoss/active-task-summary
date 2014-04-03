#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
from django.conf import settings

LOG_LEVEL = logging.DEBUG
LOG_PATH = '%s/ats.log' % os.environ.get('HOME')
