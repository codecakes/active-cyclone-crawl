"""Celery tasks for cyclone scraper."""

import json

import backend
from apps.cyclones import models
from apps.cyclones.scraper import scraper
from backend.celery import app
from django.conf import settings


@app.task(bind=True)
def cyclone_scheduler(task_self: app.task):
    """Schedules cyclone scraper defined in cron settings."""
    fetch_sig_cb = fetch_result_cb.signature()
    scraper.scrape_page(lambda result: fetch_sig_cb.delay(result))


@app.task
def fetch_result_cb(scraped_data: dict):
    """Schedules task that enqeueus  scrapped results.

    Args:
        scraped_data(dict): Scrapped cyclone data.
    Returns:
        Scrapped cyclone dictionary.
    """
    return scraped_data


@app.task
def cycle_stale_results():
    """Save in storage layer and delete stale data."""
    data = []
    pipe = backend.redis_instance.pipeline(transaction=True)
    # Store to db and delete from redis.
    # There can be only so many cyclones at one given point!
    for key in backend.redis_instance.scan_iter("celery-task-meta*"):
        data += [json.loads(backend.redis_instance.get(key))]
        pipe.delete(key)
    pipe.execute()
    if data:
        save_db_task.signature().delay(json.dumps(data))


@app.task
def save_db_task(serialized_data: str):
    """Task call to batch save cyclone data.

    Args:
        serialized_data(str): Serialized string of list of cyclone data.
    """
    models.save_db(json.loads(serialized_data))
    settings.LOGGER.info("Cyclone data stored")
