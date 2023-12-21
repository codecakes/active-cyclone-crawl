from apps.cyclones import views
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register("", views.CycloneViewSet, basename="cyclones")

urlpatterns = [
    path(
        "",
        views.CycloneViewSet.as_view(
            {
                "get": "list",
            }
        ),
        name="cyclones",
    ),
] + router.urls
