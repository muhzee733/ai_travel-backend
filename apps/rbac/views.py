from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
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
    {"key": "dashboard", "label": "Dashboard", "path": "/dashboard", "permission": None, "icon": "Home"},
    {"key": "settings", "label": "Settings", "path": "/settings", "permission": ["settings.view", "settings.manage"], "icon": "Settings"},
    {
        "key": "rbac",
        "label": "RBAC",
        "path": "/rbac",
        "permission": "rbac.manage_roles",
        "icon": "Shield",
        "children": [
            {"key": "roles", "label": "Roles", "path": "/roles", "permission": "rbac.manage_roles", "icon": "ShieldCheck"},
            {"key": "permissions", "label": "Permissions", "path": "/permissions", "permission": "rbac.view_permissions", "icon": "ShieldQuestion"},
            {"key": "users", "label": "Users", "path": "/users", "permission": "rbac.manage_roles", "icon": "Users"},
        ],
    },
    {"key": "reports", "label": "Reports", "path": "/reports", "permission": "reports.view", "icon": "BarChart3"},
    {"key": "hotels", "label": "Hotels", "path": "/hotels", "permission": "hotels.view", "icon": "Building2"},
    {"key": "cars", "label": "Cars", "path": "/cars", "permission": "cars.view", "icon": "Car"},
    {"key": "packages", "label": "Packages", "path": "/packages", "permission": "packages.view", "icon": "Package"},
    {"key": "earning", "label": "Earning", "path": "/earning", "permission": "earning.view", "icon": "Coins"},
    {"key": "airtickets", "label": "AirTickets", "path": "/airtickets", "permission": "airtickets.view", "icon": "Plane"},
    {"key": "visa", "label": "Visa", "path": "/visa", "permission": "visa.view", "icon": "BadgeCheck"},
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
    """
    Filter menu/widget items by permission, preserving children lists when provided.
    """
    filtered = []
    for item in items:
        required = item.get("permission")
        children = item.get("children")

        include_item = False
        if required is None:
            include_item = True
        elif isinstance(required, (list, tuple, set)):
            include_item = any(code in user_permissions for code in required)
        else:
            include_item = required in user_permissions

        filtered_children = None
        if children:
            filtered_children = _filter_items_for_permissions(children, user_permissions)
            if filtered_children:
                include_item = include_item or bool(filtered_children)

        if include_item:
            new_item = dict(item)
            if filtered_children is not None:
                new_item["children"] = filtered_children
            filtered.append(new_item)

    return filtered


class DashboardConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        permission_codes = user.get_permission_codes()
        role_slugs = list(user.roles.values_list("slug", flat=True))

        menu_tree = _filter_items_for_permissions(MENU_REGISTRY, permission_codes)

        widgets = _filter_items_for_permissions(WIDGET_REGISTRY, permission_codes)

        data = {
            "user": {
                "id": str(user.id),
                "username": user.username,
            },
            "roles": role_slugs,
            "permissions": sorted(permission_codes),
            "menu_tree": menu_tree,
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

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {"detail": "Role slug must be unique."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {"detail": "Role slug must be unique."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def partial_update(self, request, *args, **kwargs):
        try:
            return super().partial_update(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {"detail": "Role slug must be unique."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
