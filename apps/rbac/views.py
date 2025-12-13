from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()

WIDGET_REGISTRY = []


MENU_STATIC = [
    {"key": "dashboard", "label": "Dashboard", "path": "/dashboard", "permission": None, "icon": "Home"},
    {"key": "settings", "label": "Settings", "path": "/settings", "permission": None, "icon": "Settings"},
    {"key": "customers", "label": "Customers", "path": "/customers", "permission": None, "icon": "Users"},
]


def _filter_items_for_permissions(items, user_permissions, allow_all=False):
    """
    Filter menu/widget items by permission, preserving children lists when provided.
    """
    filtered = []
    for item in items:
        required = item.get("permission")
        children = item.get("children")

        include_item = False
        if allow_all:
            include_item = True
        elif required is None:
            include_item = True
        elif isinstance(required, (list, tuple, set)):
            include_item = any(code in user_permissions for code in required)
        else:
            include_item = required in user_permissions

        filtered_children = None
        if children:
            filtered_children = _filter_items_for_permissions(children, user_permissions, allow_all)
            if filtered_children:
                include_item = include_item or bool(filtered_children)

        if include_item:
            new_item = dict(item)
            if filtered_children is not None:
                new_item["children"] = filtered_children
            filtered.append(new_item)

    return filtered


def _permission_allows(user_permissions, required):
    if required is None:
        return True
    if isinstance(required, (list, tuple, set)):
        return any(code in user_permissions for code in required)
    return required in user_permissions


class DashboardConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def _build_menu_tree(self):
        return MENU_STATIC

    def get(self, request):
        user = request.user
        permission_codes = set()  # permissions disabled
        allow_all = True
        role_slugs = []

        menu_data = _filter_items_for_permissions(self._build_menu_tree(), permission_codes, allow_all)
        widgets = []

        data = {
            "user": {
                "id": str(user.id),
                "username": user.username,
            },
            "roles": role_slugs,
            "permissions": sorted(permission_codes),
            "menu": menu_data,
            "widgets": widgets,
        }
        return Response(data)


class PermissionViewSet:
    pass


class RoleViewSet:
    pass


class UserRoleViewSet:
    pass


class MePermissionsView(APIView):
  """
  Return the authenticated user's roles and permission codes.
  """
  permission_classes = [IsAuthenticated]

  def get(self, request):
    user = request.user
    roles = list(user.roles.values_list("slug", flat=True))
    permissions = sorted(user.get_permission_codes())
    return Response({"roles": roles, "permissions": permissions})


class PermissionCheckView(APIView):
  """
  Check if the authenticated user has a given permission code.
  """
  permission_classes = [IsAuthenticated]

  def get(self, request):
    code = request.query_params.get("code")
    if not code:
      return Response({"detail": "Missing 'code' query param."}, status=status.HTTP_400_BAD_REQUEST)
    allowed = user_has = request.user.has_perm_code(code)
    return Response({"code": code, "allowed": user_has})
