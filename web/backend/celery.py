"""Celery configuration module."""

import os
from celery import Celery
from django.conf import settings

app = Celery(os.getenv("PROJECT_NAME"))

app.config_from_object(
    'django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
