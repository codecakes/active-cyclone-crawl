"""Serializer for views."""

from apps.cyclones.models import Cyclone, Forecast, HistoricSnapshot
from rest_framework import serializers


class ForecastSerializer(serializers.ModelSerializer):
    """Serializer for forecast model."""

    class Meta:
        model = Forecast
        fields = "__all__"


class HistoricSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for historic snapshot model."""

    class Meta:
        model = HistoricSnapshot
        fields = "__all__"


class CycloneSerializer(serializers.ModelSerializer):
    """Serializer for cyclone model."""

    forecasts = ForecastSerializer(many=True, read_only=True, required=False)
    snapshots = HistoricSnapshotSerializer(
        many=True, read_only=True, required=False
    )

    class Meta:
        model = Cyclone
        fields = "__all__"
