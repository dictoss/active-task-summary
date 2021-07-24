"""
This file is nessasary if this application upgrade from 0.6.1 or lower.
"""
from django.db import models

class BigAutoField(models.BigAutoField):
    pass

