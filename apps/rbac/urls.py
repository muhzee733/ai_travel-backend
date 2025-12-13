from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DashboardConfigView

router = DefaultRouter()

urlpatterns = [
    path("dashboard/config/", DashboardConfigView.as_view(), name="dashboard-config"),
]
