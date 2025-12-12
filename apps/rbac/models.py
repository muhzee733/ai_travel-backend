from django.conf import settings
from django.db import models

from apps.common.models import SoftDeleteModel


class Permission(SoftDeleteModel):
    code = models.CharField(max_length=150, unique=True)
    module = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ("module", "action")

    def __str__(self):
        return self.code


class Role(SoftDeleteModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(
        Permission,
        through="RolePermission",
        related_name="roles",
        blank=True,
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="UserRole",
        related_name="roles",
        blank=True,
        through_fields=("role", "user"),
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.slug


class UserRole(SoftDeleteModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_users",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_roles",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "role")
        ordering = ("-assigned_at",)

    def __str__(self):
        return f"{self.user} -> {self.role}"


class RolePermission(SoftDeleteModel):
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name="permission_roles",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("role", "permission")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.role.slug}:{self.permission.code}"
