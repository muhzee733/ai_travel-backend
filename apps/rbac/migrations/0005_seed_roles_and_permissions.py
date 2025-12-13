from django.conf import settings
from django.db import migrations


MODULE_PERMISSIONS = {
    "dashboard": ["view"],
    "settings": ["view", "create", "update", "delete", "report", "manage"],
    "reports": ["view", "create", "update", "delete", "report"],
    "hotels": ["view", "create", "update", "delete", "report"],
    "cars": ["view", "create", "update", "delete", "report"],
    "packages": ["view", "create", "update", "delete", "report"],
    "earning": ["view", "create", "update", "delete", "report"],
    "airtickets": ["view", "create", "update", "delete", "report"],
    "visa": ["view", "create", "update", "delete", "report"],
}

RBAC_EXTRA_CODES = [
    "rbac.manage_roles",
    "rbac.manage_users",
    "rbac.view_permissions",
]

CUSTOMER_PERMISSION_CODES = [
    "dashboard.view",
    "settings.view",
    "hotels.view",
    "cars.view",
    "packages.view",
    "airtickets.view",
    "visa.view",
    "earning.view",
    "reports.view",
]


def seed_permissions_and_roles(apps, schema_editor):
    Permission = apps.get_model("rbac", "Permission")
    Role = apps.get_model("rbac", "Role")
    UserRole = apps.get_model("rbac", "UserRole")
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))

    # Seed permissions
    for module, actions in MODULE_PERMISSIONS.items():
        for action in actions:
            code = f"{module}.{action}"
            Permission.objects.update_or_create(
                code=code,
                defaults={
                    "module": module,
                    "action": action,
                    "description": f"Allows {action} on {module}.",
                },
            )

    for code in RBAC_EXTRA_CODES:
        module, action = code.split(".", 1)
        Permission.objects.update_or_create(
            code=code,
            defaults={
                "module": module,
                "action": action,
                "description": f"Allows {action} operations.",
            },
        )

    admin_role, _ = Role.objects.get_or_create(
        slug="admin",
        defaults={"name": "Admin", "description": "Platform administrator"},
    )
    customer_role, _ = Role.objects.get_or_create(
        slug="customer",
        defaults={"name": "Customer", "description": "Default customer role"},
    )

    all_permissions = Permission.objects.all()
    admin_role.permissions.set(all_permissions)

    customer_permissions = Permission.objects.filter(code__in=CUSTOMER_PERMISSION_CODES)
    customer_role.permissions.set(customer_permissions)

    # Assign roles to users
    for user in User.objects.filter(is_superuser=True):
        UserRole.objects.get_or_create(user=user, role=admin_role, defaults={"assigned_by": None})
        # keep single source of truth for role field
        if hasattr(user, "role") and user.role != "admin":
            user.role = "admin"
            user.save(update_fields=["role"])

    for user in User.objects.filter(is_superuser=False):
        UserRole.objects.get_or_create(user=user, role=customer_role, defaults={"assigned_by": None})
        if hasattr(user, "role") and user.role != "customer":
            user.role = "customer"
            user.save(update_fields=["role"])


def noop(apps, schema_editor):
    # No-op reverse; we don't want to delete permissions or roles on rollback
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("rbac", "0004_seed_menus"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(seed_permissions_and_roles, reverse_code=noop),
    ]
