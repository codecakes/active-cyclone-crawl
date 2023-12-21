from django.contrib import admin
from apps.cyclones.models import Cyclone, Forecast, HistoricSnapshot


@admin.register(Cyclone, Forecast, HistoricSnapshot)
class AdminPermissionsMixin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False


# admin.site.register((Cyclone, HistoricSnapshot, Forecast))
