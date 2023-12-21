"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

router = routers.DefaultRouter()

SCHEMA_META = dict(
    title="Cyclones: OpenAPI Spec",
    description="OpenAPI Spec Schema",
    version="0.0.1",
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("openapi-schema/", get_schema_view(**SCHEMA_META), name="openapi-schema"),
    path("login-rest-router/", include(router.urls)),
    path("apihealth/", include("apps.apihealth.urls")),
    path("cyclones/", include("apps.cyclones.urls")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
