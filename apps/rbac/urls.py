from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DashboardConfigView, PermissionViewSet, RoleViewSet, UserRoleViewSet

router = DefaultRouter()
router.register(r"permissions", PermissionViewSet, basename="rbac-permissions")
router.register(r"roles", RoleViewSet, basename="rbac-roles")
router.register(r"users", UserRoleViewSet, basename="rbac-users")

urlpatterns = [
    path("dashboard/config/", DashboardConfigView.as_view(), name="dashboard-config"),
    path("rbac/", include(router.urls)),
]
