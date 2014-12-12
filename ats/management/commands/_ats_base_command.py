#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import logging
from django.core.management.base import BaseCommand, AppCommand, CommandError


class AtsBaseCommand(BaseCommand):
    def handle(self, *args, **options):
        print("AtsBaseCommand.handler.")
        return True


class AtsAppCommand(AppCommand):
    def handle_app(self, app, **options):
        print("AtsAppCommand.handler.")
        return True
