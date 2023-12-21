from django.urls import path

from apps.apihealth import views

urlpatterns = [
    path("", view=views.ApiHealthViewSet.as_view({"get": "retrieve"}), name="index"),
]
