"""Misc utilities module."""

import logging
import functools
from django.db.models import Q


def createLogger(path: str) -> logging.Logger:
    # create logger
    LOGGER = logging.Logger("Logger", logging.DEBUG)
    # create log format
    log_fmt = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # create log file handler
    file_handler = logging.FileHandler(path, delay=False)
    file_handler.setFormatter(log_fmt)
    # create log file streamer
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(log_fmt)

    LOGGER.addHandler(file_handler)
    LOGGER.addHandler(stream_handler)
    return LOGGER


def filter_existing_queryset(model, model_key_list, key_name):
    """Filter existing entries from given values.

    Args:
        model(django.db.models.Model): The model to filter.
        model_key_list(list): List of model keys to filter on.
        key_name(str): Name of the attribute to filter each key by.
    Returns:
        Queryset of filtered db model entries.
    """
    query = Q(**{f"{key_name}__in": model_key_list})
    return model.objects.filter(query).distinct()


def check_unique_constraint(model):
    """Check unique constraint in model.

    Args:
        model(django.db.models.Model): The model to check uniquess for.
    Returns:
        bool.
    """
    try:
        model.validate_unique()
    except Exception:
        return False
    return True


def get_model_attr_value(m, attr):
    """Get objects' attributes value."""
    return functools.reduce(getattr, [m] + attr.split("__"))


def filter_non_duplicate_entry(models, *constant_attrs, non_dup):
    """Filter duplicate entries from given set as a generator."""
    for m in models:
        attr_vals = tuple(
            [get_model_attr_value(m, attr) for attr in constant_attrs]
        )
        if attr_vals not in non_dup:
            non_dup.add(attr_vals)
            yield m
