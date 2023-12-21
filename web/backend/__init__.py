"""Imported celery app when Django starts so shared_task use this app."""
from backend.celery import app as celery_app
from django.conf import settings
import redis


if not settings.TEST:
    redis_instance = redis.StrictRedis(
        host=settings.REDIS_HOST)

    # Flush before start. No need in demo.
    redis_instance.flushdb()

__all__ = ['celery_app']
