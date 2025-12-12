from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    email = models.EmailField(unique=True)

    class Roles(models.TextChoices):
        ADMIN = "admin", "Admin"
        CUSTOMER = "customer", "Customer"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.CUSTOMER,  # normal user
    )

    @property
    def is_admin_role(self):
        return self.role == self.Roles.ADMIN

    @property
    def is_customer_role(self):
        return self.role == self.Roles.CUSTOMER

    def get_role_slugs(self):
        """
        Convenience accessor for role slugs assigned through RBAC.
        """
        if not hasattr(self, "roles"):
            return []
        return list(self.roles.values_list("slug", flat=True))

    def get_permission_codes(self):
        """
        Compute permission codes from all roles assigned to the user.
        """
        from apps.rbac.models import Permission as RbacPermission

        if getattr(self, "is_superuser", False):
            return set(RbacPermission.objects.values_list("code", flat=True))

        if not hasattr(self, "roles"):
            return set()

        permission_codes = set()
        roles = self.roles.prefetch_related("permissions")
        for role in roles:
            permission_codes.update(role.permissions.values_list("code", flat=True))
        return permission_codes

    def has_perm_code(self, code: str) -> bool:
        return code in self.get_permission_codes()
