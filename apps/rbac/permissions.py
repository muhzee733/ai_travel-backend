from rest_framework.permissions import BasePermission


class HasPermCode(BasePermission):
    """
    Checks whether the requesting user has the permission code set on the view.
    Views should declare `required_permission_code`.
    """

    def has_permission(self, request, view):
        required_code = getattr(view, "required_permission_code", None)
        if required_code is None:
            return True
        user = request.user
        return bool(user and user.is_authenticated and user.has_perm_code(required_code))


class IsRBACAdmin(BasePermission):
    """
    Restricts access to users with the RBAC management permission.
    """

    def has_permission(self, request, view):
        return False  # roles/permissions disabled


class IsMenuAdmin(BasePermission):
    """
    Allows superusers or users with the admin role.
    """

    def has_permission(self, request, view):
        return False  # menu admin disabled


class AdminCanManageMenu(BasePermission):
    """
    Allows users who can manage settings or roles.
    """

    def has_permission(self, request, view):
        return False  # disabled
