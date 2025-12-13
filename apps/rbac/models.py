from django.conf import settings
from django.db import models

from apps.common.models import SoftDeleteModel

class PageRegistry(SoftDeleteModel):
    class Types(models.TextChoices):
        SYSTEM = "SYSTEM", "System"
        CMS = "CMS", "CMS"
        CUSTOM_LINK = "CUSTOM_LINK", "Custom Link"

    key = models.CharField(max_length=150, unique=True)
    title = models.CharField(max_length=200)
    path = models.CharField(max_length=255)
    default_icon = models.CharField(max_length=100)
    permission = models.JSONField(null=True, blank=True)
    type = models.CharField(max_length=20, choices=Types.choices, default=Types.SYSTEM)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.key


class Menu(SoftDeleteModel):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ("location",)

    def __str__(self):
        return self.location

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


class MenuItem(SoftDeleteModel):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="items")
    page_registry = models.ForeignKey(
        PageRegistry, on_delete=models.SET_NULL, null=True, blank=True, related_name="menu_items"
    )
    custom_label = models.CharField(max_length=200, blank=True, null=True)
    custom_path = models.CharField(max_length=255, blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    permission = models.JSONField(null=True, blank=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    sort_order = models.PositiveIntegerField(default=1, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ("sort_order", "id")

    def __str__(self):
        base = self.custom_label or (self.page_registry.title if self.page_registry else "item")
        return f"{base} ({self.menu.location})"
