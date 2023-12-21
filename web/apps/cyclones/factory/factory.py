"""Fake factory generators for models."""

import factory
from faker import Factory
from dateutil.tz import gettz
from apps.cyclones.models import Cyclone, Forecast, HistoricSnapshot

TZINFO = gettz("America/Chicago")
LAT = (-90, 90)
LNG = (-180, 180)

fake = Factory.create()


class CycloneFactory(factory.DjangoModelFactory):
    class Meta:
        model = Cyclone
        django_get_or_create = (
            "name",
            "region",
            "img_src",
            "link_page",
        )

    name = factory.Sequence(lambda n: f'cyclone_{n}')
    region = fake.word()
    img_src = fake.uri()
    link_page = fake.uri()


class ForecastFactory(factory.DjangoModelFactory):
    class Meta:
        model = Forecast
        django_get_or_create = (
            "forecast_hr",
            "lat",
            "lng",
            "intensity",
            "forecast_time",
        )

    forecast_hr = fake.random_digit()
    lat = fake.pyfloat(min_value=LAT[0], max_value=LAT[1])
    lng = fake.pyfloat(min_value=LNG[0], max_value=LNG[1])
    intensity = fake.random_digit()
    forecast_time = fake.date_time_this_month(tzinfo=TZINFO, before_now=True)
    cyclone = factory.SubFactory(CycloneFactory)


class HistoricSnapshotFactory(factory.DjangoModelFactory):
    class Meta:
        model = HistoricSnapshot
        django_get_or_create = (
            "synoptic_time",
            "lat",
            "lng",
            "intensity",
        )

    synoptic_time = fake.date_time_this_month(
        tzinfo=TZINFO, before_now=True
    )
    lat = fake.pyfloat(min_value=LAT[0], max_value=LAT[1])
    lng = fake.pyfloat(min_value=LNG[0], max_value=LNG[1])
    intensity = fake.random_digit()
    cyclone = factory.SubFactory(CycloneFactory)
