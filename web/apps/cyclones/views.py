"""Active cyclones in the last one hour."""

from apps.cyclones.models import Cyclone
from apps.cyclones.serializer import (
    CycloneSerializer,
)
import datetime as dt
from django.db.models import Q
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import permission_classes

I = int

@permission_classes((permissions.AllowAny,))
class CycloneViewSet(viewsets.ModelViewSet):
    """Cyclone get only viewset."""

    serializer_class = CycloneSerializer
    http_method_names = ["get", "list"]
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        queryset = Cyclone.objects.prefetch_related("forecasts", "snapshots")
        params = self.request.query_params
        tm_delta = dt.timedelta(
            **dict(
                hours=I(params.get("H", 0)),
                minutes=I(params.get("M", 0)),
                seconds=I(params.get("S", 0)),
                days=I(params.get("d", 0)),
            )
        )
        return queryset.filter(
            Q(forecasts__forecast_time__lte=dt.datetime.now() - tm_delta)
        ).order_by('forecasts__forecast_time').distinct()
