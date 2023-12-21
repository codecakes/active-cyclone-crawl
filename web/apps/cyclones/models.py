"""Cyclone models."""

import itertools
from typing import List

from backend import utils
from django.db import models


class Cyclone(models.Model):
    name = models.CharField(blank=False, null=False, unique=True, max_length=120)
    region = models.CharField(blank=False, null=False, max_length=120)
    img_src = models.URLField(blank=True)
    link_page = models.URLField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "name",
                    "region",
                ],
                name="uniq_name_region",
            )
        ]


class Forecast(models.Model):
    forecast_hr = models.IntegerField(blank=False, default=0)
    lat = models.FloatField(blank=False, null=False)
    lng = models.FloatField(blank=False, null=False)
    intensity = models.IntegerField(blank=False, default=0)
    forecast_time = models.DateTimeField(null=False)
    cyclone = models.ForeignKey(
        Cyclone, related_name="forecasts", null=True, on_delete=models.SET_NULL
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "forecast_time",
                    "lat",
                    "lng",
                    "forecast_hr",
                    "intensity",
                    "cyclone",
                ],
                name="uniq_forecast_time_forecast_hr_cyclone_fkey",
            )
        ]


class HistoricSnapshot(models.Model):
    synoptic_time = models.DateTimeField(null=False)
    lat = models.FloatField(blank=False, null=False)
    lng = models.FloatField(blank=False, null=False)
    intensity = models.IntegerField(blank=False, default=0)
    cyclone = models.ForeignKey(
        Cyclone, related_name="snapshots", null=True, on_delete=models.SET_NULL
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["synoptic_time", "cyclone"],
                name="uniq_synoptic_time_cyclone_fkey",
            )
        ]


def save_db(list_dict: List[dict]):
    """Batch saves cyclone data.

    Args:
        list_dict(list): List of cyclone data dictionary.
    """
    cyclones = {}
    forecast_track = None
    history_track = None
    forecast_time = None
    forecast_list = []
    snapshot_list = []
    all_cyclones = []
    for data in list_dict:
        if (
            "result" in data
            and isinstance(data["result"], dict)
            and (scraped_data := data["result"])
        ):
            cyclone = Cyclone(
                **dict(
                    name=scraped_data["cyclone_name"],
                    region=scraped_data["region"],
                    img_src=scraped_data["img_src"],
                    link_page=scraped_data["link"],
                )
            )
            cyclone_dict = {"cyclone": cyclone}
            if (forecast_track := scraped_data["forecast_track"]) :
                cyclone_dict = {
                    **cyclone_dict,
                    **{
                        "forecasts": forecast_track,
                    },
                    **{"forecast_time": scraped_data["forecast_time"]},
                }
            if (history_track := scraped_data["history_track"]) :
                cyclone_dict = {
                    **cyclone_dict,
                    **{"snapshots": history_track[0]},
                }
            cyclones = {
                **cyclones,
                **{cyclone.name: cyclone_dict},
            }
    existing_cyclones = utils.filter_existing_queryset(Cyclone, cyclones.keys(), "name")
    all_cyclones += [existing_cyclones]
    if (
        new_cyclones_dict := {
            ckey: cyclones[ckey]["cyclone"]
            for ckey in set(cyclones)
            - set(existing_cyclones.values_list("name", flat=True))
        }
    ) :
        new_cyclones = Cyclone.objects.bulk_create(new_cyclones_dict.values())
        all_cyclones += [new_cyclones]
    for each_cyclone in itertools.chain(*all_cyclones):
        if (
            (cyclone_dict := cyclones[each_cyclone.name])
            and cyclone_dict["cyclone"]
            and (cyclone_fkey := {"cyclone": each_cyclone})
        ):
            if (forecasts := cyclone_dict.get("forecasts")) and (
                forecast_time := cyclone_dict.get("forecast_time")
            ):
                forecast_list += [
                    Forecast(
                        **{
                            **forecast_entry,
                            **{"forecast_time": forecast_time},
                            **cyclone_fkey,
                        }
                    )
                    for forecast_entry in forecasts
                ]
            if (snapshots := cyclone_dict.get("snapshots")) :
                snapshot_list += [HistoricSnapshot(**{**snapshots, **cyclone_fkey})]
    if forecast_list:
        # bulk create non duplicate entries.
        non_dup_forecasts = set()
        filtered_lazylists = filter(
            utils.check_unique_constraint,
            utils.filter_non_duplicate_entry(
                forecast_list,
                "forecast_hr",
                "forecast_time",
                "lat",
                "lng",
                "intensity",
                "cyclone__id",
                non_dup=non_dup_forecasts,
            ),
        )
        Forecast.objects.bulk_create(filtered_lazylists)
    if snapshot_list:
        # bulk create non duplicate entries.
        non_dup_snapshots = set()
        filtered_lazylist = filter(
            utils.check_unique_constraint,
            utils.filter_non_duplicate_entry(
                snapshot_list,
                "synoptic_time",
                "cyclone__id",
                non_dup=non_dup_snapshots,
            ),
        )
        HistoricSnapshot.objects.bulk_create(filtered_lazylist)
