"""Tests for cyclone module."""

import datetime as dt

import apps.cyclones.models as models
from apps.cyclones.factory.factory import (
    CycloneFactory,
    ForecastFactory,
    HistoricSnapshotFactory,
    TZINFO,
    fake,
    LAT,
    LNG,
)
from apps.cyclones.models import Cyclone, Forecast, HistoricSnapshot
from django.db.models import Q
from django.test import TestCase

FAKE_DATA = [
    dict(
        result=dict(
            cyclone_name="fake_cyclone",
            region=fake.word(),
            img_src=fake.uri,
            link=fake.uri,
            history_track=[
                dict(
                    synoptic_time=fake.date_time_this_month(
                        tzinfo=TZINFO, before_now=True
                    ),
                    lat=fake.pyfloat(min_value=LAT[0], max_value=LAT[1]),
                    lng=fake.pyfloat(min_value=LNG[0], max_value=LNG[1]),
                    intensity=fake.random_digit(),
                )
                for _ in range(5)
            ],
            forecast_track=[
                dict(
                    forecast_hr=fake.random_digit(),
                    lat=fake.pyfloat(min_value=LAT[0], max_value=LAT[1]),
                    lng=fake.pyfloat(min_value=LNG[0], max_value=LNG[1]),
                    intensity=fake.random_digit(),
                )
                for _ in range(5)
            ],
            forecast_time=fake.date_time_this_month(tzinfo=TZINFO, before_now=True),
        )
    )
]


class CycloneModelTest(TestCase):
    """DB Integration Tests for models."""

    @classmethod
    def setUpTestData(cls):
        cls.cyclone = CycloneFactory()
        cls.forecasts = ForecastFactory.create_batch(
            5, forecast_time=dt.datetime.now(tz=TZINFO), cyclone=cls.cyclone
        )
        cls.snapshots = HistoricSnapshotFactory.create_batch(
            5, synoptic_time=dt.datetime.now(tz=TZINFO), cyclone=cls.cyclone
        )

    def setUp(self):
        self.data = FAKE_DATA
        self.cyclone = CycloneModelTest.cyclone
        self.forecasts = CycloneModelTest.forecasts
        self.snapshots = CycloneModelTest.snapshots

    def testCycloneNoDuplicates(self):
        models.save_db(self.data)
        cyclone_objs = Cyclone.objects.prefetch_related("forecasts", "snapshots").all()
        saved_objs = len(cyclone_objs)
        self.assertEqual(saved_objs, 2, "Got %d saved entries" % saved_objs)
        names = cyclone_objs.values_list("name", flat=True)
        cyclone_name = self.data[0]["result"]["cyclone_name"]
        self.assertTrue(cyclone_name in names)
        second_entry = list(set(names) - set([cyclone_name]))[0]
        self.assertRegexpMatches(
            second_entry, r"^\w+_\d$", "Expected form cyclone_n got %s" % second_entry
        )

    def testSaveDb(self):
        """Test model associated entries are mutually exclusive."""
        models.save_db(self.data)
        cyclone_objs = Cyclone.objects.prefetch_related("forecasts", "snapshots").all()
        self.assertEqual(len(cyclone_objs), 2)
        saved_model = Cyclone.objects.prefetch_related("forecasts", "snapshots").get(
            name=self.data[0]["result"]["cyclone_name"]
        )
        self.assertTrue(saved_model)
        cyclone = Cyclone.objects.get(name=self.cyclone.name)
        forecasts = Forecast.objects.filter(Q(cyclone=cyclone)).values_list(
            "pk", flat=True
        )
        snapshots = HistoricSnapshot.objects.filter(Q(cyclone=cyclone)).values_list(
            "pk", flat=True
        )
        self.assertTrue(len(forecasts))
        self.assertTrue(len(snapshots))
        cyclone_rel_f = Cyclone.objects.prefetch_related("forecasts").filter(
            Q(name=saved_model.name) & Q(forecasts__id__in=forecasts)
        )
        cyclone_rel_s = Cyclone.objects.prefetch_related("snapshots").filter(
            Q(name=saved_model.name) & Q(snapshots__id__in=snapshots)
        )
        self.assertFalse(cyclone_rel_f)
        self.assertFalse(cyclone_rel_s)
