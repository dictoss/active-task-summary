#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import logging
from django.db.models.loading import get_model
from _ats_base_command import AtsBaseCommand, AtsAppCommand
from ats.models import *


class Command(AtsAppCommand):
    help = "export command"
    args = "[appname ...]"

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle_app(self, app, **options):
        print("AtsExportCommand.handler.")
