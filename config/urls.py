from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("api/auth/", include("apps.accounts.urls")),
    path("api/", include("apps.accounts.profile_urls")),
    path("api/", include("apps.rbac.urls")),
]
