from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Permission, Role, UserRole
from .permissions import IsRBACAdmin
from .serializers import (
    PermissionSerializer,
    RoleCreateUpdateSerializer,
    RoleSerializer,
    UserBasicSerializer,
)

User = get_user_model()

MENU_REGISTRY = [
    {"key": "dashboard", "label": "Dashboard", "path": "/dashboard", "permission": None},
    {"key": "settings", "label": "Settings", "path": "/settings", "permission": ["settings.view", "settings.manage"]},
    {"key": "reports", "label": "Reports", "path": "/reports", "permission": "reports.view"},
    {"key": "hotels", "label": "Hotels", "path": "/hotels", "permission": "hotels.view"},
    {"key": "cars", "label": "Cars", "path": "/cars", "permission": "cars.view"},
    {"key": "packages", "label": "Packages", "path": "/packages", "permission": "packages.view"},
    {"key": "earning", "label": "Earning", "path": "/earning", "permission": "earning.view"},
    {"key": "airtickets", "label": "AirTickets", "path": "/airtickets", "permission": "airtickets.view"},
    {"key": "visa", "label": "Visa", "path": "/visa", "permission": "visa.view"},
]

WIDGET_REGISTRY = [
    {"key": "total_hotels", "title": "Total Hotels", "permission": "hotels.view"},
    {"key": "total_cars", "title": "Total Cars", "permission": "cars.view"},
    {"key": "total_packages", "title": "Total Packages", "permission": "packages.view"},
    {"key": "total_earning", "title": "Total Earning", "permission": "earning.view"},
    {"key": "total_airtickets", "title": "Total AirTickets", "permission": "airtickets.view"},
    {"key": "total_visa", "title": "Total Visa", "permission": "visa.view"},
    {"key": "reports_summary", "title": "Reports Summary", "permission": "reports.view"},
    {"key": "settings_status", "title": "Settings Status", "permission": ["settings.view", "settings.manage"]},
]


def _filter_items_for_permissions(items, user_permissions):
    filtered = []
    for item in items:
        required = item.get("permission")
        if required is None:
            filtered.append(item)
            continue
        if isinstance(required, (list, tuple, set)):
            if any(code in user_permissions for code in required):
                filtered.append(item)
        elif required in user_permissions:
            filtered.append(item)
    return filtered


class DashboardConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        permission_codes = user.get_permission_codes()
        role_slugs = list(user.roles.values_list("slug", flat=True))

        menu = _filter_items_for_permissions(MENU_REGISTRY, permission_codes)
        widgets = _filter_items_for_permissions(WIDGET_REGISTRY, permission_codes)

        data = {
            "user": {
                "id": str(user.id),
                "username": user.username,
            },
            "roles": role_slugs,
            "permissions": sorted(permission_codes),
            "menu": menu,
            "widgets": widgets,
        }
        return Response(data)


class PermissionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Permission.objects.all().order_by("module", "action")
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsRBACAdmin]


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().prefetch_related("permissions")
    permission_classes = [IsAuthenticated, IsRBACAdmin]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return RoleCreateUpdateSerializer
        return RoleSerializer

    @action(detail=True, methods=["put"], url_path="permissions")
    def set_permissions(self, request, id=None):
        role = self.get_object()
        permissions = request.data.get("permissions", [])
        if not isinstance(permissions, list):
            return Response(
                {"detail": "permissions must be a list of permission codes."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        permission_qs = Permission.objects.filter(code__in=permissions)
        found_codes = set(permission_qs.values_list("code", flat=True))
        missing = sorted(set(permissions) - found_codes)
        if missing:
            return Response(
                {"detail": f"Permission codes not found: {', '.join(missing)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            role.permissions.set(permission_qs)

        serializer = RoleSerializer(role)
        return Response(serializer.data)


class UserRoleViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UserBasicSerializer
    permission_classes = [IsAuthenticated, IsRBACAdmin]

    def get_queryset(self):
        queryset = User.objects.all().order_by("email")
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        return queryset

    @action(detail=True, methods=["put"], url_path="roles")
    def set_roles(self, request, pk=None):
        user = self.get_object()
        roles = request.data.get("roles", [])
        if not isinstance(roles, list):
            return Response(
                {"detail": "roles must be a list of role slugs."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        role_qs = Role.objects.filter(slug__in=roles)
        found_slugs = set(role_qs.values_list("slug", flat=True))
        missing = sorted(set(roles) - found_slugs)
        if missing:
            return Response(
                {"detail": f"Role slugs not found: {', '.join(missing)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            UserRole.objects.filter(user=user).delete()
            for role in role_qs:
                UserRole.objects.create(
                    user=user,
                    role=role,
                    assigned_by=request.user,
                )

        serializer = UserBasicSerializer(user)
        return Response(serializer.data)
